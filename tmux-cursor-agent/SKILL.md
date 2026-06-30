---
name: tmux-cursor-agent
category: autonomous-ai-agents
tags: [tmux, cursor, agent, monitoring, automation]
description: "Control and monitor Cursor AI agents through tmux — session lifecycle, state detection (EXECUTING/STOPPED), four-step messaging protocol, cancel operations, and monitoring daemon."
triggers:
  - 启动/重启 cursor-agent session 时
  - 需要检测 cursor agent 的工作状态时
  - 向 cursor agent 发送消息时
  - 需要取消执行或输入时
  - 设置 daemon 监控时
  - 收到 CURSOR-STOPPED 通知时
---

# tmux-cursor-agent

> Control and monitor Cursor AI agents through tmux — session lifecycle, state detection, messaging protocol, and monitoring daemon.

## Quick Reference

### Start cursor-agent in tmux

```bash
# Create session and start agent
tmux new-session -d -s cursor -n agent -c /path/to/project
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter

# Verify it's running
sleep 4
tmux list-windows -t cursor -F '#{window_index}: #{pane_current_command}'
# Must show: "0: agent - cursor-agent" (not zsh/bash)
```

### Check Agent State

```bash
# Quick state check
python3 core/watch.py cursor 0 --debug

# Or use capture-pane directly
tmux capture-pane -t cursor:0 -p -S -5

# EXECUTING signals: spinner ⠠⠛, Working/Running/Reading/Editing text
# STOPPED (idle): no activity, just "→ Add a follow-up"
```

### Send Message (Four-Step Protocol)

```bash
# 1. Verify idle + clean input box
tmux capture-pane -t cursor:0 -p -S -5

# 2. Type message (NO Enter!)
tmux send-keys -t cursor:0 "Your message here"

# 3. Wait
sleep 2

# 4. Submit Enter + verify
tmux send-keys -t cursor:0 Enter
sleep 3
tmux capture-pane -t cursor:0 -p -S -5
```

### Cancel Operations

```bash
# Cancel execution (Ctrl+C)
tmux send-keys -t cursor:0 C-c

# Clear unsubmitted input (Escape)
tmux send-keys -t cursor:0 Escape

# Exit agent gracefully
tmux send-keys -t cursor:0 "/exit" Enter
```

### Monitor with Daemon

```bash
export MON="python3 core/monitor.py"

# Register pane
$MON group-create default --label "My Group"
$MON add --group default cursor 0 --label "Dev Agent"

# Start daemon (background)
$MON daemon --group default

# List status
$MON list
$MON status --group default
```

## Core Tools

```bash
# Path setup
export TCA_DIR="/path/to/tmux-cursor-agent"
```

| Tool | Command | Purpose |
|------|---------|---------|
| **State Detection** | `python3 core/watch.py <session> <window> [lines]` | Detect EXECUTING/STOPPED |
| **Pane Reading** | `python3 core/read.py capture <session> <window> --lines N` | Read pane content |
| **Monitoring Daemon** | `python3 core/monitor.py daemon --group <name>` | Poll and notify state changes |
| **Group Management** | `python3 core/monitor.py group-create/remove/list` | Manage monitor groups |
| **Shell Helpers** | `source core/cursor-watch-lib.sh` | Shell functions for state detection |

## State Detection Reference

### EXECUTING (Agent is working)

| Signal | Example | How to detect |
|--------|---------|---------------|
| Braille spinner | `⠠⠛` `⠘⠤` | Unicode Braille pattern in pane |
| Status text | `Working`, `Reading`, `Editing`, `Running` | Activity region scan |
| Background tasks | `3 background tasks` | `N background tasks?` regex |
| Progress | `progress: 120/500` | Monitoring progress pattern |

### STOPPED (Agent is idle)

| Reason | Meaning | Detection |
|--------|---------|-----------|
| `idle` | Normal idle, awaiting input | No activity signals |
| `needs_approval` | Command approval prompt | `Run this command?` visible |
| `needs_input` | Plan mode question | `Question N of M` visible |
| `task_done` | Task appears complete | `All tests passed` / `✅` markers |
| `exited` | Exit confirmation | `Press Ctrl+C again to exit` |
| `user_draft` | Unsubmitted text in input | Non-placeholder `→ text` |
| `empty` | No pane content | Capture returned empty |

### Don't Misinterpret

| UI Element | Actual Meaning |
|-----------|----------------|
| `→ Add a follow-up` | Input box placeholder (empty). NOT idle signal. |
| `Auto · 84.8%` | Context window usage. NOT task progress. |
| `Run Everything` | Permission mode flag. NOT a button/error. |
| `N tasks` | Compass suggestion count. Agent awaiting next message. |

## Messaging Protocol

### Four Steps (Mandatory)

```
① capture-pane → verify STOPPED + clean input
② send-keys "text" (NO Enter!)
③ sleep 2
④ send-keys Enter → capture-pane verify
```

### Selection Menu Handling

| Action | Command |
|--------|---------|
| Navigate up | `send-keys Up` |
| Navigate down | `send-keys Down` |
| Toggle select | `send-keys Space` |
| Submit | `send-keys Enter` |
| Skip | `send-keys Escape` |

**Don't send numbers directly** — they go into "Other" input field.

## Pitfalls to Watch For

1. **Wrong pane**: Always check `pane_current_command` is `cursor-agent`, not `zsh`
2. **Enter swallowed**: Always separate text from Enter (sleep 2 between)
3. **No verify**: Always `capture-pane` after sending to confirm delivery
4. **Sending during execution**: Wait for STOPPED state first
5. **Percentage = progress**: `Auto · 80%` is context usage, NOT task progress
6. **Shell chars**: `<` `>` `|` `$()` have shell meaning — escape or avoid
