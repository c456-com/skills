---
name: c456-ai-summit
category: autonomous-ai-agents
tags: [tmux, cursor, summit, conference, multi-agent, dynamic-layout, meeting-log]
description: "Host an AI roundtable summit with multiple cursor-agent roles in tmux — dynamic layout switching, per-pane monitoring, shared meeting log system, and agency-agents role integration."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tmux, cursor, summit, conference, multi-agent, dynamic-layout, meeting-log]
    related_skills: [tmux-cursor-agent, cursor-agent-orchestration, agency-agents]

---

> **Overlap note:** The `cursor-agent-orchestration` skill covers the general multi-pane conference pattern (Layout B), conference log protocol, and roundtable layout manager. This `c456-ai-summit` skill is a **concrete event template** — specific role lineup, specific log files, specific layout script — that you can customize per session. The two are complementary: load `cursor-agent-orchestration` for the general technique, load `c456-ai-summit` for a ready-to-run summit.
---

# c456 AI Summit

> Host multi-role AI roundtable discussions using tmux + cursor-agent + agency-agents.
> Dynamic layout, per-pane monitoring, meeting log with timeline.

## Prerequisites

- **tmux-cursor-agent** skill (monitoring daemon)
- **agency-agents-router** plugin (233 expert roles): `scripts/install.sh --tool hermes`
- **layout.sh** (dynamic tmux layout manager): save to project root `.hermes/layout.sh`

## Quick Start

### 1. Setup the Summit Session

```bash
# Create session with explicit size (240x80 = room for 6+ panes)
tmux new-session -d -s c456-summit -n Agents -x 240 -y 80 -c /path/to/project

# Create N panes (here 6 for rehearsal, adjust for actual guest count)
for i in 1 2 3 4 5; do
  tmux split-window -h -t c456-summit:0 -c /path/to/project
done

# Apply tiled layout
tmux select-layout -t c456-summit:0 tiled

# Label each pane with role name (Chinese supported)
tmux set -t c456-summit pane-border-status top
tmux set -t c456-summit pane-border-format '#{pane_index}: #{pane_title}'
tmux select-pane -t c456-summit:0.0 -T "PM 产品经理"
tmux select-pane -t c456-summit:0.1 -T "ARCH 架构师"
# ... for each role

# Enable mouse scrolling so the observer can scroll through each pane's history
tmux set -t c456-summit -g mouse on

# Notify the user to attach
echo "Attach: tmux attach -t c456-summit"
```

### 2. Prepare Meeting Log Files

```bash
cd /path/to/project

# Timeline (host-maintained)
cat > MEETING_TIMELINE.md << 'EOF'
# Summit — Meeting Timeline
> Host-maintained chronological index of all remarks.
EOF

# Per-role log files (one per guest + host)
for role in PM ARCH MAS GROWTH UX SEC HOST; do
  cat > "MEETING_LOG_${role}.md" << 'EOF2'
# Summit — ROLE Log

> Personal remarks log, readable by all participants.

EOF2
done
```

### 3. Load Roles (per pane, sequential)

For each pane, load the role personality from agency-agents or a custom definition.

**From agency-agents (recommended):**

```bash
# Find and read the agent file
cat /tmp/agency-agents/product/product-manager.md

# Send role definition + meeting rules via four-step protocol
# Step 1: verify pane is idle
tmux capture-pane -t c456-summit:0.0 -p -S -3
# Step 2: send role text (NO Enter)
tmux send-keys -t c456-summit:0.0 "你的角色是 Product Manager。以下是你的完整人格定义和会议规矩……"
# Step 3: wait
sleep 3
# Step 4: Enter + verify
tmux send-keys -t c456-summit:0.0 Enter
sleep 10
tmux capture-pane -t c456-summit:0.0 -p -S -5
```

**Role loading message template:**

```
你的角色是 [ROLE_NAME]，以下是你的完整人格定义和本场会议规矩。

【人格定义】
[PERSONALITY_DEFINITION]

【会议规矩】
• 参会人：[LIST_ALL_ROLES] + 主持人 Hermes + 老板旁听
• 你的日志文件：MEETING_LOG_[CODE].md
• 阅读他人发言：cat MEETING_LOG_角色简称.md
• 写日志：cat >> MEETING_LOG_角色简称.md 追加发言
• 每段发言格式：
  ## 编号 | 角色全名 | ISO8601时间 | 类型
  
  正文内容
  
  ---
• 时间线：主持人维护 MEETING_TIMELINE.md，tail 可看最新动态
• 引用他人：@角色简称:编号（例如 @ARCH:T01）

【任务】
请确认收到以上规则。然后在你的日志文件中写入签到记录：
## T00 | 你的全名 | 时间 | Check-in

收到请回复「[简称] 已就位」。
```

### 4. Start Per-Pane Monitor

```bash
cd /path/to/tmux-cursor-agent

# Register monitoring group
python3 -m core.monitor group-create summit --label "AI Summit"

# Add each pane with pane index
python3 -m core.monitor add --group summit c456-summit 0 --pane 0 --label "PM"
python3 -m core.monitor add --group summit c456-summit 0 --pane 1 --label "ARCH"
# ... for each pane

# Start daemon (via Hermes terminal with watch_patterns)
terminal(
  command="cd /path/to/tmux-cursor-agent && exec python3 -m core.monitor daemon --group summit",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
```

Monitor daemon now emits `CURSOR-STOPPED:summit:c456-summit:0:0:idle` with pane index.

## Dynamic Layout Switching

Save `layout.sh` to the project directory. Supports:

| Command | Effect | Best For |
|---------|--------|----------|
| `bash layout.sh cols` | Multi-column (auto-calculates based on terminal width & min 50px/pane) | Broadcasting to all roles simultaneously |
| `bash layout.sh grid` | Tiled grid | Cross-panel debate, overview |
| `bash layout.sh focus PM` | Zoom into one pane (by role keyword or index) | One-on-one interview with a role |
| `bash layout.sh zoom` | Toggle zoom off (restore previous layout) | Return from interview |

**Smart column calculation** (`cmd_cols` in layout.sh):
- Reads terminal width
- Divides by `min_width` (default 50) to get max columns
- If all panes fit → `even-horizontal`
- If not → calculates rows, uses `tiled`

Customize `min_width` in the script for your display.

## Discussion Flow

### Round 1: Opening Statements — `cols` mode

Send the topic to ALL panes simultaneously. Each role writes their independent analysis to their log file.

```bash
bash layout.sh cols
for pane in 0 1 2 3 4 5; do
  tmux send-keys -t c456-summit:0.$pane "【议题】c456 想做 AI 时代的知识基座……"
  sleep 2
  tmux send-keys -t c456-summit:0.$pane Enter
done
```

Wait for all 6 CURSOR-STOPPED notifications. Then read logs and update timeline.

### Round 2: Cross-Debate — `grid` + `focus` modes

Pick interesting points from logs, route to specific roles:

```bash
bash layout.sh focus "ARCH"  # Zoom into Architect
tmux send-keys -t c456-summit:0.1 "@PM:T01 提到的定价策略，从架构角度评估可行性"
bash layout.sh zoom          # Restore
```

### Round 3: Convergence — `cols` mode

```bash
bash layout.sh cols
# Broadcast: "One-sentence final recommendation?"
```

## Teardown

```bash
# Graceful exit all cursor-agent sessions
for pane in 0 1 2 3 4 5; do
  tmux send-keys -t c456-summit:0.$pane "/exit" Enter
  sleep 2
  tmux send-keys -t c456-summit:0.$pane Enter
done

# Kill monitor daemon
# Kill tmux session
tmux kill-session -t c456-summit
```

## Pitfalls

1. **Pane indexing after vertical splits**: When splitting horizontally then vertically, tmux pane indices may not be sequential. Always verify with `tmux list-panes`.
2. **Login token sharing**: Multiple cursor-agent instances share the same auth token. Log in once, then all panes reuse it.
3. **Concurrent Cursor Pro limits**: Tested with 6 concurrent instances on Cursor Pro. If throttled, reduce guest count.
4. **Terminal size matters**: Create session with `-x 240 -y 80` to have room for all panes. Without explicit size, small terminals cause "no space for new pane" errors.
5. **layout.sh min_width**: Adjust based on your monitor. 80 for 4K, 50 for laptop screens.
6. **Focus with role keyword**: `focus SEC` fuzzy-matches pane title. Must match partial label text.

## File Reference

| File | Purpose |
|------|---------|
| `.hermes/layout.sh` | Dynamic tmux layout manager (cols/grid/focus/zoom) |
| `MEETING_TIMELINE.md` | Host-maintained chronological index |
| `MEETING_LOG_[CODE].md` | Per-role personal log (PM/ARCH/MAS/GROWTH/UX/SEC/HOST) |
