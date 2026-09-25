#!/usr/bin/env python3
"""接管一个已经在跑的 cursor-agent，让它获得 hook 监控能力。

为什么需要这个：
  已启动的进程**不会重载 hook 配置**——事后在 .cursor/hooks.json 里补配置，
  对该进程永远无效（实测）。但退出再恢复是**新进程**，新进程会读新配置。
  所以接管路径 = 退出 → 拿 conversation_id → 装 hook → 用同一 ID 恢复。

实测结论（cursor-agent 2026.09.23-86fc751）：
  · 恢复后上下文完整带回（标题、工具记录、文件编辑痕迹都在）
  · 恢复后的新进程 hook 正常触发（实测 3.56s 一轮完整捕获）
  · pane 里**看不到** conversation_id，不能靠肉眼找
  · `cursor-agent ls` 需要真 TTY，脚本里不可用（会报 Ink raw mode 错）
    ⇒ 用 cwd 反查 ~/.cursor/chats/*/*/meta.json 的方式拿 ID

用法：
    adopt.py <worktree_path> <tmux_session> [--conv-id <id>]

流程：
    1. 若给了 --conv-id 直接用；否则按 cwd 反查（取最新那个会话目录）
    2. 退出 agent（/exit）
    3. 装 hook + chmod +x
    4. 用同一 conv_id 作为 tag 恢复
    5. 冒烟确认输入框就绪

输出：
    CONV=<conversation_id>
    SESSION=<tmux_session>
    EVENTS=<事件流路径>
"""
import os
import sys
import json
import time
import glob
import shutil
import subprocess

WORKTREE = sys.argv[1]
SESSION = sys.argv[2]
args = sys.argv[3:]

CONV = None
if "--conv-id" in args:
    CONV = args[args.index("--conv-id") + 1]

BASE = os.path.dirname(os.path.abspath(__file__))
# 日志不落技能目录（会污染技能、随技能分发跑出去，且技能目录可能只读）。
# 默认落 Hermes scratch；可由 CURSOR_MONITOR_LOG_DIR 覆盖。
LOG_DIR = os.environ.get("CURSOR_MONITOR_LOG_DIR") or os.path.join(
    os.environ.get("TMPDIR", "/tmp").rstrip("/"), "cursor-hook-monitor", "logs"
)
HOOK_SRC = os.path.join(BASE, "hook_event.py")
os.makedirs(LOG_DIR, exist_ok=True)


def pane(lines=30):
    return subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0", "-S", f"-{lines}"],
        capture_output=True, text=True,
    ).stdout


def pane_title():
    return subprocess.run(
        ["tmux", "display-message", "-p", "-t", f"{SESSION}:0", "#{pane_title}"],
        capture_output=True, text=True,
    ).stdout.strip()


def find_conv_by_cwd():
    """按工作树反查 conversation_id：~/.cursor/chats/<hash>/<conv_id>/meta.json 的 cwd 字段。"""
    hits = []
    for meta in glob.glob(os.path.expanduser("~/.cursor/chats/*/*/meta.json")):
        try:
            with open(meta) as f:
                d = json.load(f)
        except Exception:
            continue
        if d.get("cwd") == WORKTREE:
            hits.append((d.get("createdAtMs") or 0, os.path.basename(os.path.dirname(meta))))
    if not hits:
        return None
    hits.sort(reverse=True)
    return hits[0][1]


# 1) 拿 conversation_id
if not CONV:
    CONV = find_conv_by_cwd()
if not CONV:
    sys.exit(
        f"无法按 cwd 反查到会话（worktree={WORKTREE}）。\n"
        f"请手动传 --conv-id <id>（可从 ~/.cursor/chats/*/*/meta.json 里找 cwd 匹配的那个目录名）。"
    )
print(f"CONV={CONV}", flush=True)

# 2) 退出 agent（先确认它在输入框，不在忙）
title = pane_title()
if "⏳" in title or "Working" in title:
    sys.exit(f"agent 正在忙（title={title!r}），不要中途接管。等它回到 Ready 再执行。")
if "Ready" not in title:
    sys.exit(f"pane 状态异常（title={title!r}），确认 session 名是否正确。")

subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "/exit"], check=True)
time.sleep(2)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
time.sleep(4)
if "Ready" in pane_title():
    sys.exit("/exit 未生效，仍在 agent 内（可能弹了确认框，看 pane）。")

# 3) 装 hook —— 必须在恢复（新进程）之前落盘
cursor_dir = os.path.join(WORKTREE, ".cursor")
os.makedirs(cursor_dir, exist_ok=True)
hook_dst = os.path.join(cursor_dir, "cursor-monitor-hook.py")
shutil.copy(HOOK_SRC, hook_dst)
os.chmod(hook_dst, 0o755)

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

# 4) 恢复（同一 conv_id 作 tag）
events = os.path.join(LOG_DIR, f"{CONV}.jsonc")
cmd = (
    f"CURSOR_MONITOR_TAG={CONV} "
    f"CURSOR_MONITOR_LOG_DIR={LOG_DIR} "
    f"cursor-agent --trust --resume={CONV}"
)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", cmd], check=True)
time.sleep(2)
subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0", "Enter"], check=True)
time.sleep(12)

title = pane_title()
if "Ready" not in title:
    sys.exit(f"恢复后 TUI 未就绪（title={title!r}）")
print(f"SESSION={SESSION}", flush=True)
print(f"TITLE={title}", flush=True)
print(f"EVENTS={events}", flush=True)
print("# 建议立刻发一轮秒回任务冒烟：确认事件流真的产生了行，再挂 watch.py", flush=True)
