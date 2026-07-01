---
name: cursor-agent-orchestration
category: autonomous-ai-agents
tags: [cursor, agent, orchestration, tmux, multi-agent, team-work, coordination]
description: "Orchestrate multiple Cursor Agent instances via tmux in Multi-Session Team Work Mode — startup sequences, session naming, git worktree isolation, pre-flight verification, and state recovery. Designed as the coordination layer above tmux-cursor-agent, c456-ai-summit, and doc-driven-multi-agent."
related_skills: [tmux-cursor-agent, c456-ai-summit, doc-driven-multi-agent, hermes-agent]
version: 1.0.0
license: MIT
---

# Cursor Agent Orchestration via tmux

Coordinate **multiple Cursor Agent instances** running in independent tmux sessions on a headless or remote server — a **team of agents** working asynchronously on the same project, with a coordinator (you, Hermes, or a human) relaying information between them.

Unlike the [c456-ai-summit](skill:autonomous-ai-agents/c456-ai-summit) skill (single-window, multi-pane synchronous discussions), this skill is for **long-lived team work mode** where each agent has its own full-screen tmux session and works for hours or days on independent tasks.

## Skill Ecosystem

This skill is the **coordination layer** in a three-layer stack:

```
Layer 3:  doc-driven-multi-agent    ← Protocol: document handoffs, role SOPs, gates
Layer 2:  cursor-agent-orchestration ← (THIS) Orchestration: startup, naming, recovery
Layer 1:  tmux-cursor-agent          ← Runtime: tmux sessions, messaging, daemon
Layer 1:  c456-ai-summit              ← Runtime (alternative): multi-pane conference
```

| Skill | When to Use |
|---|---|
| **[tmux-cursor-agent](skill:autonomous-ai-agents/tmux-cursor-agent)** | Single agent in tmux — send messages, check state, monitoring daemon |
| **[c456-ai-summit](skill:autonomous-ai-agents/c456-ai-summit)** | Multi-pane synchronous discussion (2–10 agents, minutes to 1 hour) |
| **[cursor-agent-orchestration](skill:autonomous-ai-agents/cursor-agent-orchestration) (this)** | Multi-session async team (4+ agents, hours to days) |
| **[doc-driven-multi-agent](skill:autonomous-ai-agents/doc-driven-multi-agent)** | Document-driven team protocol with handoffs, roles, gates |

This skill is **not standalone** — it references the runtime skills for basic operations. Always load the companion skills together:

```bash
skill_view(name='cursor-agent-orchestration')  # This skill
skill_view(name='tmux-cursor-agent')            # Runtime operations
skill_view(name='c456-ai-summit')                # If running conference mode
skill_view(name='doc-driven-multi-agent')        # If using handoff protocol
```

---

## Why tmux + Cursor Agent (not delegate_task)

| Concern | Hermes `delegate_task` | tmux + Cursor Agent |
|---------|----------------------|---------------------|
| Visibility | Invisible (background subagent) | Visible (tmux windows) |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Cost | Per-token API calls | Fixed subscription (Cursor Pro) |
| User inspection | Can't see progress | `tmux capture-pane` or attach |
| Resume on crash | Lost | tmux session persists |
| Multi-agent coordination | Delegation chain | Independent sessions, relay pattern |

---

## Layout A: Multi-Session Team Work Mode (Core Pattern)

Multiple tmux **sessions**, each with a **single agent window**. Best for asynchronous collaboration where agents run long tasks (hours/days):

- Each agent has full-screen terminal visibility
- Agents work independently without visual cross-talk
- You can attach/detach individual sessions without affecting others
- Preferred when agents produce substantial output (tests, code, docs)

```
tmux session hierarchy (single host):

cursor-dev-feature-x              cursor-pm-feature-x
  window 0: Dev-1 (cursor-agent)    window 0: PM (cursor-agent)
  window 1: Dev-2 (cursor-agent)

cursor-arch-feature-x             cursor-analyst-feature-x
  window 0: Arch (cursor-agent)     window 0: Analyst (cursor-agent)
```

- One tmux session per role, one window per agent instance
- Naming: `cursor-{role}-{task_id}` (e.g. `cursor-dev-ab-opt-0624`)
- All sessions on the same host, managed by a coordinator (Hermes or a human)

### When to Use This vs Multi-Pane (c456-ai-summit)

| Factor | Prefer Multi-Session (this) | Prefer Multi-Pane (c456-ai-summit) |
|--------|--------------------------|-----------------------------------|
| Duration | Hours/days | Minutes |
| Agents | 4+ (scales to 10+) | 2–10 (limited by screen) |
| Work style | Independent tasks | Synchronous discussion |
| Output | Code, tests, docs | Analysis, decisions |
| Coordination | Async relay | Real-time moderation |

---

## Pre-Flight: Before Any Multi-Agent Session

### Skill Pre-Flight (MANDATORY)

**Load the governing skills before doing anything in tmux. Do NOT skip this step.**

```bash
skill_view(name='cursor-agent-orchestration')  # This skill
skill_view(name='tmux-cursor-agent')            # Four-step protocol, daemon commands
```

⚠️ **Without loading tmux-cursor-agent, you'll likely forget `watch_patterns` when starting the daemon, and CURSOR-STOPPED notifications will never arrive.** Skill docs contain the correct command templates.

### Protocol Pre-Flight (before sending any message)

Before the first message leaves your keyboard, answer these three questions:

| # | Question | If "Yes" | If "No" |
|---|----------|----------|---------|
| 1 | Is this a **decision-making meeting** that needs real convergence? | Use **Sequential Protocol**. Brief only the first speaker. Keep others **盲开 (blind)** until called. | Use **Broadcast Protocol**. Safe for brainstorming / data-gathering only. |
| 2 | Does this have a clear **output deliverable**? | Sequential protocol is strongly recommended. Broadcast produces shallow output. | Consider whether a session is needed at all. |
| 3 | Have all roles confirmed **who speaks when**? | Proceed. | Brief the first speaker with the agenda. |

**Default: Sequential Protocol.** Broadcast is for brainstorming only.

### Pre-Send Verification Checklist

**Check every row before every message:**

| # | Check | If you answer "No" |
|---|-------|-------------------|
| **🟢 1 — Buffer** | Is the pane's input buffer **clean** (no stale shell commands, no `→` prefixed text)? | **Clean it first:** send `Escape`, `C-c`, `C-u`, `C-k` in sequence with 1s sleeps. Re-check before sending. |
| **🟢 2 — Pane** | Am I sending to **exactly one pane** (the intended speaker)? | **Stop.** In Sequential Protocol, only ONE pane receives this message. |
| **🟢 3 — Protocol** | Am I using **Four-Step Protocol** (`send-keys` → `sleep 2` → `send-keys Enter` → `capture-pane`)? | **Stop.** Never use `echo`, `cat`, or heredoc. The agent reads only from stdin via `send-keys`. |
| **🟢 4 — Log** | Have I read the relevant log files so I know what was already said? | **Stop.** Read before relay. |

**If any check fails → fix it before sending. Do not proceed.**

---

## Session Naming Conventions

Consistent naming is essential when coordinating multiple agents:

| Role | Session Name | Window Name |
|------|-------------|-------------|
| Project Manager | `cursor-pm-{task}` | `PM` |
| Architect | `cursor-arch-{task}` | `Arch` |
| Developer | `cursor-dev-{task}` | `Dev-1`, `Dev-2` |
| Analyst | `cursor-analyst-{task}` | `Analyst` |

- `{task}` = short identifier like `ab-opt-0624`, `info-0625`
- All sessions for one task share the same `{task}` suffix
- Each task gets its own set of sessions (never reuse)

---

## Agent Startup Sequence

```bash
TASK="my-feature"
WORKTREE="/path/to/project/.worktrees/$TASK"
AGENT="cursor-agent"
MONITOR_DIR="/path/to/c456-com/skills/tmux-cursor-agent"

# Phase 1 — Start all agent sessions
for role in pm arch dev analyst; do
  tmux new-session -d -s "cursor-${role}-${TASK}" -n "$role" -c "$WORKTREE"
  tmux send-keys -t "cursor-${role}-${TASK}:0" "$AGENT --model auto agent" Enter
  sleep 4
done

# Verify all started
for role in pm arch dev analyst; do
  echo "=== $role ==="
  tmux capture-pane -t "cursor-${role}-${TASK}:0" -p -S -3
done

# Phase 2 — Register agents and start monitoring daemon
# ⚠️ MUST do this BEFORE sending any task!
for role in pm arch dev analyst; do
  python3 -m core.monitor add --group "$TASK" "cursor-${role}-${TASK}" 0 --label "$role"
done

# Start daemon via Hermes terminal (background + watch_patterns)
#   terminal(
#     command="cd $MONITOR_DIR && exec python3 -m core.monitor daemon --group $TASK",
#     background=true,
#     watch_patterns=["CURSOR-STOPPED:"]
#   )

# Verify daemon sees all windows
# process(action='poll', session_id='<id>')
# → "total=N" where N matches agent count
```

**Key rules:**
- Start all sessions first, then verify — don't check readiness between each start
- Register + start monitoring **BEFORE** sending any task
- If you skip monitoring, agents complete work silently and you'll have no way to know

---

## Git Worktree Isolation

Always use `git worktree` for parallel development to avoid branch conflicts:

```bash
# Create isolated worktree
cd /path/to/project
git worktree add ../project-feature-xxx feature/xxx

# Start agent in worktree
cd ../project-feature-xxx
cursor-agent --model auto agent

# Clean up after merge
cd /path/to/project
git worktree remove ../project-feature-xxx
```

---

## Session Resume After Crash

When Cursor Agent shows "Connection stalled" or the session was lost:

```bash
# Step 1: Try Enter first (simplest recovery, works often)
tmux send-keys -t cursor-dev-my-task:0 Enter

# Step 2: If that fails, resume
tmux send-keys -t cursor-dev-my-task:0 C-c C-c
sleep 1
tmux send-keys -t cursor-dev-my-task:0 "cursor-agent --resume <resume-id>" Enter

# Step 3: Graceful model switch (don't kill)
tmux send-keys -t cursor-dev-my-task:0 "/summarize" Enter
sleep 5
tmux send-keys -t cursor-dev-my-task:0 "/exit" Enter
# Note resume ID, then start fresh with new model
```

---

## Orchestration-Specific Pitfalls

### 🚨 Broadcasting to all sessions = isolated reports, not a discussion

The most common orchestration mistake is **sending the same task to every session simultaneously** and then merging their outputs. This produces **N isolated reports**, not a converged discussion.

**Correct approach:** sequential, moderated, one-at-a-time. One speaker proposes, peers critique, speaker revises, moderator confirms, then move to the next.

### 🚨 Multi-agent session confusion

When relaying between role sessions (PM → Arch → Dev), re-verify the session-to-role mapping before each send. Session names drift if sessions are recreated.

```bash
tmux list-sessions -F '#{session_name}'
# Confirm: cursor-pm-my-task, cursor-arch-my-task, etc.
```

### 🚨 Blind opening violation

**Rule:** Only the first speaker receives the full topic brief. Others stay **盲开 (blind)** — they don't see the agenda until the host calls on them.

**Recovery if you already broadcast:** Reload the agenda only to the first speaker. Tell other agents "please wait — you will receive instructions shortly."

### 🚨 Daemon process accumulation

Each `terminal(background=true)` start creates a new daemon process. Old daemons accumulate and conflict. **Always:**
1. `pkill -f "python3 -m core.monitor daemon" 2>/dev/null; sleep 2`
2. Verify: `ps aux | grep "core.monitor daemon" | grep -v grep | wc -l` → **0**
3. Only then start with `exec python3 -m core.monitor daemon --group GROUP`

### 🚨 Security scan blocks Chinese messages

When using the four-step protocol with Chinese text via `tmux send-keys`, Hermes's security scanner may flag "Confusable Unicode characters". Consider: (a) batching messages, or (b) using English for task instructions that don't specifically need Chinese context.

### 🚨 Exited false positives for cursor-agent

The daemon may report `state=exited` for cursor-agent sessions that are still running. This happens because cursor-agent runs on Node.js (process name `node`), and a temporary shell command can switch `pane_current_command` briefly. Verify with `capture-pane` before assuming the agent crashed.

### 🚨 `/exit` autocomplete menu traps

Typing `/exit` shows an autocomplete menu; pressing Enter once selects from the menu rather than confirming exit. Always send Enter **TWICE**: once to select `/exit`, once to confirm.

---

## Layout B: Multi-Pane Conference Mode

For synchronous multi-pane discussions, see the **[c456-ai-summit](skill:autonomous-ai-agents/c456-ai-summit)** skill. That skill covers:
- 2×2, 3×2, and custom tiled layouts
- Four-pane summit protocol with pane-level monitoring
- Meeting log format with timeline index
- Protocol A (Sequential Discussion — recommended for decision-making)
- Protocol B (Broadcast — for brainstorming)
- Role loading from Agency Agents
- Rehearsal → Test → Formal flow

Quick setup reference (details in c456-ai-summit):

```bash
# Create session with single pane
tmux new-session -d -s c456-summit -n Agents -c /path/to/project

# Split into 2×2 tiled layout
tmux split-window -h -t c456-summit:0
tmux split-window -v -t c456-summit:0.0
tmux split-window -v -t c456-summit:0.1
tmux select-layout -t c456-summit:0 tiled

# Start cursor-agent in each pane (stagger to avoid login race)
for pane in 0 1 2 3; do
  tmux send-keys -t c456-summit:0.$pane "cursor-agent --model auto agent" Enter
  sleep 6
done
```

---

## Layout Switching (native tmux commands)

| Effect | Command | Notes |
|--------|---------|-------|
| **Multi-column** | `tmux select-layout -t session:window even-horizontal` | One row, N columns |
| **Grid** | `tmux select-layout -t session:window tiled` | Even grid |
| **Zoom focus** | `tmux resize-pane -Z -t session:window.pane` | **Does NOT change pane indices** |
| **Unzoom** | `tmux resize-pane -Z -t session:window.pane` (same, toggle) | |

**Priority rule:** Use `resize-pane -Z` (zoom) for focusing. It preserves pane indices. Avoid `swap-pane + main-vertical` because it reorders panes and breaks monitoring.

---

## Monitoring Script Architecture

The Python monitoring system (from [tmux-cursor-agent](skill:autonomous-ai-agents/tmux-cursor-agent) core) has four components:

| Component | Responsibility |
|-----------|---------------|
| **Registry** | Manages named groups of monitored sessions (create/add/remove/list) |
| **Watch** | Captures a single pane and determines EXECUTING/STOPPED/WAITING state |
| **Monitor** | Daemon loop: polls registry, calls Watch on each window, emits state changes |
| **Read** | Captures pane content with configurable line count and optional file output |

State is persisted per-group in a JSON file so the daemon survives restarts.

### Event Handling Flow

```
CURSOR-STOPPED:group:session:window:reason
    │
    ├── needs_approval → review command → auto-approve / escalate
    ├── needs_input    → capture-pane → answer or relay
    ├── task_done      → read output → check handoff → forward to next role
    ├── idle           → capture-pane verify → treat as ready for input
    └── exited         → check crash → restart or notify user
```

For detailed daemon setup, see the [tmux-cursor-agent](skill:autonomous-ai-agents/tmux-cursor-agent) skill.

---

## Meeting Design (Required — define before opening any session)

Before inviting any agent, define all six:

### 1. Topic
What is this about? (e.g., "产品升级方向", "性能优化方案评审")

### 2. Purpose
Why are we doing this? (e.g., "评估可行性", "决定 Go/No-Go")

### 3. Constraints (REQUIRED — this changes everything)
Hard constraints — share with ALL roles before discussion starts:

| Constraint | Example |
|-----------|---------|
| Team size | "1-person" vs "well-funded startup" |
| Funding | "cash-strapped" vs "series A" |
| Timeline | "need results in 2 weeks" vs "6-month build" |
| Target | "hot money" vs "hot users" vs "enterprise sales" |

**Without constraints, agents default to "well-resourced team, build platform" assumptions.**

### 4. Required Deliverables
| Role | Deliverable |
|------|------------|
| PM | Product plan / M0 scope / roadmap |
| ARCH | Technical architecture review |
| MAS | Agent integration protocol assessment |
| GROWTH | Go-to-market strategy |
| UX | User experience evaluation |
| SEC | Security threat model |

### 5. Agenda (speaker order)
Define who speaks when.

### 6. Output File
The final deliverable is written to a shared file by the responsible role.

For the detailed meeting protocols (Sequential Discussion A and Broadcast B), see the **[c456-ai-summit](skill:autonomous-ai-agents/c456-ai-summit)** skill.

---

## References

| File | About |
|------|-------|
| [`references/agency-agents-roster.md`](references/agency-agents-roster.md) | Agency Agents 233 specialist personas — installation, division reference, API |
| [`references/monitoring-daemon-reference.md`](references/monitoring-daemon-reference.md) | Orchestration-view monitoring daemon configuration |

## Templates

| File | About |
|------|-------|
| [`templates/roundtable-role-definition.md`](templates/roundtable-role-definition.md) | Reusable role identities for PM, Arch, Dev, Analyst |
| [`templates/bug-fix-prompt.md`](templates/bug-fix-prompt.md) | Bug fix prompt template for cursor-agent |
| [`templates/feature-dev-prompt.md`](templates/feature-dev-prompt.md) | Feature development prompt template for cursor-agent |
