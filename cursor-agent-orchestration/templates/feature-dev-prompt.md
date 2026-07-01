# Feature Development Prompt Template

Use this template when delegating a feature development task to a Cursor Agent (Dev role). Focus on **what** to achieve, not **how** to implement it.

```markdown
## Task: [Feature Name]

### Objective
[One paragraph describing what the feature does and why it's needed]

### Specification
- File: `path/to/spec-or-design-doc` (if available)
- Key requirements:
  1. [Requirement 1]
  2. [Requirement 2]
  3. [Requirement 3]

### Acceptance Criteria
1. [ ] [Criterion 1]
2. [ ] [Criterion 2]
3. [ ] [Criterion 3]

### Constraints
- [Constraint 1]
- [Constraint 2]

### Verification
- Run: `make ci-quick` or `pytest path/to/tests`
- Manual: [any manual verification steps]
```
