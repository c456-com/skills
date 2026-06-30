---
title: Handoff Chat Message Templates (All Roles)
type: reference
status: active
last-reviewed: 2026-06-30
---

# Handoff Chat Message Templates

> **Comm log is the authoritative handoff;** chat blocks are copyable summaries for humans to forward between sessions.

## General Rules

| Rule | Description |
|------|-------------|
| **Comm timestamp** | Run `TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'` before writing entry — never fabricate |
| **First-person opening** | `Hello, I am <Role Name> (<Code>).` — never use "You are PO/Dev…" as the subject |
| **Comm always first** | Sender must have already appended comm (with Handoff three elements) before sending chat block |
| **Receiver procedure** | Confirm role → find comm entry where Target matches → read Address docs → execute Task |
| **Boundary refusal** | Request outside role → refuse (1st/2nd time); 3rd explicit confirmation → `OVERRIDE_ROLE_BOUNDARY` |

### Handoff Three Elements (mandatory in every block)

```markdown
**Handoff:**
- **Target:** <Role Name> (<Code>)
- **Address:** `docs/...` (at least 1 path, including this comm entry)
- **Task:** One/two sentences — what the next role should do
```

### Chat Block Required Fields

| Field | Description |
|-------|-------------|
| Opening | First-person role declaration |
| Please read first | This comm entry + Address paths (in order) |
| Background | Optional, 1–2 sentences of context |
| Please… | Specific task (verb-first) |
| Expected output | Verdict tags, documents, ci/test evidence |
| Note | Comm log requirement; forbidden items |

---

## Boundary Refusal (All Roles)

When a human or previous session asks you to do work **clearly outside your role**:

**1st / 2nd refusal (copyable):**

```markdown
Hello, I am <Role Name> (<Code>).

You are asking me to "<task summary>", which belongs to <Correct Role Name> (<Code>).
This is outside my role authority. **I will not execute this work.**

Correct path:
1. comm Handoff → Target: <Correct Role>
2. Address: <spec/plan/review path>
3. Task: <what that role should do>

Please open a session for <Correct Role>, or ask a human to forward the above Handoff.

If you still insist I do this as <current role>, please confirm explicitly in writing
for the 3rd+ time; after confirmation I'll log `OVERRIDE_ROLE_BOUNDARY` and proceed.
```

**After exceptional execution (comm must include):**

```markdown
**Said / Decided:**
- `OVERRIDE_ROLE_BOUNDARY` — Human confirmed 3rd time for <Code> to do "<task summary>"
- Confirmation text: «…»
```

---

## PM → PO

**Scenario:** Plan ready, request G1.5 design alignment or Dev assignment approval

```markdown
Hello, I am Project Manager (PM). Please do **G1.5 design alignment** or review plan for feature `<feature-slug>`.

**Please read first (in order):**
1. `docs/superpowers/comms/<feature>.md` — latest PM entry
2. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

**Please confirm task scope aligns with product design; if approved, assign Dev (G2).**

**Expected output:** comm `APPROVED` + Handoff three elements → Developer (Dev)
```

---

## PM → Arch

```markdown
Hello, I am Project Manager (PM). Please do **architecture pre-review** for feature `<feature-slug>` (complex task).

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/specs/<feature>.md`
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`

**Please evaluate implementation approach (storage/concurrency/module boundaries).**

**Expected output:** comm `ARCH_PRE_PASS` or modification list + Handoff → Product Owner (PO)
```

---

## PO → PM

```markdown
Hello, I am Product Owner (PO). Feature `<feature-slug>` design is frozen. Please write plan and schedule.

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/specs/<feature>.md` — Status: approved

**Please write plan with tasks, dependencies, and risks; complex tasks mark for Arch pre-review.**

**Expected output:** `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` + comm Handoff
```

---

## PO → Dev

```markdown
Hello, I am Product Owner (PO). Please (Dev) implement feature `<feature-slug>` **Task <N>** (G2 implementation go).

**Please read first (in order):**
1. `docs/superpowers/comms/<feature>.md` — this PO Handoff
2. `docs/superpowers/specs/<feature>.md` — acceptance criteria §…
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — Task <N>
4. Worktree path from PM (check plan meta)

**Please TDD per plan Task <N>; work in worktree only; after completion, Handoff Arch.**

**Expected output:** code + pytest; `make ci` PASS; comm Handoff → Architect (Arch)

**Note:** Do not expand scope; implementation questions go to Arch (not PO).
```

---

## PO → Arch

```markdown
Hello, I am Product Owner (PO). Please do **architecture pre-review** for feature `<feature-slug>` (storage/concurrency/approach).

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/specs/<feature>.md`

**Please assess implementation feasibility; product semantics issues → `ESCALATE_PO`.**

**Expected output:** comm `ARCH_PRE_PASS` or modification suggestions + Handoff
```

---

## Arch → Dev

```markdown
Hello, I am Architect (Arch). Feature `<feature-slug>` code review verdict: **ARCH_FAIL**. Please (Dev) rework.

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/reviews/arch-review-<feature>-YYYY-MM-DD.md` — rework checklist

**Please TDD fix per review checklist; `make ci` pass before re-submitting to me.**

**Expected output:** fixed code + comm Handoff → Architect (Arch)

**Note:** If product semantics or ADR changes needed, stop coding and wait for PO/Arch doc updates.
```

---

## Arch → Analyst

```markdown
Hello, I am Architect (Arch). Feature `<feature-slug>` code review verdict: **ARCH_PASS**. Please (Analyst) do independent data verification.

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/reviews/arch-review-<feature>-YYYY-MM-DD.md`
3. `docs/superpowers/specs/<feature>.md` — acceptance criteria

**Please run independent verification per spec (3-phase or as specified); do NOT modify product code.**

**Expected output:** `reviews/<feature>-analyst-*.md` + comm `DATA_PASS` / `DATA_FAIL`
```

---

## Arch → PO

```markdown
Hello, I am Architect (Arch). Feature `<feature-slug>` has **product semantics / acceptance criteria** issues. Need you (PO) to decide (ESCALATE_PO).

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/specs/<feature>.md`
3. `docs/superpowers/reviews/arch-review-*.md` (if any)

**Please clarify or update spec; comm `APPROVED` before Dev can proceed.**

**Expected output:** Updated spec or decision doc + comm Handoff → Dev / PM
```

---

## Dev → Arch

```markdown
Hello, I am Developer (Dev). Feature `<feature-slug>` **Task <N>** is complete. Please (Arch) code review.

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry (with Verification table)
2. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — Task <N>
3. Code paths: (list changed files)

**Dev has already executed tests (please do NOT re-run full CI):**
- (Copy from comm Verification table: command, result, duration)
- Not run: (theory cases, full backtest → Analyst)

**Please static review implementation + spec alignment; sign `ARCH_PASS` / `ARCH_FAIL`.**

**Expected output:** arch-review doc + comm Handoff → Analyst (PASS) or Dev (FAIL)
```

---

## Analyst → Dev

```markdown
Hello, I am Data Analyst (Analyst). Feature `<feature-slug>` data verification verdict: **DATA_FAIL**. Please (Dev) fix per bug list.

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/reviews/<feature>-analyst-YYYY-MM-DD.md` — bug list + reproduction steps

**Please fix data bugs per review; do NOT modify spec. After fix, Handoff Arch for re-review.**

**Expected output:** fixed code + pytest/ci + comm Handoff → Architect (Arch)
```

---

## Analyst → PO

```markdown
Hello, I am Data Analyst (Analyst). Feature `<feature-slug>` data verification verdict: **DATA_PASS**. Please (PO) do product acceptance (G3).

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/reviews/<feature>-analyst-YYYY-MM-DD.md`
3. `docs/superpowers/specs/<feature>.md` — acceptance criteria

**Please review analysis report against spec; sign `PRODUCT_ACCEPTED` for closure.**

**Expected output:** comm `PRODUCT_ACCEPTED` + Handoff → Project Manager (PM) for archiving
```

---

## PO → PM (Product Acceptance)

```markdown
Hello, I am Product Owner (PO). Feature `<feature-slug>` product acceptance: **PRODUCT_ACCEPTED**. Please (PM) archive closure (G4).

**Please read first:**
1. `docs/superpowers/comms/<feature>.md` — this entry
2. `docs/superpowers/reviews/` (Arch + Analyst chain)
3. `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` — confirm all `[x]`

**Please confirm plan all green, reviews complete, daily updated. Initiate G4 closure.**

**Expected output:** comm `COMMIT_REQUEST` → PO, Dev, Analyst
```

---

## Default Handoff Direction Quick Reference

| From | Default To | Template Section |
|------|-----------|-----------------|
| PM | PO / Arch | PM → PO · PM → Arch |
| PO | PM / Dev / Arch | PO → PM · PO → Dev · PO → Arch |
| Arch | Dev / Analyst / PO | Arch → Dev · Arch → Analyst · Arch → PO |
| Dev | Arch | Dev → Arch |
| Analyst | Dev / PO | Analyst → Dev · Analyst → PO |
