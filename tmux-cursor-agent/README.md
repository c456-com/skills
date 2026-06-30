# tmux-cursor-agent

> **Control and monitor Cursor AI agents through tmux — detect states, send messages, build automation.**

A toolkit for orchestrating [Cursor](https://cursor.com) AI coding agents via tmux sessions. Designed for AI assistants (like Hermes Agent) and automation scripts that need to:

- **Launch** cursor-agent in a tmux pane
- **Detect** whether the agent is working (EXECUTING) or idle (STOPPED)
- **Send** messages to the agent with a reliable four-step protocol
- **Cancel** execution (Ctrl+C) or clear input (Escape)
- **Monitor** multiple agents via a Python polling daemon

## Quick Start

```bash
# 1. Create a tmux session and start cursor-agent
tmux new-session -d -s cursor -n my-agent -c /path/to/project
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter

# 2. Wait for it to boot, then check state
python3 core/watch.py cursor 0 --debug

# 3. Send a message (four-step protocol)
tmux capture-pane -t cursor:0 -p -S -5       # verify idle
tmux send-keys -t cursor:0 "Implement feature X"     # no Enter yet!
sleep 2
tmux send-keys -t cursor:0 Enter                     # now press Enter
sleep 3
tmux capture-pane -t cursor:0 -p -S -5               # verify sent

# 4. Cancel if stuck
tmux send-keys -t cursor:0 C-c                       # Ctrl+C to cancel
tmux send-keys -t cursor:0 Escape                    # Esc to clear input
```

## What's Inside

```
tmux-cursor-agent/
├── core/                    # Python + shell tools
│   ├── watch.py             # State detection engine
│   ├── read.py              # Adaptive pane reading
│   ├── monitor.py           # Polling daemon CLI
│   ├── registry.py          # State file management
│   ├── monitor_log.py       # Structured logging
│   └── cursor-watch-lib.sh  # Shell helpers
├── docs/
│   ├── 01-quickstart.md
│   ├── 02-session-lifecycle.md
│   ├── 03-state-detection.md
│   ├── 04-messaging-protocol.md
│   ├── 05-monitoring-daemon.md
│   └── 06-pitfalls.md
├── fixtures/calibrate/      # State detection test fixtures
├── scripts/                 # Calibration & test scripts
├── templates/               # Prompt templates
├── SKILL.md                 # Hermes Agent skill definition
├── LICENSE                  # MIT
└── README.md
```

## Core Concepts

### State Detection

The state detection engine (`core/watch.py`) captures the bottom lines of a cursor-agent tmux pane and classifies two states:

| State | Meaning |
|-------|---------|
| **EXECUTING** | Agent is working — spinner, `Working`/`Reading`/`Editing` visible, background tasks running |
| **STOPPED** | Agent is idle — no activity indicators, awaiting input |

STOPPED is further classified by reason:
- `idle` — normal idle, waiting for input
- `needs_approval` — command approval prompt (`Run this command?`)
- `needs_input` — Plan mode question or user input required
- `task_done` — task appears complete
- `exited` — agent is exiting (`Press Ctrl+C again to exit`)

### Four-Step Messaging Protocol

The only reliable way to send messages to a cursor-agent pane:

```
1. capture-pane  → verify agent is STOPPED and input box is clean
2. send-keys     → type the message (NO Enter)
3. sleep 2       → wait for tmux to buffer the text
4. send-keys Enter → submit, then capture-pane to verify
```

### Monitoring Daemon

For long-running scenarios, `core/monitor.py daemon` polls registered panes every 15s and emits `CURSOR-STOPPED` notifications when agents transition from EXECUTING to STOPPED.

```bash
# Register a pane for monitoring
python3 core/monitor.py group-create default --label "My Group"
python3 core/monitor.py add --group default cursor 0 --label "Dev Agent"

# Start the daemon (background)
python3 core/monitor.py daemon --group default
```

## Requirements

- **tmux** ≥ 3.2
- **Python** ≥ 3.10 (stdlib only — no external dependencies)
- **cursor-agent** CLI installed and on PATH

## License

MIT
