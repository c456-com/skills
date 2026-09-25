#!/usr/bin/env python3
"""OpenCode 监控探针：旁听 SSE，把「一轮结束」转成进程完成通知唤醒 Hermes。

用法：
    watch.py <session_id> <timeout_seconds> [--tmux-session <name>]

设计要点（都是实测踩出来的）：
  · 终态判据 = 本 session 出现过 execution.succeeded / execution.interrupted /
    session.step.failed / session.tool.failed 任一。只等 succeeded 会漏掉被打断和失败的轮次。
  · 按 data.sessionID 分流：一条 SSE 流里混着所有 session 的事件。
  · 绝不用「最后一行是不是 succeeded」——事件到达顺序不固定。
  · 权限面板卡死：permission.asked 出现后长时间无 permission.replied ⇒ 报 QUESTION-PANEL。
  · 必须由 Hermes 托管（terminal(background=true, notify_on_complete=true)），
    用 subprocess.Popen 起的进程 Hermes 不认，退出时不通知。
  · 正常退出码可能是 curl 的 28（--max-time 到点），不是故障。
"""
import sys
import os
import json
import time
import signal
import subprocess

SESSION_ID = sys.argv[1]
TIMEOUT = int(sys.argv[2]) if len(sys.argv) > 2 else 900
TMUX = None
if "--tmux-session" in sys.argv:
    TMUX = sys.argv[sys.argv.index("--tmux-session") + 1]

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
    if not TMUX:
        return ""
    return subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", f"{TMUX}:0", "-S", "-10"],
        capture_output=True, text=True,
    ).stdout


def on_signal(signum, frame):
    # curl 是子进程，用管道关闭自然结束；不吞信号，让上层能感知
    raise SystemExit(0)


signal.signal(signal.SIGTERM, on_signal)

url = service_url()
pw = password()
if not url.startswith("http"):
    sys.exit(f"拿不到 service 地址：{url!r}（opencode service status 输出异常）")

print(f"PROBE-START session={SESSION_ID} url={url} timeout={TIMEOUT}s", flush=True)

# 用管道跑 curl，边读边解析；一行一个 SSE data
proc = subprocess.Popen(
    ["curl", "-s", "-N", "-u", f"opencode:{pw}", "--max-time", str(TIMEOUT),
     f"{url}/api/event"],
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, bufsize=1,
)

started_at = None          # 本 session 的 execution.started 时间
seen_terminal = set()      # 已报告过的终态（id 或 key）
asked_permissions = {}     # requestID -> 时间戳
deadline = time.time() + TIMEOUT
last_any_event = time.time()

try:
    for line in proc.stdout:
        line = line.strip()
        now = time.time()
        if now > deadline:
            print(f"WATCH-TIMEOUT conv={SESSION_ID}", flush=True)
            break
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
