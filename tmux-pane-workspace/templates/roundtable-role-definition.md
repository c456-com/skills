# 角色定义模板 — Tmux Pane 圆桌会议

设置多 pane 圆桌会议时使用此模板。它只定义 tmux workspace 和会议角色，不绑定具体 Agent。实际消息发送、状态等待和监控方式，请使用对应的 `tmux-*-agent` 技能。

## 布局选项

### 2x2 网格（4 个角色）

```bash
tmux new-session -d -s roundtable -n Agents -c /path/to/project
tmux split-window -h -t roundtable:0
tmux split-window -v -t roundtable:0.0
tmux split-window -v -t roundtable:0.1
tmux select-layout -t roundtable:0 tiled
```

### 3x2 网格（6 个角色）

```bash
tmux new-session -d -s roundtable -n Agents -c /path/to/project
tmux split-window -h -t roundtable:0
tmux split-window -v -t roundtable:0.0
tmux split-window -v -t roundtable:0.1
tmux split-window -v -t roundtable:0.0
tmux split-window -v -t roundtable:0.1
tmux select-layout -t roundtable:0 tiled
```

## 主题

```text
[用 2-3 句话陈述讨论主题。包含每个角色都需要知道的上下文。]
```

## 基础角色（4 pane）

### 角色：产品经理（PM） — pane 0

视角：市场机会、用户需求、商业化路径、竞品差异。关注「要不要做」和「为什么做」。

### 角色：架构师（Arch） — pane 1

视角：技术可行性、扩展性、现有系统复用度、工程风险。关注「能不能做」和「怎么做」。

### 角色：开发者（Dev） — pane 2

视角：落地成本、现有代码库改动量、CI/测试覆盖、交付节奏。关注「做起来要多久」和「会不会破坏系统」。

### 角色：分析师（Analyst） — pane 3

视角：行业趋势、数据支撑、竞品动态、冷启动策略。关注「数据怎么说」和「别人怎么做」。

## 扩展角色

- Growth Hacker：增长、定价、冷启动、传播。
- UX Architect：上手门槛、信息架构、可访问性。
- Security Architect：多租户隔离、隐私、权限、合规。
- Finance：成本、毛利、现金流、定价模型。

## 讨论协议

### 第一轮：开场陈述

每个角色给出独立观点。若具体 Agent 技能支持状态通知，可等待全部 STOPPED 后再读取；否则逐 pane 读取。

### 第二轮：交叉碰撞

主持人选择性地把一个角色的观点转给另一个角色评审，不要无差别广播。

```text
[角色 B]，[角色 A] 提到了“[引用]”。请从你的角度评估：有什么顾虑、赞同或替代方案？
```

### 第三轮：收敛

要求每个角色给出最终建议、最大风险和下一步行动。

```text
基于前面的讨论，请给出你认为现在应该采取的唯一下一步行动，并说明最大风险。
```

## 多 pane 监控

如果具体 Agent 技能支持 pane 级监控，可以把每个 pane 注册为 `session:window.pane`。例如 Cursor Agent 使用 `tmux-cursor-agent`：

```bash
for pane in 0 1 2 3; do
  python3 -m core.monitor add --group roundtable roundtable 0 --pane "$pane" --label "Pane-$pane"
done
```

## 多 pane 布局陷阱

1. **pane 数量不匹配**：发送前用 `tmux list-panes -t roundtable:0 -F '#{pane_index}: #{pane_title}'` 验证。
2. **角色映射漂移**：`resize-pane -Z` 不会改变 pane 索引；但 `swap-pane`、重排布局或重新拆 pane 后，必须重新验证角色映射。
3. **可见性不足**：4 个 pane 通常适合总览；6 个以上建议用 `focus` 聚焦阅读。
4. **具体 Agent 登录竞争**：如果多个 pane 同时启动同一种 Agent，按对应 `tmux-*-agent` 技能建议错峰启动。
