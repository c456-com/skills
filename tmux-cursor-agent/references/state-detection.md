# State Detection Reference

## EXECUTING signals (agent is working)

| Signal | Example | Pattern |
|--------|---------|---------|
| Braille spinner | `⠠⠛` `⠘⠤` | Unicode U+2800-U+28FF in activity region |
| Status keyword | `Working` `Reading` `Editing` `Running` | Regex match in activity region |
| Background tasks | `3 background tasks` | `N background tasks?` regex |
| Progress | `progress: 120/500` | `progress:\d+/\d+` |

## STOPPED reasons (agent is idle)

| Reason | Meaning | Detection |
|--------|---------|-----------|
| `idle` | Normal idle, awaiting input | No activity signals |
| `needs_approval` | Command approval prompt | `Run this command?` visible |
| `needs_input` | Plan mode question | `Question N of M` or `Enter to submit` |
| `task_done` | Task appears complete | `All tests passed` / `✅` |
| `exited` | Exit confirmation | `Press Ctrl+C again to exit` |
| `user_draft` | Unsubmitted text in input | Non-placeholder `→ text` |
| `empty` | No pane content | Capture returned empty |

## Don't misinterpret

| UI Element | Actual Meaning |
|-----------|----------------|
| `→ Add a follow-up` | Input box placeholder (empty). NOT idle signal. |
| `Auto · 84.8%` | Context window usage. NOT task progress. |
| `Run Everything` | Permission mode flag. NOT a button/error. |
| `N tasks` | Compass suggestion count. Agent awaiting next message. |
