# Role Definition Template — AI Roundtable

Use this template when setting up a multi-pane cursor-agent roundtable (Layout B).
Customize the `topic`, adjust roles per discussion, and pick a layout.

## Layout Options

### 2×2 Grid (4 roles)
```
tmux new-session -d -s roundtable -n Agents -c /path/to/project
tmux split-window -h -t roundtable:0
tmux split-window -v -t roundtable:0.0
tmux split-window -v -t roundtable:0.1
tmux select-layout -t roundtable:0 tiled
```

### 3×2 Grid (6 roles) — for broader discussion
```
tmux new-session -d -s roundtable -n Agents -c /path/to/project
tmux split-window -h -t roundtable:0        # → 2 columns
tmux split-window -v -t roundtable:0.0      # split left column
tmux split-window -v -t roundtable:0.1      # split right column
# Now 4 panes. Add 2 more:
tmux split-window -v -t roundtable:0.0      # split left-top
tmux split-window -v -t roundtable:0.1      # split right-top
tmux select-layout -t roundtable:0 even-vertical
```

## Topic
```
[State the discussion topic in 2-3 sentences. Include context the agents need.]
```

## Base Roles (4-pane)

### Role: Product Manager (PM) — Pane 0
你是 PM（产品经理）。视角：市场机会、用户需求、商业化路径、竞品差异。关注「要不要做」和「为什么做」，关注用户分层和付费意愿。

### Role: Architect (Arch) — Pane 1
你是 Arch（架构师）。视角：技术可行性、扩展性、现有系统的复用度、工程风险。关注「能不能做」和「怎么做」。

### Role: Developer (Dev) — Pane 2
你是 Dev（开发者）。视角：落地成本、现有代码库改动量、CI/测试覆盖、交付节奏。关注「做起来要多久」和「会不会把代码搞坏」。

### Role: Analyst — Pane 3
你是 Analyst（分析师）。视角：行业趋势、数据支撑、竞品动态、冷启动策略。关注「数据怎么说」和「别人怎么做的」。

## Extended Roles (6-pane)

### Role: Growth Hacker — Pane 4
你是 Growth Hacker（增长黑客）。视角：热钱变现、用户裂变、定价策略、冷启动、病毒循环。关注「怎么赚钱」和「怎么让用户自己带用户」。

### Role: UX Architect — Pane 5
你是 UX Architect（体验架构师）。视角：非技术用户的上手门槛、知识库管理界面的信息架构、可访问性。关注「用户能不能轻松用起来」。

### Role: Security Architect — optional
你是 Security Architect（安全架构师）。视角：多租户数据隔离、用户隐私、访问控制、合规性。关注「数据安不安全」。

## Discussion Protocol

### Round 1 — Opening Statements (parallel)
Broadcast to all panes. Wait for all CURSOR-STOPPED. Read each pane.

**Coordinator actions:**
1. Send opening statement to all STOPPED panes via four-step protocol
2. Wait for N× CURSOR-STOPPED (monitor daemon)
3. For each pane: `capture-pane -t session:window.$pane -p -S -15`
4. Identify key points, disagreements, blind spots

### Round 2 — Cross-Pollination (relay)
Selectively forward interesting points between panes. NOT a broadcast.

**Template messages:**
```text
@[Role B], [Role A] mentioned "[quote]". From your perspective, evaluate this — any concerns or endorsements?
@[Role C], you brought up "[quote]". [Role D], comment on the feasibility/risk/cost of this approach.
```

**Coordinator:** For each relay: check target STOPPED → send → wait CURSOR-STOPPED → read → optional follow-up.

**User interaction:** Observer can interrupt with "ask [Role X] about [aspect]" — queue as next relay.

### Round 3 — Convergence (parallel)
```text
Everyone, final thought: what is the ONE action c456 should take first based on our discussion?
```
Wait for all CURSOR-STOPPED, compile action-item list.

## Monitoring for Multi-Pane Layout
The daemon registers each pane as `session:window.pane`:
```bash
for pane in 0 1 2 3; do
  python3 -m core.monitor add --group roundtable roundtable 0 --pane "$pane" --label "Pane-$pane"
done
```
Watch: `tmux capture-pane -t roundtable:0.$pane -p -S -100`

## Pitfalls for Multi-Pane Layout
1. **Pane index drift after zoom:** Zooming (`resize-pane -Z`) and un-zooming can re-index panes. Always `list-panes` before sending after zoom.
2. **Pane count mismatch:** Verify with `list-panes -F '#{pane_index}: #{pane_title}'` before sending.
3. **Visibility:** 4 panes works on ~27" displays. 6 may need zooming to read.
4. **Login race:** Stagger cursor-agent starts with 5-8 seconds between each pane.
