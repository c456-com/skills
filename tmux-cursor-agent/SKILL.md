---
name: tmux-cursor-agent
category: autonomous-ai-agents
tags: [tmux, cursor, agent, monitoring, automation]
description: "Control and monitor Cursor AI agents through tmux — session lifecycle, state detection (EXECUTING/STOPPED), four-step messaging protocol, cancel operations, and monitoring daemon. Supports pane-level monitoring (--pane flag for session:window.pane)."
version: 0.3.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tmux, cursor, agent, monitoring, automation]
    related_skills: [ai-coding-agents, cursor-agent-orchestration]
---

# tmux-cursor-agent

> Control and monitor Cursor AI agents through tmux — detect states, send messages, cancel execution.

> **Terminology alias:** This user calls tmux「多窗口终端」(multi-window terminal). When they say「多窗口终端」「终端管理器」or「终端分屏」, treat it as equivalent to tmux. This alias applies throughout: "start a 多窗口终端 session", "capture pane from 多窗口终端", etc.

Published at: `c456-com/skills` — <https://github.com/c456-com/skills/tree/main/tmux-cursor-agent>
Install via: `npx skills add c456-com/skills --skill tmux-cursor-agent -y`
Local clone: `git clone git@github.com:c456-com/skills.git /path/to/skills`

## Quick Reference

### Start cursor-agent in tmux

```bash
tmux new-session -d -s cursor -n agent -c /path/to/project
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter
sleep 4
# Verify it's running (pane_current_command shows "node" not "cursor-agent")
tmux list-windows -t cursor -F '#{window_index}: #{window_name} - #{pane_current_command}'
# Expected: pane shows "node" (the Node.js runtime), NOT "zsh" or "bash"
```

### First-Time Setup: Login & Workspace Trust

On first start (or after clearing auth), cursor-agent prompts for browser-based OAuth login:

```bash
# Start agent → it shows a login link
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter
sleep 8

# Check if login is needed
tmux capture-pane -t cursor:0 -p -S -5
# → Shows: "Press any key to log in..." or a loginDeepControl URL

# Press any key to trigger browser login
tmux send-keys -t cursor:0 Enter

# On macOS, the browser opens automatically. On headless:
# Copy the login URL and open it in a browser on another machine.
sleep 30  # Wait for browser login to complete

# After login: "⚠ Workspace Trust Required" prompt appears
# Press 'a' to trust the workspace, then wait for ready
tmux send-keys -t cursor:0 a
sleep 10

# Verify ready: should show "→ Plan, search, build anything"
tmux capture-pane -t cursor:0 -p -S -3
```

**Multiple instances with same account share credentials** — once one session logs in, others reuse the token automatically. To use a different account, clear the cached token first (location varies by platform; check `~/.local/share/cursor-agent/`).

### Check State

```bash
git clone https://github.com/c456-com/skills.git /tmp/tmux-cursor-agent
cd /tmp/tmux-cursor-agent/tmux-cursor-agent
python3 -m core.watch cursor 0 --debug
# → state=executing (agent working) or state=stopped (idle)
```

Or from a local clone:

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.watch cursor 0 --debug
```

### Send Message (Four-Step Protocol)

```bash
# 1. Verify idle + clean input
tmux capture-pane -t cursor:0 -p -S -5
# 2. Type (NO Enter!)
tmux send-keys -t cursor:0 "Your message here"
# 3. Wait
sleep 2
# 4. Enter + verify
tmux send-keys -t cursor:0 Enter
sleep 3
tmux capture-pane -t cursor:0 -p -S -5
```

### Cancel

```bash
tmux send-keys -t cursor:0 C-c      # Cancel execution
tmux send-keys -t cursor:0 Escape   # Clear unsubmitted input
```

### Graceful Shutdown

Use `/exit` to gracefully shut down cursor-agent (preserves session state for resume). Do NOT kill the process or use C-c alone.

```bash
# Type /exit and press Enter (watch for autocomplete)
tmux send-keys -t cursor:0 "/exit" Enter
sleep 3

# If /exit showed an autocomplete menu (common), just press Enter again
# to confirm the selected action
tmux send-keys -t cursor:0 Enter
sleep 2

# Verify back at shell prompt
tmux capture-pane -t cursor:0 -p -S -2
# → Should show shell prompt (zsh/bash), not cursor-agent interface
```

### Monitor with Daemon

Register sessions and start the monitoring daemon for automatic CURSOR-STOPPED notifications.

The daemon supports two modes of pane targeting:

| Mode | Example | When to Use |
|------|---------|-------------|
| **Window-level** (default) | `session 0` → `session:0` | One agent per window (team work mode) |
| **Pane-level** | `session 0 --pane 3` → `session:0.3` | Multiple agents per window (conference mode) |

> **Pane-level layout script:** For dynamic multi-pane layout management (cols/grid/focus/zoom), see the `cursor-agent-orchestration` skill's `templates/roundtable-layout.sh`.

#### Window-level (default, one agent per window)

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.monitor add --group my-group cursor-dev 0 --label "Dev"
```

#### Pane-level (multiple agents in one window)

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.monitor add --group summit c456-summit 0 --pane 0 --label "PM"
python3 -m core.monitor add --group summit c456-summit 0 --pane 1 --label "Arch"
python3 -m core.monitor add --group summit c456-summit 0 --pane 2 --label "Dev"
python3 -m core.monitor add --group summit c456-summit 0 --pane 3 --label "Analyst"
```

> **⚠️ CRITICAL: Verify role labels before registering.** Do NOT trust manually-set pane titles or initial assumptions. Cursor-agent dynamically updates pane titles after initialization, so early labels are often wrong. Before registering, ask EVERY pane to self-identify:
> 1. Send `你是谁？请用一句话介绍你的角色职责` to each pane (four-step protocol)
> 2. Wait for responses, read the actual role from each pane's reply
> 3. Only then register with the verified labels
>
> Also scan ALL panes first — don't assume you know the count:
> ```bash
> tmux list-panes -t session:0 -F '#{pane_index}: #{pane_title}'
> ```
> A window may have more panes than you remember (e.g., 10 instead of 6).

#### Multi-window monitoring (same group)

One monitor group can track panes across multiple windows. Register panes from different windows under the same group:

```bash
# Window 0 panes
python3 -m core.monitor add --group summit c456-summit 0 --pane 0 --label "PM"
python3 -m core.monitor add --group summit c456-summit 0 --pane 1 --label "ARCH"

# Window 1 panes (same group)
python3 -m core.monitor add --group summit c456-summit 1 --pane 0 --label "FEASIBILITY-A"
python3 -m core.monitor add --group summit c456-summit 1 --pane 1 --label "FEASIBILITY-B"
```

The daemon emits `CURSOR-STOPPED:group:session:window:pane:reason` for pane-level, identifying which window and pane changed state.

Each pane is tracked independently with its own state file (`cursor-watch-{session}-{window}-{pane}.state`).
CURSOR-STOPPED notifications include the pane index:
- Window-level: `CURSOR-STOPPED:group:session:window:reason`
- Pane-level: `CURSOR-STOPPED:group:session:window:pane:reason`

#### Manual pane status check

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.watch c456-summit 0 --pane 0 --debug
# → state=executing or state=stopped
```

#### Starting the daemon

> **⚠️ 强制前置：执行以下任何命令前，必须先加载本技能**
>
> 你在记忆中保存的 daemon 命令是**错误或过时的**。只有技能文档中的模板包含正确的 `watch_patterns` 参数。
>
> ```python
> # 必须执行这一行，然后读下面三步法
> skill_view(name='tmux-cursor-agent')
> ```
>
> **为什么必须这么做：** 你自己记忆中的 daemon 命令总是缺 `watch_patterns`，导致 CURSOR-STOPPED 永远不会通知到对话。只有每次从这里复制才能保证参数完整。

> **⚠️ 三步执行法（每次必做，缺一不可）**

> | 步 | 命令 | 验证 |
> |----|------|------|
> | **0 加载技能** | `skill_view(name='tmux-cursor-agent')` | 读到当前这行 |
> | **① 杀旧** | `pkill -f "python3 -m core.monitor daemon" 2>/dev/null; sleep 2` | `ps aux \| grep core.monitor \| grep -v grep` → 输出 **空** |
> | **② 注册** | `python3 -m core.monitor add ...` | `python3 -m core.monitor list --group X` → 显示所有 pane |
> | **③ 启动** | `terminal(background=true, watch_patterns=["CURSOR-STOPPED:"], command="cd ~/Codes/c456-com/skills/tmux-cursor-agent && exec python3 -m core.monitor daemon --group GROUP")` | `process(action='poll')` → 显示 `CURSOR-MONITOR-START` |
>
> **⛔ 常见致死错误：**
> - 忘了 `watch_patterns` → daemon 静默运行，你永远收不到任何 CURSOR-STOPPED
> - 用了 `notify_on_complete=true` → daemon 永不完成，此参数对 daemon 无效
> - 不先杀旧进程 → 多个 daemon 打架，state 文件冲突，通知乱发
>
> **正确的模板（直接复制）：**
>
> ```bash
> # ① 杀旧
> pkill -f "python3 -m core.monitor daemon" 2>/dev/null; sleep 2
> ps aux | grep "core.monitor" | grep -v grep | wc -l   # 必须 = 0
>
> # ② 注册（跳过，已注册）
>
> # ③ 启动（关键：同时要 background=true + watch_patterns）
> terminal(
>   command="cd /path/to/skills/tmux-cursor-agent && exec python3 -m core.monitor daemon --group YOUR_GROUP",
>   background=true,
>   watch_patterns=["CURSOR-STOPPED:"]
> )
> ```

## Scope Discipline

**When using tmux + cursor-agent, stay focused on:**

| ✅ In Scope | ❌ Out of Scope |
|------------|----------------|
| Starting/stopping agent in tmux | Git worktree management |
| Detecting EXECUTING/STOPPED states per pane | Team role workflows (PM/Arch/Dev) |
| Window-level and pane-level monitoring | Project-specific code strategies |
| Sending messages (four-step protocol) | CI/CD pipeline setup |
| Cancelling execution/input | Multi-agent task orchestration |
| Monitoring daemon for state changes | Any task the agent itself should do |
| Capturing pane content | |
| Multi-pane layout setup (3×2, 2×2, custom) | |

## Pane Title State Detection

cursor-agent automatically updates the tmux pane title with its status as a suffix, providing a lightweight state detection method that doesn't require capturing pane content.

### Setting Custom Pane Titles (via `/rename`)

To prevent cursor-agent from overwriting your custom pane title with an English role name:

1. Set the tmux pane title first:
   ```bash
   tmux select-pane -t session:0.0 -T "PM 产品经理"
   ```

2. Ask cursor-agent to claim the name via `/rename` (four-step protocol):
   ```bash
   tmux send-keys -t session:0.0 "/rename PM 产品经理"
   sleep 2
   tmux send-keys -t session:0.0 Enter
   ```

After `/rename`, cursor-agent treats the custom name as its own display name and only appends the status suffix (` - ✅ Ready` / ` - ⏳ Working`), preserving your label:
- Idle: `PM 产品经理 - ✅ Ready`
- Working: `PM 产品经理 - ⏳ Working`

**Do NOT** rely on `tmux select-pane -T` alone — cursor-agent overrides manually-set titles with default English role names on its next state change.

| Title suffix | State | Meaning |
|-------------|-------|---------|
| `PM 产品经理` (no suffix, custom label) | Idle | Pane title was manually set — still works normally |
| `Pricing Analyst - ✅ Ready` | STOPPED | Agent is idle, waiting for input |
| `Pricing Analyst - ⏳ Working ···` | EXECUTING | Agent is actively processing |

To check state by title suffix (faster than `capture-pane`):

```bash
title=$(tmux display-message -p -t session:0.4 '#{pane_title}')
echo "$title" | grep -qE "⏳|[⠘⠠⠙⠸⠴⠦]" && echo "EXECUTING" || echo "STOPPED"
```

**Note:** Manually-set pane titles (e.g. via `select-pane -T "PM 产品经理"`) may be overridden by cursor-agent when its status changes. Re-apply custom titles after cursor-agent starts, or use the title suffix as a reliable alternative.

### Cross-Platform State Detection

Pane title suffixes (` - ✅ Ready` / ` - ⏳ Working`) work reliably on **macOS**. On **Linux**, cursor-agent keeps the title as `Cursor Agent` regardless of state — fall back to content scanning:

```bash
content=$(tmux capture-pane -t session:0.pane -p -S -5)
echo "$content" | grep -qE "(Working|Reading|Thinking|Editing)" && echo "EXECUTING"
```

The `layout.sh auto` command implements dual-mode (title-first, content-fallback).

### Tmux Settings for Pane Titles

For cursor-agent's title updates to stick:

```bash
tmux set -t session:window automatic-rename off   # Prevent tmux overriding titles
tmux set -g allow-rename on                        # Allow programs to set titles
tmux set -t session pane-border-status top         # Show titles in pane borders
```

## Pitfalls

1. **Wrong pane**: Always check `pane_current_command` is a Node process (shows `node`) before sending. Window names lie.
2. **Enter swallowed**: Always separate text from Enter (sleep 2 between). Never `send-keys "text" Enter` as one shot.
3. **No verify**: Always `capture-pane` after sending to confirm message is in conversation history, not stuck in input bar.
4. **Sending during execution**: Check state first. If agent is EXECUTING, wait.
5. **Placeholder ≠ idle**: `→ Add a follow-up` is an empty input box, not a task-complete signal.
6. **Percentage ≠ progress**: `Auto · 84.8%` is context window usage, not task progress.
7. **Selection menu**: Use arrow keys + Space, never send numbers directly.
8. **Daemon without panes**: Verify `total > 0` after starting daemon, or it monitors nothing.
9. **`/exit` autocomplete**: Typing `/exit` often shows an autocomplete menu. Always send Enter TWICE: once to select `/exit` from the menu, once to confirm. Check the pane afterwards — if still in cursor-agent UI, send another Enter.
10. **`pane_current_command` shows `node` not `cursor-agent`**: cursor-agent runs on Node.js, so `pane_current_command` will be `node`, not `cursor-agent`. Use `capture-pane` content to verify agent is actually running.
11. **Workspace trust blocks startup**: After OAuth login, cursor-agent shows a trust dialog requiring `a` key. Without it, the agent stays blocked and won't accept any input.
12. **Multi-session auth sharing**: Starting a second cursor-agent in another tmux window reuses the first session's auth token automatically. To force a different account, clear cached credentials first.
13. **Daemon rate limiting**: CURSOR-STOPPED notifications for the same window can be suppressed if multiple events fire within the 15-second watch interval (Hermes drops duplicates). Don't rely on catching every notification — use `process(action='poll')` or manual `capture-pane` for confirmation.
14. **Register before daemon**: Always register windows (via `monitor add`) BEFORE starting the daemon. The daemon only monitors windows that are already registered when it starts.
15. **"Exited" false positive for cursor-agent**: The daemon may report `state=exited` for cursor-agent sessions that are actually still running. This happens because cursor-agent runs on Node.js (process name `node`), and a temporary shell command can switch `pane_current_command` briefly. Verify with `capture-pane` before assuming the agent crashed.
16. **Multi-pane monitoring**: When monitoring multiple panes within the same window (conference layout), use `--pane` flag: `monitor add --group g session window --pane N --label "Role"`. The watch script accesses panes as `session:window.pane` (e.g. `c456-summit:0.0`).
17. **`--auto-layout` daemon flag**: Pass `--auto-layout` to `daemon` to auto-switch tmux layout based on which panes are working. Requires `layout.sh` in the project. See the `c456-ai-summit` skill for setup.
18. **`automatic-rename off` required**: Without this, tmux overrides cursor-agent's pane title with the running command name. Set `tmux set -t window automatic-rename off` after creating each window.
19. **Shell commands vs agent messages**: `tmux send-keys` with shell commands (echo/cat/heredoc) executes in the SHELL behind cursor-agent, never reaching the agent's conversation. Always use the four-step protocol with **plain text only** — no shell syntax, no file redirections. See `references/messaging.md` → Anti-pattern section for examples and recovery.
20. **Don't trust initial pane labels**: When setting up pane-level monitoring for multi-agent windows, cursor-agent dynamically overrides manually-set pane titles after initialization. The title you see before agents start may differ from their actual role after they load. Always verify by asking each pane `你是谁？请用一句话介绍你的角色职责` (via four-step protocol), reading their self-identified role from the response, then registering with the verified label. Example: a pane initially labeled "PM" may actually be "Trend Researcher" after cursor-agent initializes.
22. **Scan ALL panes first**: A window may have more panes than your initial setup script created (e.g., 10 instead of 6). Always run `tmux list-panes -t session:window -F '#{pane_index}: #{pane_title}'` before registration to discover every pane. Don't assume 0..N covers everything.
23. **Daemon process accumulation**: Each `terminal(background=true)` start of the daemon creates a new process. Old daemons persist as orphan processes even after the background session is killed via Hermes. Accumulation of 5+ daemon processes is common after repeated restarts. Before restarting: (a) kill all daemon processes: `pkill -f "python3 -m core.monitor daemon"` (b) verify clean with `ps aux | grep core.monitor | grep -v grep` (c) only then start the new daemon. Using `execute_code` with explicit `kill -9 PID` for each old process is more reliable than shell-level `pkill` when running through Hermes background process manager.
24. **Dirty input buffer blocks Four-Step Protocol**: After a failed broadcast (sending shell commands like `cat`/`echo` instead of agent messages), the pane's input buffer may contain stale shell text that prevents new messages from reaching the agent. The `→ Add a follow-up` idle indicator is visible, but `send-keys` keystrokes are consumed by the stale shell state rather than the agent's stdin. Recovery sequence: `tmux send-keys -t session:0.pane Escape` (cancel autocomplete), `sleep 1`, `tmux send-keys -t session:0.pane C-c` (interrupt stale process), `sleep 2`, `tmux send-keys -t session:0.pane C-u` (clear line), `tmux send-keys -t session:0.pane C-k` (clear to end), `sleep 1`, then verify with `capture-pane`. Only after `→ Add a follow-up` shows no stale content should you attempt the Four-Step Protocol again.

25. **Daemon without `watch_patterns` = no CURSOR-STOPPED notifications**: If the daemon is started via `terminal(background=true)` WITHOUT `watch_patterns=["CURSOR-STOPPED:"]`, the state-change output goes to the daemon's stdout which Hermes captures as plain process output — it is NEVER forwarded to the conversation. You can `process(action='poll')` to see current states, but you will never learn WHEN a pane transitioned from executing→stopped. Always pair `background=true` with `watch_patterns=["CURSOR-STOPPED:"]`. Note: `notify_on_complete=true` fires once when the daemon exits (not useful for a long-lived daemon); `watch_patterns` fires on every matching line. They serve different purposes and cannot substitute for each other.

## Documentation

Full docs in the repository `tmux-cursor-agent/docs/`:

```
01-quickstart.md         Quick start guide
02-session-lifecycle.md  Create/verify/destroy sessions
03-state-detection.md    How EXECUTING/STOPPED detection works
04-messaging-protocol.md Four-step protocol detail
05-monitoring-daemon.md  Daemon configuration
06-pitfalls.md           Full pitfall catalog
```

### Skill References

| File | About |
|------|-------|
| [`references/calibration.md`](references/calibration.md) | Fixture test framework & how to add/modify state detection tests |
| [`references/state-detection.md`](references/state-detection.md) | State detection patterns & edge cases |
| [`references/messaging.md`](references/messaging.md) | Messaging protocol deep dive |
| [`references/publishing-pattern.md`](references/publishing-pattern.md) | How to add/rename/remove a skill in c456-com/skills repo |
