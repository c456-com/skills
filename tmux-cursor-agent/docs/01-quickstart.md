# Quick Start Guide

## Prerequisites

```bash
# Install tmux (if not already installed)
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt-get install tmux

# Verify cursor-agent is available
which cursor-agent
cursor-agent --help
```

## 1. Create a tmux Session

```bash
# Create a new session named "cursor" with a single window
tmux new-session -d -s cursor -n my-task -c /path/to/your/project

# Verify it was created
tmux list-sessions
```

## 2. Start cursor-agent

```bash
# Send the start command to the tmux pane (window index 0)
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter

# Wait for the agent to boot up (3-5 seconds)
sleep 4

# Check the pane content to confirm it's running
tmux capture-pane -t cursor:0 -p -S -5
```

You should see the cursor-agent welcome message like `→ Plan, search, build anything`.

## 3. Check Agent State

```bash
# Quick state check using the watch utility
python3 core/watch.py cursor 0 15 --debug

# Expected output shows:
# EXECUTING=True/False  reason=idle/task_done/etc
```

## 4. Send Your First Message

```bash
# Step 1: Verify agent is idle
tmux capture-pane -t cursor:0 -p -S -5

# Step 2: Type the message (NO Enter!)
tmux send-keys -t cursor:0 "Refactor the database schema to use UUIDs for primary keys"

# Step 3: Wait for tmux to buffer
sleep 2

# Step 4: Submit
tmux send-keys -t cursor:0 Enter

# Step 5: Verify it was sent
sleep 3
tmux capture-pane -t cursor:0 -p -S -5
# You should see the message in the conversation history and "Working" spinner
```

## 5. Cancel or Interrupt

```bash
# Cancel current execution (like Ctrl+C in terminal)
tmux send-keys -t cursor:0 C-c

# Clear input box (Escape — cancel unsubmitted text)
tmux send-keys -t cursor:0 Escape

# Force exit cursor-agent
tmux send-keys -t cursor:0 "/exit" Enter
```

## 6. Read Pane Content

```bash
# Last 20 lines
python3 core/read.py capture cursor 0 --lines 20

# 50 lines, skipping the bottom 100 (read older content)
python3 core/read.py capture cursor 0 --lines 50 --offset 100

# Write to a file
python3 core/read.py capture cursor 0 --lines 200 --out /tmp/pane-output.txt
```

## 7. Monitor with Daemon

```bash
# Register the pane
python3 core/monitor.py group-create default --label "My Project"
python3 core/monitor.py add --group default cursor 0 --label "Dev"

# Start daemon (in background)
python3 core/monitor.py daemon --group default &
```

## Next Steps

- Read [Session Lifecycle](02-session-lifecycle.md) for detailed session management
- Read [State Detection](03-state-detection.md) to understand how EXECUTING/STOPPED detection works
- Read [Messaging Protocol](04-messaging-protocol.md) for the full four-step protocol
- Read [Monitoring Daemon](05-monitoring-daemon.md) for daemon configuration
- Read [Pitfalls](06-pitfalls.md) for common mistakes to avoid
