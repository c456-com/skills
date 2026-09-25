#!/usr/bin/env python3
"""探针：复验当前 cursor-agent 版本的 hook 到底触发哪些事件。

用途：换机器 / 换 cursor-agent 版本后，先跑这个确认能力，再决定是否依赖 hook。

用法：
    probe.py [scratch_dir]

它会在 scratch 目录起一个一次性 TUI 会话、装全量候选 hook、发一轮短任务，
打印实测触发的事件列表，然后清理会话（不改任何业务仓）。
"""
import os
import sys
import json
import time
import shutil
import subprocess

SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.expanduser("~"), ".cache", "cursor-hook-probe"
)
BASE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    "sessionStart",
    "beforeSubmitPrompt",
    "afterAgentResponse",
    "afterAgentThought",
    "stop",
    "afterFileEdit",
    "preToolUse",
    "postToolUse",
]

shutil.rmtree(SCRATCH, ignore_errors=True)
os.makedirs(os.path.join(SCRATCH, ".cursor"), exist_ok=True)
os.makedirs(os.path.join(SCRATCH, "logs"), exist_ok=True)

hook = os.path.join(SCRATCH, "hook.py")
shutil.copy(os.path.join(BASE, "hook_event.py"), hook)
os.chmod(hook, 0o755)

with open(os.path.join(SCRATCH, ".cursor", "hooks.json"), "w") as f:
    json.dump(
        {"version": 1, "hooks": {e: [{"command": hook}] for e in CANDIDATES}},
        f, indent=2,
    )

SESSION = "cursor-hook-probe"
env_prefix = (
    f"CURSOR_MONITOR_TAG=probe CURSOR_MONITOR_LOG_DIR={SCRATCH}/logs"
)

subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
subprocess.run(
    ["tmux", "new-session", "-d", "-s", SESSION, "-n", "agent", "-c", SCRATCH], check=True
)
subprocess.run(
    ["tmux", "send-keys", "-t", f"{SESSION}:0",
     f"{env_prefix} cursor-agent --trust --model auto agent"], check=True
)
time.sleep(2)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
time.sleep(12)

title = subprocess.run(
    ["tmux", "display-message", "-p", "-t", f"{SESSION}:0", "#{pane_title}"],
    capture_output=True, text=True,
).stdout.strip()
if "Ready" not in title:
    print(f"TUI 未就绪：{title!r}", file=sys.stderr)
    sys.exit(1)

# 发一轮：短 + 一次工具调用，覆盖有无工具两种情形
for prompt in (
    "Reply with exactly this token and nothing else: PROBE-A",
    "Run this and paste the output: for i in 1 2 3; do echo P-$i; sleep 2; done",
):
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "-l", prompt], check=True)
    time.sleep(2)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
    time.sleep(3)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
    time.sleep(18)

events = os.path.join(SCRATCH, "logs", "probe.jsonc")
fired, not_fired = [], []
if os.path.exists(events):
    with open(events, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line).get("event")
            except Exception:
                continue
            if e not in fired:
                fired.append(e)

for e in CANDIDATES:
    (fired if e in fired else not_fired).append(e) if False else None
not_fired = [e for e in CANDIDATES if e not in fired]

ver = subprocess.run(["cursor-agent", "--version"], capture_output=True, text=True).stdout.strip()
print(f"cursor-agent 版本：{ver}")
print()
print(f"实测触发（{len(fired)}/{len(CANDIDATES)}）：")
for e in fired:
    print(f"  ✓ {e}")
print()
print(f"未触发：")
for e in not_fired:
    print(f"  ✗ {e}")
print()
print(f"事件流：{events}")
print(f"用 timeline.py 看详情：python3 {os.path.join(BASE, 'timeline.py')} {events}")

subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
