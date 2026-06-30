# Session Lifecycle

Managing tmux sessions for cursor-agent: create, verify, communicate, destroy.

## Creating a Session

### Basic Session

```bash
# Single window session
tmux new-session -d -s cursor -n agent -c /path/to/project

# Named session for specific task
tmux new-session -d -s cursor-my-feature -n dev -c /path/to/project
```

### Multi-Window Session (Multiple Agents)

```bash
# Create session with first window
tmux new-session -d -s cursor -n agent-1 -c /path/to/project

# Add more windows for additional agents
tmux new-window -t cursor -n agent-2 -c /path/to/project
tmux new-window -t cursor -n monitor -c /path/to/project
```

## Starting cursor-agent

```bash
# Send cursor-agent start command to a specific pane
# Window index 0, pane 0 (default)
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter

# IMPORTANT: Wait for boot before sending messages
sleep 4

# Verify boot complete
tmux capture-pane -t cursor:0 -p -S -3
```

### Detecting cursor-agent in a Pane

Before sending any message, verify the pane is actually running cursor-agent (not a plain shell):

```bash
# Check what command is running in the pane
tmux list-windows -t cursor -F '#{window_index}: #{window_name} - #{pane_current_command}'

# Expected output:
#   0: agent-1 - cursor-agent    ← running cursor-agent
#   1: agent-2 - cursor-agent    ← running cursor-agent
#
# If you see "zsh", "bash", "fish" — it's a plain terminal, NOT running cursor-agent
```

## Checking Session Status

```bash
# List all tmux sessions
tmux list-sessions

# List windows in a specific session
tmux list-windows -t cursor -F '#{window_index}: #{window_name}'

# Check what's in a specific pane (last 5 lines)
tmux capture-pane -t cursor:0 -p -S -5
```

## Stopping cursor-agent

### Graceful Exit

```bash
# Send /exit command in the agent's input
tmux send-keys -t cursor:0 "/exit" Enter

# The agent will save its session and print a resume ID
# You'll see: "Session saved: abc123  Resume with: cursor-agent resume abc123"
```

### Hard Stop (Force Kill)

```bash
# If the agent is stuck and /exit doesn't work:
# First Ctrl+C to cancel current operation
tmux send-keys -t cursor:0 C-c
sleep 1

# Then Ctrl+C again to trigger exit
tmux send-keys -t cursor:0 C-c
sleep 1

# If still not responding, kill the pane
tmux kill-pane -t cursor:0
```

## Destroying Sessions

```bash
# Kill a single window (and its agent)
tmux kill-window -t cursor:0

# Kill the entire session (all windows)
tmux kill-session -t cursor

# Verify cleanup
tmux list-sessions
```

## Quick Reference Card

| Action | Command |
|--------|---------|
| Create session | `tmux new-session -d -s cursor -n name -c /path` |
| Add window | `tmux new-window -t cursor -n name -c /path` |
| Start agent | `tmux send-keys ... "cursor-agent agent" Enter` |
| Check process | `tmux list-windows -t cursor -F '#{pane_current_command}'` |
| Read pane | `tmux capture-pane -t cursor:N -p -S -M` |
| Send text | `tmux send-keys -t cursor:N "text"` |
| Send Enter | `tmux send-keys -t cursor:N Enter` |
| Send Ctrl+C | `tmux send-keys -t cursor:N C-c` |
| Send Escape | `tmux send-keys -t cursor:N Escape` |
| Kill window | `tmux kill-window -t cursor:N` |
| Kill session | `tmux kill-session -t cursor` |
