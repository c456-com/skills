# Pitfalls

Common mistakes and how to avoid them when using tmux + cursor-agent.

## 1. Sending Messages to Wrong Pane

**❌ The most common error:** Sending Chinese text (or any message) to a plain shell pane, not a cursor-agent pane.

```bash
# WRONG: Window is named "cursor-agent" but running zsh!
tmux send-keys -t cursor:0 "Implement feature" Enter
# → zsh: command not found: Implement
```

**✅ Always verify the pane is running cursor-agent:**
```bash
tmux list-windows -t cursor -F '#{window_index}: #{pane_current_command}'
# pane_current_command must be "cursor-agent", not "zsh"/"bash"/"fish"
```

## 2. Enter Being Swallowed

**❌ Sending text and Enter in one command often fails:**
```bash
# WRONG: tmux may swallow the Enter
tmux send-keys -t cursor:0 "Do something" Enter
```

**✅ Use the four-step protocol:**
```bash
# CORRECT: send text, wait, then Enter separately
tmux send-keys -t cursor:0 "Do something"    # no Enter!
sleep 2
tmux send-keys -t cursor:0 Enter              # separate Enter
sleep 3
tmux capture-pane -t cursor:0 -p -S -5        # verify
```

## 3. Not Verifying After Sending

**❌ Assuming the message was sent:**
```bash
tmux send-keys -t cursor:0 "Do X" Enter
# (continue without checking)
```

**✅ Always verify:**
```bash
sleep 3
tmux capture-pane -t cursor:0 -p -S -5
# ✅ Message in conversation history + Working spinner
# ❌ Text still has → prefix → send another Enter
```

## 4. Sending During Execution

**❌ Sending a message while the agent is working:**
```bash
# Agent shows "Working" spinner — text will queue or get lost
tmux send-keys -t cursor:0 "New urgent task" Enter
```

**✅ Wait for STOPPED first:**
```bash
# Check if agent is executing
python3 core/watch.py cursor 0 --debug
# Only send when state=stopped
```

## 5. Messaging During Background Tasks

**❌ The agent shows `Waiting` with background tasks — messages enter a queue:**
```bash
# Agent is monitoring background shell tasks — text won't be processed
tmux send-keys -t cursor:0 "Do this too" Enter
```

**✅ Wait for background tasks to finish, or check if the agent is truly idle.**

## 6. Placeholder vs. Idle Confusion

**❌ Treating `→ Add a follow-up` as "task complete":**

The placeholder text `→ Add a follow-up` only means the input box is empty. It does NOT mean the agent is done working. The agent could still be processing in the background.

**✅ Use the watch utility to detect actual state:**
```bash
python3 core/watch.py cursor 0 --debug
# Look for "EXECUTING=True/False" — that's your real answer
```

## 7. Percentage Misinterpretation

**❌ Treating `Auto · 84.8%` as task progress:**

The percentage in the status bar is **context window usage**, not task progress. `77% → 80.7%` means the conversation is growing, not that the task is 3.7% more complete.

**✅ The only reliable progress indicators:**
- `capture-pane` content — test output, command results
- `git diff --stat` — actual code changes
- Spinner / Working indicator — agent actively processing

## 8. Shell Metacharacters in Messages

**❌ Sending messages with `<`, `>`, `|`, `$()`, backticks:**

```bash
# Even in cursor-agent pane, the underlying shell may interpret these
tmux send-keys -t cursor:0 "Check if result > 0.5" Enter
# Shell may interpret ">" as redirect!
```

**✅ Escape or avoid shell-sensitive characters. Use `\[` and `\]` or rephrase.**

## 9. Selection Menu Using Numbers

**❌ Trying to select option 3 by pressing "3":**
```bash
tmux send-keys -t cursor:0 "3" Enter
# → "3" is typed as text into "Other" input, not selecting option 3
```

**✅ Use arrow keys + Space:**
```bash
tmux send-keys -t cursor:0 Down    # navigate
tmux send-keys -t cursor:0 Space   # toggle
tmux send-keys -t cursor:0 Enter   # submit
```

## 10. Session Gone After Restart

**❌ Blindly recreating a session without checking:**

If the tmux session was manually killed by the user or lost on reboot, creating a new one without asking wastes resources.

**✅ First check, then ask:**
```bash
tmux list-sessions
# If session is gone, ask the user before recreating
```

## 11. Stale Daemon Notifications

After stopping the daemon (`kill`) and cleaning up sessions, 1-2 residual `CURSOR-STOPPED` notifications may still arrive from the OS pipe buffer. These are stale — ignore them if the daemon PID is no longer running.

## 12. Daemon Without Registered Windows

```bash
python3 core/monitor.py daemon --group my-project
# Log shows: total=0
```

The daemon is running but **no windows are registered**. Nothing will be monitored. Always verify `total > 0` after starting the daemon:
```bash
python3 core/monitor.py status --group my-project
```

## 13. The `--model` Parameter Position

```bash
# ✅ CORRECT: --model before "agent"
cursor-agent --model auto agent

# ❌ WRONG: --model after "agent" (silently ignored!)
cursor-agent agent --model auto
```

## Quick Reference: When Things Go Wrong

| Symptom | Most Likely Cause | Try This |
|---------|-------------------|----------|
| Text appears in input bar (↪ prefix) | Enter was swallowed | Send another Enter |
| Command not found error | Wrong pane (shell, not agent) | Check pane_current_command |
| No response from agent | Agent is EXECUTING | Wait, or send Ctrl+C |
| Daemon no output | No panes registered | Run `monitor.py list` |
| Percentage not moving | Context usage, not progress | Check capture-pane content |
| Agent shows `Run Everything` | It's a status flag, not a button | Send a message |
| Session missing after restart | User or reboot killed it | Ask before recreating |
