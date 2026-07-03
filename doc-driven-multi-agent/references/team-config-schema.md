---
title: Team Config Schema Reference
type: reference
status: active
last-reviewed: 2026-07-03
---

# Team Config Schema

> The `team-config.yaml` file stores your team structure, role assignments, document paths, and engineering preferences so the skill doesn't ask you every session.

## File Location

| Scope | Path | Behavior |
|-------|------|----------|
| **Global (shared across projects)** | `~/.config/skills/doc-driven-multi-agent/team-config.yaml` | Auto-loaded on every skill invocation. Created by onboarding interview or manually. |
| **Per-project override** | `<project-root>/.skills/team-config.local.yaml` | If present, fields deep-merge on top of the global config. Only specify fields you want to override. |

The agent checks for global config first; if found, loads it. Then checks for per-project override; if found, merges fields on top (deep merge — nested fields like `roles.*` are merged, not replaced wholesale).

## Full Schema

```yaml
# ~/.config/skills/doc-driven-multi-agent/team-config.yaml
version: "1.0"
team_name: "My AI Team"
created: "2026-07-03T14:30CST"
last_used: "2026-07-03T14:30CST"

# ── Roles ──────────────────────────────────────────────────────
# Each of the 5 protocol roles. enabled=false means the role
# is skipped in the handoff chain (e.g. no Analyst in your team).
roles:
  project_manager:
    enabled: true
    played_by: "Hermes Agent"                # Human-readable name
    agent_type: "hermes"                     # hermes | cursor-agent | claude-code | copilot | human
    session_template: ""                     # e.g. "cursor-pm-{task}" for tmux sessions
    notes: ""

  product_owner:
    enabled: true
    played_by: ""
    agent_type: ""
    session_template: ""
    notes: ""

  architect:
    enabled: true
    played_by: ""
    agent_type: ""
    session_template: ""
    notes: ""

  developer:
    enabled: true
    played_by: ""
    agent_type: ""
    session_template: ""
    notes: ""

  data_analyst:
    enabled: false
    played_by: ""
    agent_type: ""
    session_template: ""
    notes: "Not needed yet"

# ── Document Paths ──────────────────────────────────────────────
# Where the protocol documents live in your project.
# Change these if your project uses a different layout.
document_paths:
  root: "."
  workflow: "docs/ops/"
  product: "docs/product/"
  specs: "docs/superpowers/specs/"
  comms: "docs/superpowers/comms/"
  plans: "docs/superpowers/plans/"
  reviews: "docs/superpowers/reviews/"
  daily: "docs/ops/daily/"
  worktrees: ".worktrees/"

# ── Feature Slug Convention ─────────────────────────────────────
# Template for generating new feature slugs.
# Available variables: {tag}, {date}, {ticket}
feature_slug_pattern: "{tag}-{date}"

# ── Handoff Chain ───────────────────────────────────────────────
# The order in which roles hand off work to the next role.
# This is the default from the protocol; override if your team
# uses a different flow (e.g. no Analyst, or Arch does pre-review
# before Dev starts).
handoff_chain:
  - "po"          # design / spec
  - "pm"          # plan / schedule
  - "arch"        # pre-review (if complex, before Dev)
  - "dev"         # implement
  - "arch"        # code review
  - "analyst"     # data verification (skipped if disabled)
  - "po"          # product acceptance
  - "pm"          # closure

# ── Engineering Preferences ─────────────────────────────────────
engineering:
  use_worktrees: true
  preferred_ci: "make ci"
  timestamp_tz: "Asia/Shanghai"
```

## Field Reference

### Top-Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Schema version (currently `"1.0"`) |
| `team_name` | string | yes | Human-readable team name |
| `created` | string | yes | ISO timestamp when config was first created |
| `last_used` | string | auto | Updated each time config is loaded |
| `roles` | object | yes | Role assignments (see below) |
| `document_paths` | object | yes | Document directory layout |
| `feature_slug_pattern` | string | no | Template for auto-generating feature slugs |
| `handoff_chain` | array | yes | Ordered list of roles in the handoff pipeline |
| `engineering` | object | yes | CI, worktree, timezone preferences |

### Roles.`<role>`

Each role key is one of: `project_manager`, `product_owner`, `architect`, `developer`, `data_analyst`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | boolean | yes | Whether this role is active in your team |
| `played_by` | string | no | Human-readable name of the person/agent playing this role |
| `agent_type` | string | no | One of: `hermes`, `cursor-agent`, `claude-code`, `copilot`, `human` |
| `session_template` | string | no | tmux session name template (e.g. `cursor-arch-{task}`). Only relevant when using cursor-agent-orchestration. |
| `notes` | string | no | Free-text notes about this role assignment |

### Document Paths

| Field | Default | Description |
|-------|---------|-------------|
| `root` | `.` | Project root (usually keeps default) |
| `workflow` | `docs/ops/` | Workflow documents |
| `product` | `docs/product/` | Product goals and decisions |
| `specs` | `docs/superpowers/specs/` | Feature specifications |
| `comms` | `docs/superpowers/comms/` | Communication log |
| `plans` | `docs/superpowers/plans/` | Task plans |
| `reviews` | `docs/superpowers/reviews/` | Verification reviews |
| `daily` | `docs/ops/daily/` | Daily engineering logs |
| `worktrees` | `.worktrees/` | Git worktree directory |

### Handoff Chain

Each entry is a role code: `pm`, `po`, `arch`, `dev`, `analyst`. The order defines the pipeline. Roles with `enabled: false` are skipped automatically.

### Engineering

| Field | Default | Description |
|-------|---------|-------------|
| `use_worktrees` | `true` | Whether to use git worktrees for task isolation |
| `preferred_ci` | `make ci` | CI command to run before handoff |
| `timestamp_tz` | `Asia/Shanghai` | IANA timezone for comm log timestamps |

## Per-Project Override Example

Create `.skills/team-config.local.yaml` in your project root to override specific fields:

```yaml
# .skills/team-config.local.yaml — overrides global config for this project only
document_paths:
  specs: "docs/specs/"            # different spec directory for this project
  comms: "docs/handoffs/"

engineering:
  preferred_ci: "pnpm ci"         # different CI tool
```

Only the specified fields are merged; all other fields fall through to the global config.

## Auto-Generation

This file is auto-generated by the onboarding interview (see [onboarding-interview.md](onboarding-interview.md)). You can also:

- **Edit manually** — any text editor; YAML syntax
- **Re-run interview** — say "reconfigure team" in chat
- **Copy template** — use [templates/team-config.yaml](../templates/team-config.yaml) as a starting point
