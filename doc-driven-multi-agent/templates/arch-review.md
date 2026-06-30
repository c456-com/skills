# Arch Review: <Feature>

> **Verdict:** ARCH_PASS | ARCH_FAIL
> **Reviewer:** Architect (Arch)
> **Scope:** <commit/PR/worktree>
> **Spec:** docs/superpowers/specs/<feature>.md
> **make ci evidence:** PASS (paste summary or reference comm entry)

## Spec Alignment

- <Item 1: aligned?>
- <Item 2: aligned?>

## Architecture & Concurrency

- <Module boundaries OK?>
- <Concurrent write paths safe?>
- <Storage layout follows conventions?>

## Testing & Maintainability

- <Tests meaningful?>
- <Dead code, duplication?>
- <Naming & structure?>

## Direct Edits (if any)

- `path:line` — <change description>

## Handoff

- **Target:** <Analyst (PASS) | Dev (FAIL)>
- **Address:** `docs/superpowers/reviews/arch-review-<feature>.md` (this), `docs/superpowers/comms/<feature>.md`
- **Task:** <PASS: Analyst verify | FAIL: Dev rework per list>
