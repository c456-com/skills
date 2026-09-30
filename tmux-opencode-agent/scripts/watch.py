#!/usr/bin/env python3
"""OpenCode 监控探针：启动时回看 session 投影，再旁听 SSE 等待后续终态。

用法：
    watch.py <session_id> <timeout_seconds> [--tmux-session <name>]

设计要点（都是实测踩出来的）：
  · SSE 是易失流，断开后不能回放；启动回看改读 OpenCode session 真源：
    ``/api/session/{id}/message?limit=1&order=desc`` 的最新 durable projection。
  · 仅当 session 当前不在 ``/api/session/active``、inbox 为空，且最新消息是
    ``idle`` 时才报 BACKFILL-DONE。``info.outcome`` 会保留上一轮，绝不单独拿它判当前轮。
  · 真源不可读/结构未知时明确打印「无法回看」，随后保持原 SSE 等待逻辑，绝不猜。
  · 终态判据 = 本 session 后续 SSE 出现过 execution.succeeded / execution.interrupted / execution.failed 任一。
  · ``session.step.failed`` / ``session.tool.failed`` **不是轮次结束**，只作提示。
  · 权限面板：``permission.asked`` 出现即打印 PERMISSION-BLOCKED 并退出，保留 CTO 18:32 行为。
  · 屏幕副路：独立每 15 秒 capture-pane 一次，识别 interrupted / 权限面板 /
    无 TUI 等屏面信号；只打印不退出，15 秒是低频防丢信号而非秒级实时反馈。
  · 必须由 Hermes 托管（terminal(background=true, notify_on_complete=true)）。

  ⚠️ 2026-09-25 操作者当面纠正的设计缺陷（已修）：**监控寿命必须绑「小弟窗口/会话存在」，
  不能绑「一轮任务」**。原实现有三处同源缺陷：
    ① SSE 终态 ``sys.exit(0)`` ⇒ 两轮任务之间无人看（实测这段空窗里发生过
       「多选面板预选项被当默认执行、13 张现行截图被误移」）；
    ② ``backfill`` 命中历史终态也 ``sys.exit(0)`` ⇒ 刚挂上就退；
    ③ SSE 断流 / ``--max-time`` 到点后直接结束 ⇒ 一次挂载只覆盖一个时间片。
  现实现：终态只打印 STAGE-DONE 后**继续盯**；SSE 结束自动重连并回看；
  退出只发生在「小弟窗口/会话真的没了」或「显式 SIGTERM」。
  """
import base64
import json
import os
import signal
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from screen_watch import capture_pane, run_screen_loop

if len(sys.argv) < 2:
    sys.exit("用法：watch.py <session_id> [timeout_seconds] [--tmux-session <name>]")

SESSION_ID = sys.argv[1]
TIMEOUT = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 900
TMUX = None
if "--tmux-session" in sys.argv:
    TMUX = sys.argv[sys.argv.index("--tmux-session") + 1]

TERMINAL_EVENTS = {
    "session.execution.succeeded",
    "session.execution.interrupted",
    "session.execution.failed",
}
NON_TERMINAL_ALERTS = {
    "session.tool.failed",
    "session.step.failed",
}


def service_url():
    result = subprocess.run(
        ["opencode", "service", "status"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        raise RuntimeError(f"opencode service status rc={result.returncode}: {result.stderr.strip()[:200]}")
    return result.stdout.strip().replace(" ", "")


def password():
    path = os.path.expanduser("~/.config/opencode/service.json")
    with open(path) as stream:
        return json.load(stream)["password"]


def api_get(url: str, path: str, timeout: float = 10):
    request = Request(url + path, headers={"Accept": "application/json"})
    token = base64.b64encode(f"opencode:{PASSWORD}".encode()).decode()
    request.add_header("Authorization", f"Basic {token}")
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def child_sessions_still_active(url: str):
    """本 session 派出的子会话是否还有 active 的。

    实测坑（2026-09-25 22:5x，两次假终态）：主轮 ``session.execution.succeeded``
    只表示「主 agent 那一段执行完成」，它派出的子会话可能还在跑
    （屏上 ``↓ N subagents``、主 session 已不在 ``/api/session/active``）。
    判主轮真结束必须额外确认：``parentID == SESSION_ID`` 的子会话全部不再 active。
    """
    active = api_get(url, "/api/session/active").get("data")
    if not isinstance(active, (list, dict)):
        return None, "active 真源结构未知"
    # 真源实测（2026-09-25）：data 可以是 {sessionID: {"type": ...}} 字典，
    # 也可以是 session 对象数组；两种都要能取到 session id。
    if isinstance(active, dict):
        ids = [k for k in active.keys() if isinstance(k, str)]
    else:
        ids = [
            item.get("id") for item in active
            if isinstance(item, dict) and item.get("id")
        ]
    children = []
    for sid in ids:
        if sid == SESSION_ID:
            continue
        try:
            detail = api_get(url, f"/api/session/{quote(sid, safe='')}").get("data") or {}
        except (HTTPError, URLError, TimeoutError, OSError, ValueError):
            continue
        if detail.get("parentID") == SESSION_ID:
            children.append((sid, (detail.get("title") or "")[:40]))
    return children, "active+parentID 交叉核"


def backfill(url: str):
    """可靠回看当前轮终态；不可判定时返回 None，不作时间猜测。"""
    encoded = quote(SESSION_ID, safe="")
    active_payload = api_get(url, "/api/session/active")
    active = active_payload.get("data")
    if not isinstance(active, dict):
        return None, "active 真源结构未知"
    if SESSION_ID in active:
        return None, "session 当前仍 active"

    inbox_payload = api_get(url, f"/api/session/{encoded}/inbox")
    inbox = inbox_payload.get("data")
    if not isinstance(inbox, list):
        return None, "inbox 真源结构未知"
    if inbox:
        return None, "session inbox 仍有待处理输入"

    messages_payload = api_get(
        url,
        f"/api/session/{encoded}/message?limit=1&order=desc",
    )
    messages = messages_payload.get("data")
    if not isinstance(messages, list):
        return None, "message 真源结构未知"
    if not messages:
        return None, "session 尚无 durable message 投影"

    latest = messages[0]
    if not isinstance(latest, dict) or latest.get("type") != "idle":
        return None, "最新 durable message 不是 idle 终态"
    outcome = latest.get("outcome")
    if outcome not in ("succeeded", "failed", "interrupted"):
        return None, f"idle outcome 未知：{outcome!r}"
    try:
        children, _ = child_sessions_still_active(url)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        return None, f"无法核子会话：{exc}"
    if children is None:
        return None, "子会话真源结构未知"
    if children:
        listing = "、".join(f"{sid}({title})" for sid, title in children)
        return None, f"本 session 仍有子会话 active：{listing}"
    ended_at = (latest.get("time") or {}).get("created")
    return {
        "event": f"session.execution.{outcome}",
        "outcome": outcome,
        "ended_at": ended_at,
        "message_id": latest.get("id"),
    }, "session durable idle projection（已确认无 active 子会话）"


def pane_text():
    """兼容旧调用方；屏幕副路本身在独立线程中每 15 秒轮询。"""
    if not TMUX:
        return ""
    text, _ = capture_pane(TMUX)
    return text


def on_signal(signum, frame):
    raise SystemExit(0)


signal.signal(signal.SIGTERM, on_signal)

try:
    url = service_url()
    PASSWORD = password()
except Exception as exc:
    sys.exit(f"拿不到 OpenCode service 连接信息：{exc}")

if not url.startswith("http"):
    sys.exit(f"拿不到 service 地址：{url!r}（opencode service status 输出异常）")

print(f"PROBE-START session={SESSION_ID} url={url} 超时片长={TIMEOUT}s（到点自动重连，不退出）", flush=True)

# ---- 启动闸：锚点必须真实存在，且目录必须匹配 --------------------------------
# 2026-09-26 实测踩坑：我给三个探针喂了「抄来的 / 不存在的 session_id」，
# 探针照样打印 PROBE-START 并一路报「在盯」，实际在旁听一个空 ID —— 盯的是空气，
# 一盯 5~8 小时。`ps` 只能证明进程活，证明不了锚点对。
# ⇒ 启动即核：id 必须在服务端存在；给了 --expect-dir 就必须目录匹配（防同项目多 worktree 串台）。
EXPECT_DIR = None
if "--expect-dir" in sys.argv:
    EXPECT_DIR = sys.argv[sys.argv.index("--expect-dir") + 1]

def verify_anchor(url: str):
    """返回 (ok, 说明)。不通过就让探针退出——宁可不盯，不可盯错。"""
    try:
        listing = api_get(url, "/api/session", timeout=15).get("data", [])
    except Exception as exc:  # noqa: BLE001
        return False, f"拉会话清单失败：{exc}"
    hit = next((s for s in listing if s.get("id") == SESSION_ID), None)
    if hit is None:
        sample = "、".join(s.get("id", "?")[:16] for s in listing[-3:])
        return False, (
            f"锚点 session {SESSION_ID} 在服务端不存在（现有 {len(listing)} 个，最近：{sample}）"
            " —— 多半是从记录里抄错了 id。先用 /api/session 取真 id 再挂。"
        )
    directory = (hit.get("location") or {}).get("directory")
    if EXPECT_DIR and (directory or "") != EXPECT_DIR:
        return False, (
            f"锚点目录不符：期望 {EXPECT_DIR!r}，实际 {directory!r}"
            " —— 同项目多 worktree 时会串台。"
        )
    return True, f"{directory!r}"

_anchor_ok, _anchor_why = verify_anchor(url)
if not _anchor_ok:
    sys.exit(f"ANCHOR-FAIL session={SESSION_ID} {_anchor_why}")
print(f"ANCHOR-OK session={SESSION_ID} {_anchor_why}", flush=True)

STAGE_DEADLINE = time.time() + float(os.environ.get("WATCH_MAX_SECONDS", "86400"))
# 屏幕副路：独立低频只打印，不参与退出判断。
screen_stop = threading.Event()
screen_thread = None
if TMUX:
    screen_thread = threading.Thread(
        target=run_screen_loop,
        args=(TMUX, screen_stop),
        name="opencode-screen-watch",
        daemon=True,
    )
    screen_thread.start()

# 探针寿命绑「小弟存在」，不绑「一轮任务」：终态只报，SSE 断流自动重连。
# ---- 已报过的回看终态去重（跨重连记忆）----------------------------------------
# 2026-09-26 实测踩坑：探针锚在一个 8 小时前已收工的 session 上，每 3600s 重连就把
# 同一条 BACKFILL-DONE 重放一次（日志里连转 6 次同一个 end_ts），真信号被噪音盖住，
# 我据此误以为「在盯」。⇒ 同一个 message_id 的回看终态只报一次，之后静默重试。
REPORTED_BACKFILL: set[str] = set()
# SSE 终态去重也必须跨重连：seen_terminal 原先在 while 循环内重置，
# 每次 SSE 断流重连都把同一条 STAGE-DONE 重报一遍（既刷屏、又白烧 watch_patterns 投递额度）。
# 事件 key 含 id/messageID/ts，跨重连天然唯一 ⇒ 提到循环外即可。
seen_terminal: set[tuple] = set()

while True:
    try:
        backfill_result, backfill_reason = backfill(url)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        backfill_result = None
        backfill_reason = f"无法回看：{exc}"
    if backfill_result is not None:
        _mid = backfill_result["message_id"] or "?"
        if _mid in REPORTED_BACKFILL:
            # 已报过 ⇒ 静默（只说明「没新东西」），不重放旧终态刷屏
            pass
        else:
            REPORTED_BACKFILL.add(_mid)
            print(
                f"BACKFILL-DONE session={SESSION_ID} event={backfill_result['event']} "
                f"outcome={backfill_result['outcome']} end_ts={backfill_result['ended_at']} "
                f"message_id={backfill_result['message_id']} source=session-message-idle"
                f"（回看：上一轮已收工）→ 继续盯，等下一轮",
                flush=True,
            )
    else:
        print(f"BACKFILL-UNAVAILABLE session={SESSION_ID} {backfill_reason}；继续监听新 SSE", flush=True)

    proc = subprocess.Popen(
        ["curl", "-sS", "-N", "-u", f"opencode:{PASSWORD}", "--max-time", str(TIMEOUT),
         f"{url}/api/event"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1,
    )
    started_at = None
    # ⛔ seen_terminal 已提到循环外（跨重连去重），此处不得重新赋值
    asked_permissions = {}
    deadline = time.time() + TIMEOUT

    try:
        for line in proc.stdout:
            line = line.strip()
            now = time.time()
            if now > STAGE_DEADLINE:
                print(f"WATCH-EXIT session={SESSION_ID} reason=WATCH_MAX_SECONDS 到点（显式上限）", flush=True)
                sys.exit(0)
            if now > deadline:
                print(f"WATCH-TIMEOUT session={SESSION_ID} 单片到点 → 续挂等下一轮", flush=True)
                break
            if not line.startswith("data: "):
                continue
            try:
                event = json.loads(line[6:])
            except Exception:
                continue

            data = event.get("data") or {}
            if data.get("sessionID") != SESSION_ID:
                continue

            etype = event.get("type", "")
            ts = (event.get("created") or int(now * 1000)) / 1000.0

            if etype == "session.execution.started":
                started_at = ts
                print(f"TURN-START ts={ts:.3f}", flush=True)

            elif etype in TERMINAL_EVENTS:
                # ⛔ 主轮 succeeded ≠ 整轮交工：派出的子会话可能还在跑。
                try:
                    children, why = child_sessions_still_active(url)
                except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
                    children, why = None, f"核子会话失败：{exc}"
                if children:
                    listing = "、".join(f"{sid}({title})" for sid, title in children)
                    print(
                        f"TERMINAL-PENDING event={etype} 仍有 {len(children)} 个子会话 active："
                        f"{listing}（{why}）→ 不判结束，继续盯",
                        flush=True,
                    )
                    continue
                if children is None:
                    print(
                        f"TERMINAL-UNVERIFIED event={etype} 无法核子会话（{why}）→ 不判结束，继续盯",
                        flush=True,
                    )
                    continue
                key = (etype, data.get("id") or data.get("messageID") or ts)
                if key in seen_terminal:
                    continue
                seen_terminal.add(key)
                duration = f"{ts - started_at:.2f}s" if started_at else "?"
                print(
                    f"STAGE-DONE session={SESSION_ID} event={etype} "
                    f"start_ts={started_at if started_at else '?'} "
                    f"end_ts={ts:.3f} duration={duration}（本轮交工，继续盯下一轮）",
                    flush=True,
                )
                # ⛔ 2026-09-25 修正：这里曾经 sys.exit(0)——探针寿命绑错了对象。
                started_at = None
                continue

            elif etype in NON_TERMINAL_ALERTS:
                print(
                    f"TOOL-FAILED event={etype} "
                    f"tool={data.get('tool') or data.get('stepID') or '?'}（非终态，继续盯）",
                    flush=True,
                )

            elif etype == "permission.asked":
                rid = data.get("id")
                if rid in asked_permissions:
                    print(f"PERMISSION-REASKED id={rid}（同一请求重复上报）", flush=True)
                asked_permissions[rid] = ts
                print(
                    f"PERMISSION-ASKED id={rid} action={data.get('action')} "
                    f"resources={data.get('resources')} source={data.get('source')}",
                    flush=True,
                )
                print(
                    f"PERMISSION-BLOCKED session={SESSION_ID} 需要 CTO 处置权限面板"
                    f"（处置后我继续盯，不退出）",
                    flush=True,
                )
                continue

            elif etype == "permission.replied":
                asked_permissions.pop(data.get("requestID"), None)
                print(f"PERMISSION-REPLIED reply={data.get('reply')}", flush=True)

        rc = proc.poll()
        print(f"CURL-END rc={rc}（28=--max-time 到点，预期非故障）→ 续挂", flush=True)

        if asked_permissions and not seen_terminal:
            print(f"QUESTION-PANEL session={SESSION_ID} 待批={list(asked_permissions)}", flush=True)

        # 退出条件只有一个：小弟真被解散了。
        if TMUX:
            alive = subprocess.run(["tmux", "has-session", "-t", TMUX], capture_output=True).returncode == 0
            if not alive:
                print(f"WATCH-EXIT session={SESSION_ID} reason=tmux 会话 {TMUX} 不存在（小弟被解散）", flush=True)
                sys.exit(0)
        else:
            try:
                detail = api_get(url, f"/api/session/{quote(SESSION_ID, safe='')}").get("data") or {}
            except (HTTPError, URLError, TimeoutError, OSError, ValueError):
                detail = {}
            if detail and detail.get("archived") is True:
                print(f"WATCH-EXIT session={SESSION_ID} reason=会话已归档（小弟被解散）", flush=True)
                sys.exit(0)
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    time.sleep(1)

# 探针整体收尾（正常结束 / 被 SIGTERM）。
screen_stop.set()
if screen_thread is not None:
    screen_thread.join(timeout=1)
