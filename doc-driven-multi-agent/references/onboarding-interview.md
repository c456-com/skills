---
title: Onboarding Interview Protocol
type: reference
status: active
last-reviewed: 2026-07-03
---

# Onboarding Interview Protocol

> How the AI agent conducts the team config interview — triggers, questions, answer processing, and save flow.

## When to Interview

The interview starts when **one or more of these conditions** are true:

| Condition | Trigger | Action |
|-----------|---------|--------|
| **First use** | `~/.config/skills/doc-driven-multi-agent/team-config.yaml` does not exist | Auto-start interview after announcing "I notice this is your first time. Let me ask a few questions about your team." |
| **Force reconfigure** | User says "reconfigure team", "setup team", "change team config" | Re-run full interview; overwrite existing config |
| **Config stale** | Config file exists but `last_used` is >30 days old | Prompt "Your team config is 30+ days old. Does it still reflect your current team? (y/N)" — if No, start interview |
| **Mid-session stability** | See [Stability Detection](#stability-detection) below | Prompt "Team looks stable. Save as config?" |

### Config Detection Flow (Decision Tree)

```
1. Check: ~/.config/skills/doc-driven-multi-agent/team-config.yaml exists?
   ├─ YES → Load it → check `last_used` age
   │         ├─ >30 days → prompt for refresh
   │         └─ ≤30 days → announce "Loaded team: {team_name}"; skip interview
   │
   └─ NO → Check: <project-root>/.skills/team-config.local.yaml exists?
            ├─ YES → Load + announce per-project override found
            └─ NO → Start onboarding interview
```

## Interview Phases

The interview is a **conversational sequence** — ask one question at a time, wait for the user's answer, then proceed. Do NOT dump all questions at once.

### Phase 1: Team Identity

**Question:** "What's your team or project name? (I'll use this to label your config)"

**Processing:** Set `team_name` to the answer. Default: `"My AI Team"`.

---

### Phase 2: Active Roles

**Question:** "Which of the 5 protocol roles does your team use? I'll list them — just tell me which ones you need:

1. **Project Manager (PM)** — planning, worktrees, closure
2. **Product Owner (PO)** — specs, product decisions, acceptance
3. **Architect (Arch)** — architecture decisions, code review
4. **Developer (Dev)** — implementation, tests
5. **Data Analyst (Analyst)** — data verification

Which roles do you use? (e.g. 'all 5', 'PM PO Arch Dev', 'just Dev and PO')"

**Processing:**
- If user says "all" or "all 5" → all `enabled: true`
- If user lists specific roles → set those to `enabled: true`, others to `false`
- Validate: at minimum `po` + `dev` must be enabled (protocol can't function without design and implementation)

---

### Phase 3: Role Assignments (one sub-question per enabled role)

For each enabled role, ask:

**Question:** "Who plays the **{Role Name} ({Code})** role? Options: Hermes Agent, Cursor Agent, Claude Code, GitHub Copilot, or a human."

**Examples:**
- For PM: "Who plays Project Manager (PM)?"
- For Dev: "Who plays Developer (Dev)?"

**Processing:** Set `played_by` to the user's answer, `agent_type` to the mapped value:

| User Says | agent_type |
|-----------|------------|
| "Hermes", "Hermes Agent", "myself" | `hermes` |
| "Cursor", "Cursor Agent" | `cursor-agent` |
| "Claude", "Claude Code" | `claude-code` |
| "Copilot", "GitHub Copilot" | `copilot` |
| "Human", "a person", "my boss" | `human` |

If `agent_type` is `cursor-agent`, also ask: "Do you use a tmux session template for this role? (e.g. `cursor-arch-{task}`)" → set `session_template`.

**Optional follow-up:** "Any notes for this role? (e.g., who specifically, or special instructions)" → set `notes`.

---

### Phase 4: Worktree Preference

**Question:** "Do you use git worktrees for parallel task isolation? (Recommended for multi-agent setups.) (Y/n)"

**Processing:**
- Y or empty → `use_worktrees: true`
- N → `use_worktrees: false`

---

### Phase 5: CI Command

**Question:** "What command do you use to run tests/CI before handoff? (default: `make ci`)"

**Processing:** Set `preferred_ci` to the answer. Keep default if user says "default" or leaves empty.

---

### Phase 6: Timezone

**Question:** "What timezone do you want for comm log timestamps? (default: Asia/Shanghai, or press Enter for default)"

**Processing:** Set `timestamp_tz` to the answer. Validate against IANA timezone list if possible; otherwise accept as-is.

---

### Phase 7: Document Paths (optional deep-dive)

**Question:** "The protocol uses default document paths like `docs/superpowers/specs/` and `docs/superpowers/comms/`. Do these work for your project, or do you use different directories? (defaults work / customize)"

- If "defaults work" → keep defaults, skip sub-questions
- If "customize" → ask one at a time:
  1. "Spec documents directory?" (default: `docs/superpowers/specs/`)
  2. "Comm log directory?" (default: `docs/superpowers/comms/`)
  3. "Plan directory?" (default: `docs/superpowers/plans/`)
  4. "Review directory?" (default: `docs/superpowers/reviews/`)
  5. "Daily log directory?" (default: `docs/ops/daily/`)
  6. "Worktree directory?" (default: `.worktrees/`)

---

## Save Flow

After all phases complete:

1. **Construct YAML** — assemble all answers into the schema
2. **Set timestamps** — `created` and `last_used` to current time (`TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'`)
3. **Ensure directory exists** — `mkdir -p ~/.config/skills/doc-driven-multi-agent/`
4. **Write file** — to `~/.config/skills/doc-driven-multi-agent/team-config.yaml`
5. **Announce success:**

```
✅ Team config saved to ~/.config/skills/doc-driven-multi-agent/team-config.yaml

Next time you load this skill, I'll remember your team and skip the interview.

To make changes later:
  • Say "reconfigure team" to re-run the interview
  • Or edit the file directly with any text editor
  • For project-specific overrides, create .skills/team-config.local.yaml
```

## Error Handling

| Situation | Response |
|-----------|----------|
| User gives unclear answer | Ask a clarifying follow-up (e.g., "I heard 'Dev and PO' — do you also need a PM or Architect?") |
| User says "skip" or "I don't know" | Use the default value for that field; note it in the config as `# auto-default` comment |
| User interrupts or changes topic | After returning to the conversation, recap: "We were setting up your team config. Last question was about {phase}. Shall I continue from there?" |
| YAML write fails (permission) | Explain the issue: "Could not write to ~/.config/skills/... — permission denied. Please create the directory manually with: mkdir -p ~/.config/skills/doc-driven-multi-agent" |

## Reconfiguration

When user says "reconfigure team":

1. Ask: "Do you want to start fresh (overwrite everything) or update specific fields?"
2. Full reconfig → run all 7 phases
3. Partial update → ask which field to change, update only that field in the YAML

## Stability Detection

Detected during the Session Protocol End checklist (see SKILL.md):

```
After 3+ feature cycles with the same role assignments AND no team-config.yaml exists yet:
  → Ask: "Your team structure looks stable. Save it as the default team config?
          (This means next session I won't need to ask about your team.)"
```

If the user agrees → run a mini-interview (Phase 1 + Phase 2 only → save) or if you already have full info from the session, construct the config directly.

## Per-Project Override Detection

When loading config:

1. Load global config from `~/.config/skills/doc-driven-multi-agent/team-config.yaml`
2. Check for `<project-root>/.skills/team-config.local.yaml`
3. If local override exists:
   - Announce: "Found project-specific overrides in .skills/team-config.local.yaml"
   - Deep-merge fields (nested objects merge, not replace)
   - For `roles.*`: individual role settings merge
   - For `document_paths`: individual path overrides merge
   - For `engineering`: individual fields merge
   - `team_name`, `created` remain from global config
