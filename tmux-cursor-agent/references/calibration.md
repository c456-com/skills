# Calibration & Test Fixtures

The state detection engine (`core/watch.py`) is tested against a library of captured tmux pane snapshots (fixtures) that cover known agent UI states. This ensures detection accuracy doesn't regress when the regex patterns are modified.

## Fixture Directory

```
fixtures/calibrate/
├── ground-truth.json        ← Maps each fixture name to expected state ("executing"/"stopped")
├── <state>-<fixture>.txt    ← Captured tmux pane content (last 40 lines)
└── meta/                    ← Capture metadata (JSON)
```

## Fixture Naming Convention

`{mode}-{state}{sequence}[optional-suffix].txt`

| Part | Values | Meaning |
|------|--------|---------|
| mode | `auto`, `plan`, `ask`, `debug`, `boot` | Agent mode when captured |
| state | `executing` (E), `stopped` (S) | Expected state |
| seq | `01`, `02`, `03` | Sequence within same mode/state |

## Running Regression

```bash
# From project root
python3 -m core.watch --test-fixtures --fixtures-dir fixtures/calibrate/
→ PASS 19/19 passed, 0 failed

# Or via shell script
bash scripts/test-cursor-watch-fixtures.sh
```

## Adding a New Fixture

1. Set up a cursor-agent in a known state
2. Capture the pane:
   ```bash
   tmux capture-pane -t cursor:0 -p -S -40 > fixtures/calibrate/<name>.txt
   ```
3. Add an entry to `ground-truth.json`:
   ```json
   "<name>": "executing" | "stopped"
   ```
4. Run regression to verify it passes

## What Fixtures Cover

| State | Examples |
|-------|----------|
| **auto executing** | Think spinner (`⠠⠛`), "Working" text, "Reading" text |
| **auto stopped** | Idle, `→ Add a follow-up`, user draft text in input |
| **plan stopped** | Plan mode idle, question prompt (`Question N of M`), "Ready to build" |
| **ask executing** | Ask mode reading |
| **debug executing** | Debug mode analyzing |
| **boot stopped** | Fresh session after startup |

## Calibration Scripts

Located in `scripts/`:

- **`calibrate-capture.sh`** — Capture a tmux pane as a fixture with metadata
- **`calibrate-cursor-states.sh`** — Interactive walkthrough to generate fixtures for all states
- **`calibrate-plan-question.sh`** — Capture the Plan mode question UI specifically
- **`test-cursor-watch-fixtures.sh`** — Run regression against all fixtures

## When to Recalibrate

- After modifying regex patterns in `core/watch.py` (especially `ACTIVITY_RE`, `NEEDS_INPUT_RE`, `TASK_DONE_RE`)
- When Cursor releases an agent UI update that changes status bar text or spinner characters
- When adding support for a new agent mode (e.g. a new `SESSION_RE` pattern)

The calibration harness creates a sandbox tmux session (`cursor-calibrate`) that runs cursor-agent in `/tmp/cursor-calibrate-sandbox` — safe to run without affecting real projects.
