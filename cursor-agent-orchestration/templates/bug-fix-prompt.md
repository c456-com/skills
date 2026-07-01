# Bug Fix Prompt Template

Use this template when delegating a bug fix to a Cursor Agent. Always include reproduction steps and expected behavior.

```markdown
## Bug: [Short Description]

### Symptoms
[What the user sees or experiences — include error messages]

### Reproduction
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen instead]

### Actual Behavior
[What currently happens]

### Environment
- Commit/branch: [e.g., develop at abc1234]
- Data scope: [e.g., All stocks or Only specific ones]
- CLI flags used: [e.g., --layers L1 --window ...]

### Root Cause Analysis (if known)
[Any clues about the root cause]

### Fix Checklist
1. [ ] Identify root cause
2. [ ] Implement fix
3. [ ] Add regression test
4. [ ] Verify fix with reproduction steps
5. [ ] Run existing test suite

### Related Files
- [Path to likely file]
```
