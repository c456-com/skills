### `$(TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z')` | <Role> | agent=<agent-id>

**Skills used:** <skill1>, <skill2>

**Read:**
- `docs/superpowers/comms/<feature>.md` — <entry timestamp> <Role> entry
- `docs/superpowers/specs/<feature>.md`
- `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`
- <other docs>

**Said / Decided:**
- <Decision 1>
- <Decision 2>
- <conclusion tags: APPROVED / ARCH_PASS / DATA_PASS / etc.>

**Artifacts:** (if applicable)
- `path/to/file1`
- `path/to/file2`

**Verification already executed:** (Dev → Arch handoff only)
| # | Command / Scope | Result | Time | Arch Need Re-run? |
|---|-----------------|--------|------|-------------------|
| 1 | `make ci` | PASS | ~Xmin | No |
| 2 | Pytest unit (N tests) | N passed | ~Xs | No |

**Handoff:**
- **Target:** <Role Name> (<Code>)
- **Address:** `docs/superpowers/comms/<feature>.md` (this entry), `docs/...` (paths)
- **Task:** <What the next role should do>

**Blockers:** <none or description>
