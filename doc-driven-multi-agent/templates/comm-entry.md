### `$(TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z')` | <Role> | agent=<agent-id>

**Skills used:** <skill1>, <skill2>

**Read:**
- `docs/superpowers/comms/<feature>.md` — <entry timestamp> <Role> entry
- `docs/superpowers/specs/<feature>.md`
- `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`
- <其他文档>

**Said / Decided:**
- <决策 1>
- <决策 2>
- <结论标签：APPROVED / ARCH_PASS / DATA_PASS / 等>

**Artifacts:**（如适用）
- `path/to/file1`
- `path/to/file2`

**Verification already executed:**（仅 Dev → Arch handoff 使用）
| # | Command / Scope | Result | Time | Arch Need Re-run? |
|---|-----------------|--------|------|-------------------|
| 1 | `make ci` | PASS | ~Xmin | No |
| 2 | Pytest unit (N tests) | N passed | ~Xs | No |

**Handoff:**
- **Target:** <Role Name> (<Code>)
- **Address:** `docs/superpowers/comms/<feature>.md`（当前 entry）, `docs/...`（路径）
- **Task:** <下一个角色要做什么>

**Blockers:** <无，或填写说明>
