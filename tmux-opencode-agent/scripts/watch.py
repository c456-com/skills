#!/usr/bin/env python3
"""OpenCode 监控探针：旁听 SSE，把「一轮结束」转成进程完成通知唤醒 Hermes。

用法（参数顺序任意）：
    watch.py <session_id> [timeout_seconds=900] [--tmux-session <name>]

设计要点（都是实测踩出来的）：
  · 终态判据 = 本 session 出现过 execution.succeeded / execution.interrupted /
    session.step.failed / session.tool.failed 任一。只等 succeeded 会漏掉被打断和失败的轮次。
  · 按 data.sessionID 分流：一条 SSE 流里混着所有 session 的事件。
  · 绝不用「最后一行是不是 succeeded」——事件到达顺序不固定。
  · 权限面板卡死：permission.asked 出现后长时间无 permission.replied ⇒ 报 QUESTION-PANEL。
  · 屏幕补位（需 --tmux-session）：SSE 不补发连接前的事件，REST 查不到待批请求，
    探针晚于面板启动（含循环重挂）时 SSE 永远看不到这个面板；
    此时屏幕连续两次可见面板 ⇒ 报 QUESTION-PANEL source=screen 并退出。
    屏幕检查按时钟调度（读线程收 SSE、主循环定时醒），SSE 完全静默时照样工作。
  · SSE 提前断开：打印 SSE-LOST，按 1/2/4/8s 退避重连（每次重取 service 地址），期间屏幕补位不停。
  · 必须由 Hermes 托管（terminal(background=true, notify_on_complete=true)），
    用 subprocess.Popen 起的进程 Hermes 不认，退出时不通知。
  · 正常退出码可能是 curl 的 28（--max-time 到点），不是故障。
"""
import sys
import os
import json
import time
import queue
import signal
import argparse
import threading
import subprocess


def positive_int(s):
    v = int(s)
    if v <= 0:
        raise argparse.ArgumentTypeError(f"必须是正整数秒数：{s!r}")
    return v


parser = argparse.ArgumentParser(description="OpenCode 单会话轮次结束探针（SSE 为主，屏幕补位）")
parser.add_argument("session_id", help="OpenCode session ID（ses_...）")
parser.add_argument("timeout", nargs="?", type=positive_int, default=900,
                    help="超时秒数，缺省 900")
parser.add_argument("--tmux-session", dest="tmux", default=None,
                    help="承载该 session TUI 的 tmux 会话名；给了才启用屏幕补位")
opts = parser.parse_intermixed_args()
SESSION_ID = opts.session_id
TIMEOUT = opts.timeout
TMUX = opts.tmux
SCREEN_CHECK_INTERVAL = 5   # 秒；连续两次可见才算，避开「刚弹出、SSE 事件还在路上」的竞态
LOOP_TICK = 0.5             # 秒；主循环最长阻塞时间，决定时钟类检查（屏幕、deadline）的精度

TERMINAL_EVENTS = {
    "session.execution.succeeded",
    "session.execution.interrupted",
    "session.step.failed",
    "session.tool.failed",
}


def service_url():
    out = subprocess.run(["opencode", "service", "status"],
                         capture_output=True, text=True).stdout
    return out.strip().replace(" ", "")


def password():
    import os.path
    p = os.path.expanduser("~/.config/opencode/service.json")
    with open(p) as f:
        return json.load(f)["password"]


def pane_text():
    # 只取可见屏，不取滚动历史：历史里残留的旧面板/文档文字会误判
    if not TMUX:
        return ""
    try:
        return subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{TMUX}:0"],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        return ""


def panel_on_screen():
    text = pane_text()
    return "Permission required" in text and "Allow once" in text and "Reject" in text


stop_requested = False


def on_signal(signum, frame):
    # 只置标志、由主循环在安全点退出：在 handler 里直接 raise，连续收到两次信号时
    # （如 GNU timeout 先发子进程再发进程组）会打断 queue.get 内部的锁恢复，
    # 崩成 RuntimeError: release unlocked lock。退出时 finally 仍会回收 curl。
    global stop_requested
    stop_requested = True


signal.signal(signal.SIGTERM, on_signal)
signal.signal(signal.SIGINT, on_signal)

url = service_url()
pw = password()
if not url.startswith("http"):
    sys.exit(f"拿不到 service 地址：{url!r}（opencode service status 输出异常）")

print(f"PROBE-START session={SESSION_ID} url={url} timeout={TIMEOUT}s tmux={TMUX or '-'}", flush=True)


def connect(url, pw, max_time):
    """起一条 curl SSE 连接及其读线程，返回 (proc, queue)；队列里的 None 表示这条连接已结束。

    读 SSE 放在独立线程：直接 for line in proc.stdout 会在 SSE 静默时阻塞，
    时钟类检查（屏幕补位、deadline）就一次都跑不到。每条连接独占一个队列，旧连接的 None 不会串到新连接。
    """
    p = subprocess.Popen(
        ["curl", "-s", "-N", "-u", f"opencode:{pw}", "--max-time", str(max_time),
         f"{url}/api/event"],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, bufsize=1,
    )
    q = queue.Queue()

    def reader():
        try:
            for raw in p.stdout:
                q.put(raw)
        finally:
            q.put(None)

    threading.Thread(target=reader, daemon=True).start()
    return p, q


def reap(p):
    try:
        return p.wait(timeout=3)
    except Exception:
        p.kill()
        return p.wait()


proc, lines = connect(url, pw, TIMEOUT)

started_at = None          # 本 session 的 execution.started 时间
seen_terminal = set()      # 已报告过的终态（id 或 key）
asked_permissions = {}     # requestID -> 时间戳
deadline = time.time() + TIMEOUT
last_any_event = time.time()
last_screen_check = 0.0
screen_panel_hits = 0
conn_lines = 0             # 当前连接已收到的非空行数；>0 说明连通过，断开后退避从头算
reconnect_at = None        # SSE 断开后的下次重连时刻；None 表示连接在线
reconnect_delay = 1
reconnect_attempt = 0

try:
    while True:
        if stop_requested:
            sys.exit(0)
        now = time.time()
        if now > deadline:
            print(f"WATCH-TIMEOUT conv={SESSION_ID}", flush=True)
            break

        # SSE 已知有待批请求时由 SSE 负责；只在 SSE 无记录时用屏幕补位
        if asked_permissions:
            screen_panel_hits = 0
        elif TMUX and now - last_screen_check >= SCREEN_CHECK_INTERVAL:
            visible = panel_on_screen()
            # 以截屏完成时刻计间隔：两次真实观察之间才保证 ≥ SCREEN_CHECK_INTERVAL
            last_screen_check = time.time()
            if visible:
                screen_panel_hits += 1
                if screen_panel_hits >= 2:
                    print(
                        f"QUESTION-PANEL session={SESSION_ID} source=screen "
                        f"tmux={TMUX} 屏幕可见权限面板但 SSE 未收到 permission.asked（探针晚于面板启动）",
                        flush=True,
                    )
                    sys.exit(0)
            else:
                screen_panel_hits = 0

        # SSE 断开期间：到点就重连；屏幕检查不受影响，照常按时钟进行
        if reconnect_at is not None and now >= reconnect_at:
            reconnect_at = None
            reconnect_attempt += 1
            remaining = max(1, int(deadline - now + 0.999))
            try:
                new_url = service_url()
                if not new_url.startswith("http"):
                    raise RuntimeError(f"service 地址异常：{new_url!r}")
                proc, lines = connect(new_url, password(), remaining)
                conn_lines = 0
                print(f"SSE-RECONNECT attempt={reconnect_attempt} url={new_url}", flush=True)
            except Exception as exc:
                reconnect_at = now + reconnect_delay
                print(f"SSE-LOST 重连失败（{exc}），{reconnect_delay}s 后再试（屏幕补位继续）", flush=True)
                reconnect_delay = min(reconnect_delay * 2, 8)

        try:
            line = lines.get(timeout=LOOP_TICK)
        except queue.Empty:
            continue
        if line is None:
            # 这条连接结束了。离 deadline 不足 2s 视为 --max-time 自然到点，照旧收尾；
            # 否则是 SSE 异常断开：回收 curl、排期重连，主循环继续（屏幕补位不停）
            rc = reap(proc)
            if stop_requested:
                sys.exit(0)   # 进程组被整体终止时 curl 往往先退，别误报成 SSE 断开
            if deadline - time.time() <= 2:
                break
            if conn_lines > 0:
                reconnect_delay = 1
            reconnect_at = time.time() + reconnect_delay
            print(f"SSE-LOST rc={rc} 本连接收到 {conn_lines} 行，{reconnect_delay}s 后重连（屏幕补位继续）", flush=True)
            reconnect_delay = min(reconnect_delay * 2, 8)
            lines = queue.Queue()
            continue
        line = line.strip()
        if line:
            conn_lines += 1
        now = time.time()

        if not line.startswith("data: "):
            continue
        try:
            ev = json.loads(line[6:])
        except Exception:
            continue

        data = ev.get("data") or {}
        if data.get("sessionID") != SESSION_ID:
            continue          # 不是本会话，丢开

        last_any_event = now
        etype = ev.get("type", "")
        ts = (ev.get("created") or int(now * 1000)) / 1000.0

        if etype == "session.execution.started":
            started_at = ts
            print(f"TURN-START ts={ts:.3f}", flush=True)

        elif etype in TERMINAL_EVENTS:
            key = (etype, data.get("id") or data.get("messageID") or ts)
            if key in seen_terminal:
                continue
            seen_terminal.add(key)
            dur = f"{ts - started_at:.2f}s" if started_at else "?"
            print(
                f"STAGE-DONE session={SESSION_ID} event={etype} "
                f"start_ts={started_at if started_at else '?'} "
                f"end_ts={ts:.3f} duration={dur}",
                flush=True,
            )
            sys.exit(0)

        elif etype == "permission.asked":
            rid = data.get("id")
            asked_permissions[rid] = ts
            print(
                f"PERMISSION-ASKED id={rid} action={data.get('action')} "
                f"resources={data.get('resources')}",
                flush=True,
            )

        elif etype == "permission.replied":
            asked_permissions.pop(data.get("requestID"), None)
            print(f"PERMISSION-REPLIED reply={data.get('reply')}", flush=True)

    # curl 自然结束（--max-time 到点，退出码 28 = 预期）
    rc = proc.poll()
    print(f"CURL-END rc={rc}（28=--max-time 到点，预期非故障）", flush=True)

    # 收尾前最后核一次：有没有 terminal 事件刚好在最后
    if not seen_terminal:
        pending = list(asked_permissions)
        if pending:
            print(f"QUESTION-PANEL session={SESSION_ID} 待批={pending}", flush=True)
        else:
            print(f"WATCH-TIMEOUT conv={SESSION_ID} 未见终态事件", flush=True)

except SystemExit:
    raise
except KeyboardInterrupt:
    pass
finally:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
