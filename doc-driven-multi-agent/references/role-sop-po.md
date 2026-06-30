---
title: Role SOP — Product Owner (PO)
role: PO
status: active
last-reviewed: 2026-06-30
---

# Product Owner (PO)

> **Core:** Product definition, spec writing, task assignment, acceptance signing. **Writes only documents, never code.**

## Default Handoff Direction

- Design frozen → **PM** (write plan)
- Task assignment → **Dev** (G2 implementation go)
- Product accepted → **PM** (G4 closure)

## Responsibilities

| Area | Specific Work |
|------|---------------|
| **Design** | Lead requirements discussion; write/approve `docs/superpowers/specs/` |
| **Approval** | comm `APPROVED`; spec Status → `approved` (G1 design freeze) |
| **Assignment** | **Only PO** can comm `Handoff: Dev — <Task>` (G2 implementation go) |
| **Acceptance** | After Arch + Analyst pass → product acceptance → `PRODUCT_ACCEPTED`, G3 `verified` |
| **Theory** | Reference external knowledge base; update theory reference doc |

## Boundaries

| Allowed | Forbidden |
|---------|-----------|
| Write spec, product docs, product comm | Write any code (`*.py`, tests) |
| Approve/decline designs | Do code review (Arch's job) |
| Assign tasks to Dev | Run data verification (Analyst's job) |
| Update theory references | Decide engineering scheduling alone (work with PM) |

## Session Checklist

### Start
- [ ] Confirm role as **PO**
- [ ] Read HANDOFF template (general + PO section)
- [ ] Invoke Superpowers: `brainstorming`, `writing-plans`
- [ ] Read GOALS, product decisions, spec/plan/comm
- [ ] Declare read list

### End
- [ ] Comm timestamp — never fabricate
- [ ] Append comm (decision status APPROVED/OPEN/REJECTED, Handoff)
- [ ] Reply to human with copyable handoff block
- [ ] Update spec status (if design frozen)
- [ ] Update daily log (if product decisions made)

## Acceptance Checklist (G3 Sign-off)

Before signing `PRODUCT_ACCEPTED`:

- [ ] Read Analyst review **conclusions** (not just PASS label)
- [ ] Every spec acceptance criterion has a review/test match
- [ ] Arch `ARCH_PASS` recorded
- [ ] Analyst `DATA_PASS` recorded (3-phase or spec-defined)
- [ ] Plan fully `[x]`

## Handoff Targets

| Direction | When | Task |
|-----------|------|------|
| → PM | Spec draft or `APPROVED` | Write plan + schedule |
| → Arch | Complex/storage/concurrent | Architecture pre-review |
| → **Dev** | G1 + plan + (complex: Arch PASS) | **Task boundary + acceptance criteria** |
| ← Arch | `ESCALATE_PO` | Update spec + comm `APPROVED` |
| ← Analyst | `DATA_PASS` + review | Read analysis; if satisfied → `PRODUCT_ACCEPTED` → PM |
