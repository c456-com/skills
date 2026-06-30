---
name: doc-driven-multi-agent
category: autonomous-ai-agents
tags: [multi-agent, coordination, document-driven, handoff, roles, SOP, workflow, protocol]
description: "Platform-agnostic document-driven multi-agent coordination protocol — role-based SOPs, handoff protocol (三要素: target/address/task), gates G0–G4, boundary enforcement, and session lifecycle. Works with any AI agent platform (Cursor, Claude Code, Copilot, Gemini, Hermes)."
triggers:
  - 启动/重启多代理协作 session 时
  - 需要定义 AI Agent 角色及其职权边界时
  - 角色间需要通过文档 handoff 交接工作时
  - 代理不确定自己的角色或收到越界请求时
  - 设计/实现/验收流程需要通过 G0–G4 门禁控制时
related_skills: [cursor-agent-orchestration, opencode, hermes-agent]
---

# Document-Driven Multi-Agent Coordination Protocol

Coordinate multiple AI agents through **document-driven handoffs** rather than chat-based communication. Every decision, task transfer, and review is recorded in project documents forming an auditable chain of custody.

> **Core rule:** No document = no handoff = no work start.

---

## Why Document-Driven, Not Chat-Driven

| Approach | Problem |
|----------|---------|
| Chat handoff | Message is buried in conversation history; next agent can't find it |
| Session-only decisions | Lost when session ends or model switches |
| Verbal task assignment | Ambiguous; no audit trail |
| **Document-driven** | Every handoff, decision, and review has a permanent file path |

This protocol emerged from running 4–5 AI agent roles (PM, PO, Architect, Developer, Analyst) on a single codebase where each agent operates in its own isolated session. The key insight: **agents don't talk to each other; they write files for each other.** The comm log (communication log) serves as the shared memory that persists across sessions, models, and platforms.

---

## Document Chain (Source of Truth Hierarchy)

```
AGENTS.md                        ← Entry point (mandatory checklist for every agent)
  └── WORKFLOW.md                ← Canonical workflow (this protocol)
        └── GOALS.md             ← Product/project goals
              └── spec           ← What to build + acceptance criteria
                    ├── comm     ← Communication log (decisions, handoffs)
                    ├── plan     ← Task breakdown with checkboxes
                    └── code     ← Worktree implementation + tests
                          └── review  ← Verification evidence
                                └── daily  ← Engineering daily log
```

| Document | Path Convention | Purpose | Maintainer |
|----------|----------------|---------|------------|
| Entry point | `<root>/AGENTS.md` | Mandatory session checklist | All agents read |
| Workflow | `docs/ops/WORKFLOW.md` | Full protocol (this document) | All agents read |
| Goals | `docs/product/GOALS.md` | High-level objectives | PO |
| Spec | `docs/superpowers/specs/<feature>.md` | What to build + acceptance criteria | PO |
| **Comm Log** | `docs/superpowers/comms/<feature>.md` | **Decisions, handoffs, conversation history** | **All agents append** |
| Plan | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | Task items with checkboxes | PM |
| Review | `docs/superpowers/reviews/<feature>-YYYY-MM-DD.md` | Verification evidence | Arch / Analyst |
| Daily Log | `docs/ops/daily/YYYY-MM-DD.md` | Daily engineering summary | All agents |

**Iron rules:**
- **Comm Log** = conversation & decision SoT (single source of truth)
- **Spec / Plan** = requirements & task SoT
- **Reviews** = verification SoT
- Chat alone is NEVER sufficient for handoff or decision recording

---

## Five Role Model

The protocol defines five distinct roles with **strict responsibilities and hard boundaries**. Every agent must know its role before starting work. If unsure, the agent MUST stop and ask.

| Role | Code | Responsibility | Writes Code? | Key Deliverables |
|------|------|---------------|:------------:|------------------|
| **Project Manager** | `PM` | Task planning, worktree lifecycle, gate G4 closure | **No** | plan, comm, worktree management |
| **Product Owner** | `PO` | Product definition, spec writing, acceptance signing | **No** | spec, acceptance decisions, theory refs |
| **Architect** | `Arch` | Architecture decisions (ADR), code review, minor direct edits | **Limited** | ADR, arch-review, minor code tweaks |
| **Developer** | `Dev` | **Only code writer** — implementation + tests | **Yes** | code, tests, verification evidence |
| **Data Analyst** | `Analyst` | Data verification, bug reports, acceptance evidence | **No** | review reports, DATA_PASS/FAIL |

### Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| PM | Plans, schedules, worktree create/merge/cleanup | Write any product code, run data analysis, code review |
| PO | Specs, product decisions, acceptance, theory references | Write code, modify architecture ADRs |
| Arch | ADRs, code review, small direct edits (naming/typo/bug) | Modify product spec/definitions without PO; take full Dev tasks |
| Dev | Code + tests in worktree, implementation docs | Modify spec, PO docs, ADRs; expand scope without approval |
| Analyst | Data verification, bug reports with reproduction steps | Modify product code, specs, or architecture docs |

### Escalation Chain

```
Dev implementation question / blocker ──→ Arch
Arch product semantics issue ──→ PO (ESCALATE_PO)
Arch schedule/scope impact ──→ PM (ESCALATE_PM)
Analyst data bug ──→ Dev (code) | Arch (architecture) | PO (product definition)
```

**Dev must NEVER bypass Arch to ask PO for spec changes.** All communication flows through the chain.

---

## Handoff Protocol (三要素 — Three Mandatory Fields)

This is the **core mechanism** of the protocol. Every task transfer between roles must include three elements written as a structured block in the comm log:

| Element | Field Name | Requirement |
|---------|-----------|-------------|
| **Target** | `对象` | Role full name + code, e.g., `Developer (Dev)` |
| **Address** | `地址` | Repository paths (this comm entry, spec, plan, review, code) — at least 1 |
| **Task** | `事项` | One/two sentences describing what the next role should do |

### Standard Handoff Block

```markdown
**Handoff:**
- **Target:** Developer (Dev)
- **Address:** `docs/superpowers/comms/<feature>.md` (this entry), `docs/superpowers/specs/<feature>.md`
- **Task:** Implement plan Task 3.2 per spec §4 acceptance criteria; work in worktree `.worktrees/feat-<topic>`
```

### Invalid Handoffs (next agent MUST refuse)

- Handoff exists only in chat/agent reply — not in comm log
- Handoff in comm log but missing target, address, OR task (any one absent → BLOCKED)
- Decision only exists in session conversation, not in comm/spec/plan/review
- Rework items only in PR comments, not registered in comm entry
- Using `@role` or verbal notification instead of **appending comm log**

### Receiving a Handoff (pre-work checklist)

The next agent, before starting work, MUST:

1. Open the comm log and find the latest entry where **Target** matches the agent's current role
2. Verify all three fields (target, address, task) are present; if not → `BLOCKED: invalid handoff`
3. Read every document listed in `Address` and `Read:` fields
4. Declare read list in comm or session reply

---

## Gates (G0–G4)

The protocol defines five gates that control the progression of work. No work proceeds past a gate without the gate conditions being met:

| Gate | Name | Owner | Condition |
|------|------|-------|-----------|
| **G0** | Initiation | PM + PO | `comms/<feature>.md` + spec placeholder exist (or `Status: exploring`) |
| **G1** | Design Freeze | PO | spec status ≠ `draft`; comm has `APPROVED` from PO |
| **G2** | Implementation Go | PO | plan exists; PO comm assigns Dev; complex tasks need Arch pre-review pass |
| **G3** | Product Acceptance | PO | Analyst `DATA_PASS` + review document; PO signs `PRODUCT_ACCEPTED` |
| **G4** | Closure | PM | All three parties `COMMIT_DONE`; merge + worktree cleanup; `TASK_CLOSED` |

**Exception:** ≤3 file changes, or comm marked `EXCEPTION: trivial` + file list → may skip G1/G2.

---

## Session Protocol (every agent must follow)

### Before Starting (Checklist)

- [ ] If role unknown → **stop and ask** what role you are assigned; read role SOP after confirmation
- [ ] Read AGENTS.md → WORKFLOW.md (this document) → role SOP
- [ ] Invoke Superpowers skills if available (`using-superpowers`, then stage-specific skill)
- [ ] Confirm feature slug (if none → go G0: create comm + spec placeholder)
- [ ] Read **spec → plan → comm log** in full; also read related module docs + GOALS
- [ ] Confirm **worktree** path (new features: forbid main workspace; use `using-git-worktrees` pattern)
- [ ] Declare read list in reply or append to comm
- [ ] **Cross-role handoff check:** find comm entry where Target matches current role; if missing/invalid → `BLOCKED: invalid handoff`

### During Work

- Only modify files within plan scope
- Write decisions and handoffs to comm log — **never only in chat**
- Chat cannot replace comm handoff
- Strategy/direction changes → append dedicated direction log

### Before Ending (Checklist)

- [ ] Comm timestamp: run `TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'` — **never fabricate timestamps**
- [ ] **Append comm** — must include: `agent=`, `Skills used:`, `Read:`, `Said / Decided:`, **Handoff three elements**, `Blockers:`
- [ ] Update role-owned documents (plan checkboxes, review, ADR, daily log)
- [ ] **Reply to human** — attach copyable handoff block (first person, fenced markdown)
- [ ] Update daily log (`docs/ops/daily/YYYY-MM-DD.md`)
- [ ] Pass verification checks appropriate to role (`make ci` for Dev, review docs for Arch/Analyst)

---

## Boundary Enforcement (越界拒绝)

When an agent receives a request **clearly outside its role boundaries** (even from a human), it MUST proactively refuse rather than comply:

| Round | Agent Response |
|-------|---------------|
| **1st request** | **Refuse.** Explain which role should do it; recommend comm handoff path; **do not execute** |
| **2nd request** (insistence) | **Refuse again.** Restate boundary and risks of violating role separation |
| **3rd request** (explicit written confirmation) | May execute exceptionally; comm log `OVERRIDE_ROLE_BOUNDARY` + confirmation text |

**"Explicit confirmation" definition:** After ≥2 refusals, the requester must explicitly state in writing that they want THIS role to do the work. Vague "continue", "just do it", "you decide" does NOT count.

### Refusal Script

```
I am <Role Name> (<Code>). The task you've requested ("<task summary>") belongs to 
<Correct Role Name> (<Code>), not my role. I will not execute it.

Correct path:
1. comm Handoff → Target: <Correct Role>
2. Address: <spec/plan/review path>
3. Task: <what that role should do>

Please open a session for <Correct Role>, or ask a human to forward the above Handoff.

If you still insist I do this as <current role>, please confirm explicitly in writing 
for the 3rd+ time; after confirmation I'll log OVERRIDE_ROLE_BOUNDARY and proceed.
```

---

## Default Delivery Chain (Happy Path)

```
Step 1:  PM + PO      Init ──→ comm + spec placeholder
Step 2:  PO            Design Freeze ──→ spec `approved`, comm `APPROVED` → PM
Step 3:  PM            Schedule ──→ plan with tasks, comm schedule → Arch (complex) | PO (simple)
Step 4*: Arch          Pre-review ──→ comm `ARCH_PRE_PASS` + ADR if needed → PO
Step 5:  PO            Assign ──→ comm Handoff → Dev (三要素)
Step 6:  Dev           Implement ──→ code + tests + verification evidence → Arch
Step 7:  Arch          Code Review ──→ review + comm `ARCH_PASS/FAIL` → Analyst (PASS) | Dev (FAIL)
Step 8:  Analyst       Verify ──→ `DATA_PASS/FAIL` + review report → PO (PASS) | Dev (FAIL)
Step 9:  PO            Accept ──→ `PRODUCT_ACCEPTED` → PM
Step 10: PM            Commit Request ──→ `COMMIT_REQUEST` → PO + Dev + Analyst
Step 11: PO/Dev/Analyst Commit Done ──→ git commit + daily; `COMMIT_DONE` → PM
Step 12: PM            Close ──→ merge + worktree cleanup; `TASK_CLOSED`; plan `[x]`
Step 13: PM            Next ──→ new worktree + plan; Handoff next task
```

\* Step 4 required for complex tasks (>3 files, new module, strategy/rule changes, storage changes, cross-module API changes).

---

## Engineering Isolation (Git Worktree Pattern)

Each task gets its own isolated git worktree to prevent branch conflicts:

```bash
# PM creates worktree before assigning task
git fetch origin
git worktree add .worktrees/feat-<topic> -b feat/<topic> origin/main
# Record: Worktree = .worktrees/feat-<topic> in plan meta + comm

# Dev works exclusively in this worktree
cd .worktrees/feat-<topic>

# PM cleans up after TASK_CLOSED
git checkout main && git pull
git merge feat/<topic>
git worktree remove .worktrees/feat-<topic>
git branch -d feat/<topic>
```

**Rules:** One worktree per task; forbid main workspace for new features; PM manages lifecycle.

---

## Decision Tags (Comm Log Labels)

| Tag | Meaning | Used By |
|-----|---------|---------|
| `APPROVED` | Design or proposal approved | PO |
| `ARCH_PASS` | Code review passed | Arch |
| `ARCH_FAIL` | Code review failed; rework needed | Arch |
| `DATA_PASS` | Data verification passed | Analyst |
| `DATA_FAIL` | Data verification failed; bug list to Dev | Analyst |
| `PRODUCT_ACCEPTED` | PO accepted; ready for PM closure | PO |
| `COMMIT_REQUEST` | PM requests all parties commit + daily | PM |
| `COMMIT_DONE` | Party completed commit + daily | PO / Dev / Analyst |
| `TASK_CLOSED` | PM closed task: merged, worktree cleaned | PM |
| `ESCALATE_PO` | Product definition decision needed | Arch / Analyst |
| `ESCALATE_PM` | Schedule/resource decision needed | Arch / Dev / Analyst |
| `OVERRIDE_ROLE_BOUNDARY` | Role exception after triple confirmation | Any |

---

## Role SOPs (Detailed Reference)

| Role | File |
|------|------|
| Project Manager (PM) | [references/role-sop-pm.md](references/role-sop-pm.md) |
| Product Owner (PO) | [references/role-sop-po.md](references/role-sop-po.md) |
| Architect (Arch) | [references/role-sop-arch.md](references/role-sop-arch.md) |
| Developer (Dev) | [references/role-sop-dev.md](references/role-sop-dev.md) |
| Data Analyst (Analyst) | [references/role-sop-analyst.md](references/role-sop-analyst.md) |
| Handoff Chat Templates | [references/handoff-chat-templates.md](references/handoff-chat-templates.md) |

## Templates

- **[Spec Header](templates/spec-header.md)** — Spec with status, comm log ref, plan ref
- **[Plan Header](templates/plan-header.md)** — Plan with task checkboxes
- **[Comm Entry](templates/comm-entry.md)** — Comm log entry with handoff block
- **[Arch Review](templates/arch-review.md)** — Architecture review document
- **[Analyst Review](templates/analyst-review.md)** — Data verification report

---

## Comparison: This Protocol vs cursor-agent-orchestration

| Dimension | doc-driven-multi-agent | cursor-agent-orchestration |
|-----------|----------------------|---------------------------|
| Layer | **Coordination** — what agents do | **Runtime** — how agents run |
| Mechanism | Document handoffs, role boundaries, gates | tmux sessions, process lifecycle, state detection |
| Platform | Any AI agent (Cursor, Claude Code, Copilot, Hermes) | Cursor Agent via tmux |
| Key idea | Agents write files for each other | Agents run in separate tmux windows |

Use **both together**: `cursor-agent-orchestration` to run agent processes, this protocol to coordinate them.

---

## Adapting to Your Project

1. **Create document skeleton:** `AGENTS.md` → `docs/ops/WORKFLOW.md` → `docs/product/GOALS.md`
2. **Define roles** in your project context (which agents play which roles)
3. **Start with one feature** — create `docs/superpowers/comms/my-first-feature.md` + spec
4. **Enforce the handoff protocol** from day one — no chat handoffs, ever
5. **Add role SOPs** one at a time as your team grows
6. **Use git worktrees** — safe parallel agent work

---

## License

MIT
