# State Detection

Detecting whether a cursor-agent pane is **EXECUTING** (working) or **STOPPED** (idle) is the core capability of this toolkit.

## How Detection Works

The state detection engine (`core/watch.py`) works by:

1. **Capturing** the bottom N lines of a tmux pane via `capture-pane`
2. **Parsing** the region above the footer/input bar (the "activity region")
3. **Matching** against known activity patterns (braille spinners, status keywords)
4. **Classifying** as EXECUTING or STOPPED, plus a reason for STOPPED

## EXECUTING Signals

The agent is considered **EXECUTING** when any of these appear in the activity region:

| Signal | Example | Pattern |
|--------|---------|---------|
| Braille spinner | `⠠⠛` `⠘⠤` | Unicode U+2800-U+28FF characters in activity region |
| Status keyword | `Working` `Running` `Thinking` `Reading` `Globbing` `Editing` `Waiting` `Reconnecting` | Regex match |
| Background tasks | `3 background tasks` | `N background tasks?` regex |
| Progress indicators | `progress: 120/500` | `progress:\d+/\d+` regex |

### The Activity Region

The activity region is the pane content **above** the footer/input bar. The detection engine strips footer lines (identified by the `→ input` bar, `Auto · N%` status bar, `Run Everything` indicator, and task count line) and then checks the remaining content for EXECUTING signals.

```
Line content above footer...     ← activity region
──────────────────────────
→ Add a follow-up                ← input bar (footer line)
Auto · 45.3%                     ← context status (footer line)
```

## STOPPED States

When no EXECUTING signals are found, the agent is STOPPED. The engine further classifies the reason:

| Reason | Meaning | Detection |
|--------|---------|-----------|
| `idle` | Normal idle, awaiting input | No activity, no special prompts |
| `needs_approval` | Command approval prompt | `Run this command?` or `Run (once) (y)` visible |
| `needs_input` | Plan mode question | `Question N of M` or `Enter to submit, Esc to cancel` |
| `task_done` | Task appears complete | `All tests passed` or `✅` markers |
| `exited` | Exit confirmation | `Press Ctrl+C again to exit` |
| `user_draft` | Unsubmitted user text | Text in input bar that is NOT a placeholder |
| `empty` | No pane content | Capture returned empty string |

### Placeholder vs User Text

The input bar can show two types of content:

- **Placeholder** (empty input): `→ Add a follow-up`, `→ Describe how to revise...`, `→ Plan, search, build anything`
- **User text** (unsubmitted): `→ My feature request...`

Only user text (non-placeholder) is flagged as `user_draft`. Placeholders are treated as empty.

## The Watch CLI

```bash
# Basic usage: check window index 0 in session "cursor"
python3 core/watch.py cursor 0

# More lines for deeper inspection
python3 core/watch.py cursor 0 30

# Debug output shows internal state
python3 core/watch.py cursor 0 15 --debug

# Test with a fixture file (for calibration/testing)
python3 core/watch.py --fixture fixtures/calibrate/auto-executing-E01.txt

# Run regression against all fixtures
python3 core/watch.py --test-fixtures
```

## Output Format

When the agent transitions from EXECUTING to STOPPED, `run_watch()` returns a `WatchResult` with a `notify_line`:

```
CURSOR-STOPPED:cursor:0:idle
```

This line is emitted once per transition — it won't repeat if the agent stays STOPPED (hash-based deduplication prevents re-notification).

## State Transition Tracking

The engine tracks state using three disk files per pane:

| File | Purpose |
|------|---------|
| `{session}-{window}.state` | Last known state: `working`, `idle`, or `held` |
| `{session}-{window}.boot` | Marker file — removed to indicate "not first boot" |
| `{session}-{window}.notify-hash` | MD5 hash of last notified content — prevents re-notify |

The boot file is created on first watch. This means the **first** watch after any interruption will always produce a notification (useful for initial state sync).

## Testing with Fixtures

The `fixtures/calibrate/` directory contains captured tmux pane content covering various agent states:

```bash
# Run the full regression suite
bash scripts/test-cursor-watch-fixtures.sh

# Or directly
python3 core/watch.py --test-fixtures --fixtures-dir fixtures/calibrate/
```

The `ground-truth.json` file maps each fixture name to its expected state (`"executing"` or `"stopped"`). Add new fixtures by capturing pane content and adding an entry to `ground-truth.json`.
