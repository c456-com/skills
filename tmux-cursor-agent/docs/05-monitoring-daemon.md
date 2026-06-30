# Monitoring Daemon

The monitoring daemon (`core/monitor.py`) is a polling service that watches registered cursor-agent panes and emits notifications when agents transition from EXECUTING to STOPPED.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  monitor.py                      │
│                                                  │
│  daemon --group default                          │
│       │                                          │
│       │  every 15s                               │
│       ▼                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ pane 1   │  │ pane 2   │  │ pane 3   │       │
│  │ (cursor:0)│  │ (cursor:1)│  │ (cursor:2)│      │
│  └──────────┘  └──────────┘  └──────────┘       │
│       │                                          │
│       ▼                                          │
│  watch.py captures → detects state               │
│       │                                          │
│       ▼                                          │
│  Log output: CURSOR-STOPPED:group:sess:win:reason │
│                                                 │
│  stdout → consumed by parent process             │
│  (e.g., watch_patterns in Hermes)               │
└─────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Create a monitoring group and add panes
python3 core/monitor.py group-create my-project --label "My Project"
python3 core/monitor.py add --group my-project cursor 0 --label "Dev Agent"
python3 core/monitor.py add --group my-project cursor 1 --label "Review Agent"

# 2. Start the daemon
python3 core/monitor.py daemon --group my-project

# 3. In another terminal, see notifications
# CURSOR-STOPPED:my-project:cursor:0:idle
# CURSOR-STOPPED:my-project:cursor:1:needs_approval
# CURSOR-STOPPED:my-project:cursor:0:task_done
```

## CLI Reference

### Group Management

```bash
# Create a group
python3 core/monitor.py group-create <name> [--label "Description"]

# Remove a group (deletes all state files)
python3 core/monitor.py group-remove <name>

# List all groups (or a specific group's monitors)
python3 core/monitor.py list [--group <name>]
```

### Monitor Management

```bash
# Register a pane for monitoring
python3 core/monitor.py add --group <name> <session> <window> [--label "Description"]

# Remove a pane (by session:window or by label)
python3 core/monitor.py remove --group <name> <session>:<window>

# Check status of a group
python3 core/monitor.py status --group <name>
```

### Pending State

When a notified pane needs human attention but can't be handled immediately, mark it as pending:

```bash
# Mark as pending
python3 core/monitor.py set-pending --group <name> <session>:<window> <reason> "<summary>"

# Clear pending
python3 core/monitor.py clear-pending --group <name> <session>:<window>
```

### Daemon

```bash
# Start the daemon
python3 core/monitor.py daemon --group <name>

# One-shot (single poll, then exit)
python3 core/monitor.py daemon --group <name> --once

# Debug mode (verbose per-tick output)
python3 core/monitor.py daemon --group <name> --debug

# Custom log file
python3 core/monitor.py daemon --group <name> --log-file /tmp/my-monitor.log
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CURSOR_MONITOR_INTERVAL` | `15` | Polling interval in seconds |
| `CURSOR_MONITOR_STATUS_INTERVAL` | `600` | Status heartbeat interval |
| `CURSOR_MONITOR_LINES` | `15` | Lines to capture per poll |
| `CURSOR_MONITOR_DIR` | `~/.hermes/logs/cursor-monitors/` | State/log directory |
| `CURSOR_MONITOR_LOG` | `{dir}/cursor-monitors--{group}.log` | Log file path override |
| `CURSOR_MONITOR_STATE_PREFIX` | `""` | Optional file name prefix for multi-profile |

## Notification Format

```
CURSOR-STOPPED:<group>:<session>:<window>:<reason>
```

Example notification lines:

```
CURSOR-STOPPED:default:cursor:0:idle
CURSOR-STOPPED:my-project:cursor:1:needs_approval
CURSOR-STOPPED:my-project:cursor:2:needs_input
CURSOR-STOPPED:default:cursor:3:task_done
CURSOR-STOPPED:default:cursor:0:exited
```

Additional log lines:

```
CURSOR-MONITOR-START group=default pid=12345 interval=15s
CURSOR-MONITOR-WATCH group=default session=cursor:0 state=executing reason=task_done
CURSOR-MONITOR-TICK group=default ok=2 skipped=0 total=2
CURSOR-MONITOR-STATUS:default:monitors=2:ok=2:skipped=0:daemon_pid=12345
CURSOR-MONITOR-SKIP group=default session=cursor:2 reason=session_missing
CURSOR-MONITOR-STOP group=default pid=12345
```

## Notification Delivery Patterns

### Pattern 1: SSH + grep (simple)

```bash
python3 core/monitor.py daemon --group my-project 2>&1 | grep --line-buffered "CURSOR-STOPPED:"
```

### Pattern 2: Hermes Agent watch_patterns

When the daemon is started via Hermes `terminal()`:

```python
terminal(
    command="python3 core/monitor.py daemon --group my-project",
    background=True,
    watch_patterns=["CURSOR-STOPPED:"]
)
```

Each match triggers the agent to process the notification.

### Pattern 3: Process subscription

```bash
# Start daemon
python3 core/monitor.py daemon --group my-project &
PID=$!

# Periodically read its output
tail -f ~/.hermes/logs/cursor-monitors/cursor-monitors--my-project.log
```

## Running as a Systemd Service

```ini
[Unit]
Description=tmux-cursor-agent monitor (my-project)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/tmux-cursor-agent/core/monitor.py daemon --group my-project
Restart=always
RestartSec=10
Environment=CURSOR_MONITOR_DIR=/var/lib/cursor-monitors
User=your-user

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

### Daemon starts but no notifications

```bash
# Check if any panes are registered
python3 core/monitor.py list --group my-project

# Verify total > 0 — if total=0, no panes registered!
# Expected: "monitor1  cursor:0  Dev Agent"
```

### Session missing warnings

```
CURSOR-MONITOR-SKIP group=my-project session=cursor:2 reason=session_missing
```

The tmux session `cursor` does not exist or window `2` was destroyed. Remove the stale registration:

```bash
python3 core/monitor.py remove --group my-project cursor:2
```

### Boot notification burst

When starting the daemon on a group where windows are already STOPPED, you'll get one notification per window immediately. This is expected — those are current-state notifications, not new transitions.
