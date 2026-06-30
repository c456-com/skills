# doc-driven-multi-agent

> **Platform-agnostic document-driven multi-agent coordination protocol — role-based SOPs, handoff protocol, gates G0–G4, and boundary enforcement.**

A protocol for coordinating multiple AI agents through **document-driven handoffs** rather than chat-based communication. Every decision, task transfer, and review is recorded in project documents forming an auditable chain of custody.

**Core rule:** No document = no handoff = no work start.

## Quick Start

```bash
# Install via npx skills
npx skills add c456-com/skills --skill doc-driven-multi-agent -y
```

Then in your project:

1. Read `SKILL.md` for the full protocol
2. Create `AGENTS.md` as your entry point (see templates/spec-header.md for format)
3. Define roles and create the document skeleton
4. Start your first feature with a spec + comm log

## What's Inside

```
doc-driven-multi-agent/
├── SKILL.md                    # Full protocol definition
├── references/
│   ├── role-sop-pm.md          # Project Manager SOP
│   ├── role-sop-po.md          # Product Owner SOP
│   ├── role-sop-arch.md        # Architect SOP
│   ├── role-sop-dev.md         # Developer SOP
│   ├── role-sop-analyst.md     # Data Analyst SOP
│   └── handoff-chat-templates.md # Chat handoff message templates
├── templates/
│   ├── spec-header.md          # Spec document template
│   ├── plan-header.md          # Plan document template
│   ├── comm-entry.md           # Comm log entry template
│   ├── arch-review.md          # Architecture review template
│   └── analyst-review.md       # Data verification report template
├── LICENSE                     # MIT
└── README.md
```

## Core Concepts

### Document Chain

```
AGENTS.md → WORKFLOW.md → GOALS → spec → comm → plan → code → review → daily
```

Every piece of work flows through this document chain. No document = no handoff = no work start.

### Five Roles

| Role | Code | Writes Code? |
|------|------|:------------:|
| Project Manager | PM | No |
| Product Owner | PO | No |
| Architect | Arch | Limited |
| Developer | Dev | Yes |
| Data Analyst | Analyst | No |

### Handoff Protocol (三要素)

Every role transfer requires three fields in the comm log:
- **Target** (对象) — Who receives the handoff
- **Address** (地址) — Paths to relevant documents
- **Task** (事项) — What the next role should do

### Gates G0–G4

G0 (Initiation) → G1 (Design Freeze) → G2 (Implementation Go) → G3 (Product Acceptance) → G4 (Closure)

## Related Skills

- **[tmux-cursor-agent](https://github.com/c456-com/skills/tree/main/tmux-cursor-agent)** — Runtime layer: run Cursor Agent processes via tmux
- **[c456-software-dev-sop](https://github.com/c456-com/skills/tree/main/c456-software-dev-sop)** — General software development SOP

## License

MIT
