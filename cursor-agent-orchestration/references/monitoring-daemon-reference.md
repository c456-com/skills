# Monitoring Daemon CLI & Architecture

## Architecture Overview

```
state file (~/.hermes/logs/cursor-monitors--<group>.state)
    └── cursor_monitor.py daemon --group <group> (15s polling loop)
            └── cursor_watch.py <session> <window> (per-pane state check)
                    └── tmux capture-pane → check bottom lines for state signals
                            └── stdout: CURSOR-STOPPED:<group>:<session>:<window>:<reason>
                                    └── watch_patterns match → coordinator agent turn
```

## CLI Reference

```bash
export MON="python3 /path/to/cursor_monitor.py"

# Group management
$MON group-create <group> [--label "label"]
$MON group-remove <group>

# Window registration
$MON add --group <group> <session> <window> [--label "label"]
$MON remove --group <group> <target>

# Query
$MON list [--group <group>]
$MON status --group <group>

# Daemon
$MON daemon --group <group> [--debug] [--once]

# Pending state (for human-in-the-loop escalations)
$MON set-pending --group <group> <session>:<window> needs_input "Question summary"
$MON clear-pending --group <group> <session>:<window>
```

## Event Reasons

| Reason | Detection Logic | Meaning |
|--------|----------------|---------|
| `task_done` | Pane transitioned from EXECUTING to STOPPED (spinner disappeared) | Agent finished a message turn |
| `needs_approval` | Bottom lines contain "Run this command?" or approval prompt | Agent is waiting for command approval |
| `needs_input` | Bottom lines contain "Question N of M", "Enter to submit", "Ready to build?" | Agent is waiting for user decision |
| `idle` | Pane is STOPPED but was already STOPPED last poll (no transition) | Ambient idle notification — may be noise |
| `exited` | pane_current_command changed from "cursor-agent" to "zsh"/"bash" | Agent process exited |

## State Persistence

State is stored per-group in a JSON file (default: `~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.state`):

```json
{
  "group": "my-task",
  "label": "Feature X Team",
  "windows": [
    {"session": "cursor-pm-my-task", "window": 0, "label": "PM"},
    {"session": "cursor-dev-my-task", "window": 0, "label": "Dev"}
  ],
  "last_hash": {},
  "pending": null
}
```

## Daemon Lifecycle Verification

```bash
# Start (must be through process management system):
terminal(
  command="exec python3 /path/to/cursor_monitor.py daemon --group my-group",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)

# Verify it's tracking:
process(action='list')
# → verify session_id is present

# Check it sees registered windows:
process(action='poll', session_id="<id>")
# → output must contain "total=N" where N > 0

# If total=0: no windows registered to group. Run add first.
```

## Known Notification Pitfalls

- **Boot burst:** When daemon starts on already-idle windows, it emits immediate CURSOR-STOPPED for each. These are stale — do ONE capture-pane sweep to establish baseline, then ignore.
- **Rapid-fire:** Same agent may emit 3-5 notifications in succession during busy periods. Read latest capture-pane ONCE, handle the most recent meaningful event.
- **Idle noise during execution:** Agent in EXECUTING may briefly show STOPPED between tool calls. If `capture-pane` shows spinner/Working, the "idle" event is noise.
- **Phantom notifications after cleanup:** After killing sessions and daemon, residual stdout from OS pipe buffer may inject 1-2 stale notifications. If daemon PID is gone, ignore.
- **needs_input false positive:** Daemon may fire `needs_input` when pane content hash changes without actual Question UI. Always `capture-pane` to verify.
