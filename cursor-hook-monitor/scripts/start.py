#!/usr/bin/env python3
"""方案 A 启动器：预建会话拿 conversation_id → 装 hook → 启动 TUI。

用法：
    start.py <worktree_path> <tmux_session_name> [initial_prompt]

产出（stdout，机器可读，交给调用方解析）：
    CONV=<conversation_id>
    SESSION=<tmux_session>
    EVENTS=<事件流文件路径>
    HOOK=<装好的 hook 脚本路径>
    PROMPT_SENT=1            （仅当传了 initial_prompt）

关键顺序（顺序错了监控就不成立，都是实测踩出来的）：
    1. create-chat 先拿 conversation_id —— 提前知道会话身份，监控路径可先算好
    2. 把 hook 装进该工作树的 .cursor/hooks.json —— 必须在启动前就位，
       长驻进程不重载 hook 配置，事后补配对该会话永远无效
    3. chmod +x hook 脚本 —— 漏了会静默失效且 agent 不报错
    4. 用 CURSOR_MONITOR_TAG=<conversation_id> + --resume=<conversation_id> 启动 TUI
       ⇒ tag / 会话身份 / 事件文件 三者同一个 ID，天然对齐
    5. 冒烟：确认 TUI 真的进入输入框

  ⚠️ 本脚本 **不** 负责挂监控探针。探针必须由 Hermes 自己托管：
        terminal(background=true, notify_on_complete=true,
                 command="python3 <skill>/scripts/watch.py <CONV> <timeout> --tmux-session <SESSION>")
     若在本脚本里用 subprocess.Popen 起探针，Hermes 不托管那个进程，
     进程退出时不会产生通知 ⇒ Hermes 永远叫不醒（实测踩过）。
"""
import os
import sys
import json
import time
import shutil
import subprocess

WORKTREE = sys.argv[1]
SESSION = sys.argv[2]
INITIAL_PROMPT = sys.argv[3] if len(sys.argv) > 3 else None

BASE = os.path.dirname(os.path.abspath(__file__))
# 日志不落技能目录（会污染技能、随技能分发跑出去，且技能目录可能只读）。
# 默认落 Hermes scratch；可由 CURSOR_MONITOR_LOG_DIR 覆盖。
LOG_DIR = os.environ.get("CURSOR_MONITOR_LOG_DIR") or os.path.join(
    os.environ.get("TMPDIR", "/tmp").rstrip("/"), "cursor-hook-monitor", "logs"
)
HOOK_SRC = os.path.join(BASE, "hook_event.py")

os.makedirs(LOG_DIR, exist_ok=True)

# 1) 预建会话，拿 conversation_id
res = subprocess.run(
    ["cursor-agent", "create-chat"],
    cwd=WORKTREE, capture_output=True, text=True, timeout=60,
)
conv = res.stdout.strip().splitlines()[-1].strip() if res.stdout.strip() else ""
if not conv:
    sys.exit(f"create-chat 未返回 conversation_id（stderr={res.stderr.strip()[:200]}）")
print(f"CONV={conv}", flush=True)

# 2) 装 hook —— 必须在 TUI 启动前完成
cursor_dir = os.path.join(WORKTREE, ".cursor")
os.makedirs(cursor_dir, exist_ok=True)
hook_dst = os.path.join(cursor_dir, "cursor-monitor-hook.py")
shutil.copy(HOOK_SRC, hook_dst)
os.chmod(hook_dst, 0o755)  # 漏这行 = hook 静默失效（实测两次踩到）

hooks_path = os.path.join(cursor_dir, "hooks.json")
existing = {}
if os.path.exists(hooks_path):
    try:
        with open(hooks_path) as f:
            existing = json.load(f)
    except Exception:
        existing = {}
hooks = existing.setdefault("hooks", {})
for evt in ("beforeSubmitPrompt", "afterAgentResponse", "stop", "afterFileEdit"):
    hooks[evt] = [{"command": hook_dst}]
existing.setdefault("version", 1)
with open(hooks_path, "w") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

# 3) 事件流路径（监控在 agent 启动前就能确定）
os.makedirs(LOG_DIR, exist_ok=True)
events = os.path.join(LOG_DIR, f"{conv}.jsonc")

# 4) 启动 TUI：tag / resume / 事件文件名 三者用同一个 ID
cmd = (
    f"CURSOR_MONITOR_TAG={conv} "
    f"CURSOR_MONITOR_LOG_DIR={LOG_DIR} "
    f"cursor-agent --trust --resume={conv}"
)
subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
subprocess.run(
    ["tmux", "new-session", "-d", "-s", SESSION, "-n", "agent", "-c", WORKTREE], check=True
)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", cmd], check=True)
time.sleep(2)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
time.sleep(12)

title = subprocess.run(
    ["tmux", "display-message", "-p", "-t", f"{SESSION}:0", "#{pane_title}"],
    capture_output=True, text=True,
).stdout.strip()
if "Ready" not in title:
    sys.exit(f"TUI 未就绪，title={title!r}（检查 pane：tmux capture-pane -t {SESSION}:0 -p -S -20）")

print(f"SESSION={SESSION}", flush=True)
print(f"TITLE={title}", flush=True)
print(f"EVENTS={events}", flush=True)
print(f"HOOK={hook_dst}", flush=True)

if INITIAL_PROMPT:
    # 四步发送协议：text → 2s → Enter → 3s → Enter（单条 send-keys 吞 Enter）
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "-l", INITIAL_PROMPT], check=True)
    time.sleep(2)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
    time.sleep(3)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
    print("PROMPT_SENT=1", flush=True)

print("# 下一步：由 Hermes 托管监控探针（不要用 subprocess 起，见文件头说明）", flush=True)
