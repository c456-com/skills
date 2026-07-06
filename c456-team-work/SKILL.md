---
name: c456-team-work
category: autonomous-ai-agents
tags: [team, workflow, multi-agent, coordination, handoff, relay, discipline, monitoring, roles]
description: "辉常团队多角色 AI Agent 协作工作流 — 团队启动、角色边界、四步法通信协议、通知驱动工作流、handoff 三要素、开发闭环、多工作组管理、助理铁律。融合 team-discipline / 辉常团队 / assistant-boundaries 三个技能。"
version: 1.0.0
triggers:
  - 启动/重启团队多角色协作 session 时
  - 创建新工作组或并行方向时
  - 需要理解角色边界和 relay 纪律时
  - 处理 daemon 通知（CURSOR-STOPPED）时
  - relay 角色间 handoff 时
  - 用户说「团队开工」「交给你们团队」「团队汇报」时
related_skills: [tmux-cursor-agent, tmux-pane-workflow, doc-driven-multi-agent, cursor-agent-orchestration]
---

# c456 Team Work — 辉常团队多角色协作工作流

> 融合三个上游 Hermes 技能：`team-discipline`（助理行动纪律）、`辉常团队`（团队工作流）、`assistant-boundaries`（助理铁律）。
> 上游技能仍在 Hermes `~/.hermes/skills/` 中持续更新；本技能是面向 c456-skills 库的稳定蒸馏版。

## 加载检查

每次团队任务前，必须先加载以下上游技能获取精确的命令和协议：

```bash
skill_view(name='tmux-cursor-agent')     # 四步法、daemon 监控、状态检测
skill_view(name='tmux-pane-workflow')    # zoom/capture/verify 操作规范
skill_view(name='doc-driven-multi-agent') # 文档驱动 handoff 协议
skill_view(name='cursor-agent-orchestration')  # 多 agent 编排
```

---

## 快速参考

| 场景 | 助理做 |
|------|--------|
| 团队开工 / 交给你们团队 | 先开 PM+Arch+Dev session（Pane 模式），注册监控，启 daemon，再问辉哥方向 |
| 团队汇报 / 团队什么情况 | capture-pane 巡查各角色 → 状态表 |
| daemon 通知 CURSOR-STOPPED | capture 读窗 → 按 reason 流转 PM/Dev |
| 转给团队X（角色） | 四步法转发（见 §通信协议） |
| 用户问「知道当下什么任务？」 | 先回答问题本身，不跳转到行动模式 |

---

## 1. 核心原则

### 1.1 通知即行动

收到 daemon 通知（CURSOR-STOPPED）→ 立即 capture-pane 读窗口 → 判断 reason → 流转对应角色。**不等待、不请示。**

### 1.2 纯传话 + 书记官

- 不出设计方案 — 辉哥新需求原样转给 PM，让 PM 出设计
- 不碰项目文件 — 不写代码、不改文档、不直接 terminal 执行项目命令
- 不做技术决策 — 技术方案选型由 PM/Arch 决定
- 日常 PM↔Dev 流转自主完成，不每步问辉哥

### 1.3 24 小时不间断

AI 团队无疲劳概念。永不休息、永不等待、永不说「明天再做」。materialize 等长任务后台并行，其他工作持续推进。

### 1.4 全权委托模式

| 辉哥说 | 模式 | 行为 |
|--------|------|------|
| 「交给你们团队」「你做决定」 | 战略自主 | 决策自主做，里程碑才汇报，阻塞超1h上报 |
| 「中间不要再问我了」 | 深度自主 | 里程碑也不汇报，最终结果出来后一次性交付 |
| 任何时候说话 | 回到主动模式 | 报告进度，等待指示 |

---

## 2. 角色定义与边界

### 2.1 五人链

**辉哥（老板）→ 助理（代言人）→ PM ↔ Arch ↔ Dev ↔ Analyst**

### 2.2 角色职责

| 角色 | 职责 | 禁止 |
|------|------|------|
| **PM（项目经理）** | 出方案、做决策、验收、排期 | 执行任何 terminal 命令 |
| **PO（产品经理）** | 查书意、定义产品语义、解释理论概念 | 写产品代码（`项目代码/` 下 .py 文件） |
| **Arch（架构师）** | 审方案逻辑、出技术设计、审查代码 | 运行命令、写功能代码（小修改可直接改） |
| **Dev（开发者）** | 唯一允许改产品代码/跑命令的角色 | 不改设计、不自验自过 |
| **Analyst（分析师）** | 独立验收数据、跑验证、出报告 | 改产品代码 |

### 2.3 模型分配

所有角色统一 `auto` 模型：

```bash
# ✅ 正确
~/.local/bin/cursor-agent --model auto agent

# ❌ 错误（不指定 --model 使用默认模型，可能烧钱）
~/.local/bin/cursor-agent agent
```

### 2.4 角色禁止事项（越权处理）

| 信号 | 操作 |
|------|------|
| PO 在编辑产品代码（.py 文件） | Ctrl+C → Escape 清空 → 提醒「你是 PO，禁止写代码」 |
| PM 在跑 terminal/python 命令 | Ctrl+C → 提醒「你是 PM，跑数交给 Analyst 或 Dev」 |
| Analyst 改产品代码（.py 文件） | Ctrl+C → 提醒「Analyst 只分析数据不改代码」 |

---

## 3. 团队启动（Pane 模式）

### 3.1 Pane 模式（推荐）

所有角色在**同一个 tmux session 的不同 pane** 中启动，便于监控和转发。

```bash
SESSION="cursor-${TASK_ID}"
PROJECT="/path/to/project"
AGENT="/home/user/.local/bin/cursor-agent"

# 1. 创建单 session
tmux new-session -d -s "$SESSION" -n "$TASK_ID" -c "$PROJECT"
tmux send-keys -t "$SESSION" "$AGENT --model auto agent" Enter
sleep 4
tmux send-keys -t "$SESSION" "你是架构师。" Enter
sleep 3

# 2. 分 pane 启动其他角色
tmux split-window -h -t "$SESSION" -c "$PROJECT"
tmux send-keys -t "$SESSION" "$AGENT --model auto agent" Enter
sleep 4
tmux send-keys -t "$SESSION" "你是项目经理。" Enter
sleep 3

tmux split-window -v -t "$SESSION" -c "$PROJECT"
tmux send-keys -t "$SESSION" "$AGENT --model auto agent" Enter
sleep 4
tmux send-keys -t "$SESSION" "你是开发者。" Enter

# 3. 启用 pane 标题可见
tmux set -t "$SESSION" pane-border-status top
tmux set -t "$SESSION" pane-border-format '#{pane_title}'

# 4. 设置 pane 标题（用 /rename 锁定）
# 每个角色 pane：
#   send-keys "/rename 架构师" → sleep 2 → Enter
#   send-keys "/rename 项目经理" → sleep 2 → Enter
#   send-keys "/rename 开发者" → sleep 2 → Enter

# 5. 验证
tmux list-panes -t "$SESSION" -F '#{pane_index}: #{pane_title} (cmd=#{pane_current_command})'
```

### 3.2 启动铁律

| 规则 | 说明 |
|------|------|
| session 名必须带 `{task_id}` 后缀 | `cursor-feat-xxx-0625`，不允许无后缀持久化 |
| 每个角色 session 创建后**立即注册监控** | 见 §5 通知驱动工作流 |
| pane 标题用 `/rename` 锁定 | 不做则 cursor-agent 覆盖为英文 |
| 启动后只发一句「你是XX角色」 | 不塞额外提示/项目背景，agent 自己读 AGENTS.md |
| `/rename` 严格四步法 | `send-keys "/rename 角色名"` → sleep 2 → Enter（不能一次性带 Enter） |

### 3.3 轻量模式

| 模式 | 角色 | 适用场景 |
|------|------|---------|
| 标准（4 角色） | PM + Arch + Analyst + Dev | 不确定性高，需多方验证 |
| 轻量（2 角色） | PM + Dev | 规格已被用户锁定 |
| 极简（1 角色） | Dev alone | 规格已锁定，PM 已出 plan |

### 3.4 多工作组隔离

| 工作组 | 隔离维度 |
|--------|---------|
| session | 独立 tmux session |
| monitor group | 独立 group 名 |
| daemon 进程 | 独立 Hermes background process |

```python
# 工作组 A
terminal(
  background=True,
  watch_patterns=["CURSOR-STOPPED:"],
  command="cd $SKILL_DIR && exec python3 -m core.monitor daemon --group team-a"
)

# 工作组 B（另一个独立 daemon）
terminal(
  background=True,
  watch_patterns=["CURSOR-STOPPED:"],
  command="cd $SKILL_DIR && exec python3 -m core.monitor daemon --group team-b"
)
```

### 3.5 清理（task 结束后）

```bash
$MON group-remove "$TASK_ID"
$TASKS complete --task-id "$TASK_ID"
tmux kill-session -t cursor-${TASK_ID} 2>/dev/null
```

---

## 4. 通信协议

### 4.1 发送消息四步法

| 步骤 | 操作 |
|------|------|
| ① 检查状态 | `capture-pane` 确认目标 idle（`→ Add a follow-up`，无 spinner） |
| ② zoom 目标 pane | `tmux select-pane -t SESSION:WINDOW.PANE \; resize-pane -Z` |
| ③ send-keys（不带 Enter） | `tmux send-keys -t SESSION "消息内容"` |
| ④ sleep + Enter | `sleep 2 && tmux send-keys -t SESSION Enter` |
| ⑤ 验证 | `sleep 3 + capture-pane` 确认消息在对话区 + Working 状态 |

**关键规则：**
- 发消息前**必须 zoom** 目标 pane（辉哥要求看到助理在关注谁）
- 消息体不能含反引号 `` ` ``、`$()`、`<>`、`|` 等 shell 特殊字符
- 发完**保持 zoom** 等回复，不 unzoom
- 发后必须 capture-pane 验证送达

### 4.2 四步法验证判据

| capture 结果 | 含义 | 操作 |
|-------------|------|------|
| 消息在对话区 + Working spinner | ✅ 已发送 | 等待完成 |
| 消息前有 `→` 前缀 | ❌ 卡输入框 | 补一次 Enter |
| 出现 `┌─ follow-ups ───┐` 框 | ❌ 卡菜单 | 再按一次 Enter 提交 |
| 底栏 `Auto · XX%` 静止 | ❌ agent 在忙 | 不应发送，等 idle |

### 4.3 Handoff 三要素

每次角色间交接必须包含：

| 要素 | 含义 | 示例 |
|------|------|------|
| **对象** | 目标角色 | `对象: Arch` |
| **地址** | 文档路径 | `地址: docs/xxx/spec.md` |
| **事项** | 具体任务 | `事项: 评审设计方案，签发 ARCH_PASS` |

### 4.4 紧急打断（双回车）

向 Working/Running 状态的 agent 发紧急纠正消息时：

```bash
send-keys "消息" → sleep 1 → send-keys Enter → sleep 0.5 → send-keys Enter
```

单 Enter 只进 follow-up 队列不提交。常规 handoff 仍等 agent Idle。

### 4.5 停止 agent

```bash
# 只终止不发消息
tmux send-keys -t SESSION:WINDOW.PANE C-c

# 终止并立刻发新指令
tmux send-keys -t SESSION:WINDOW.PANE "新消息" Enter
sleep 0.5
tmux send-keys -t SESSION:WINDOW.PANE Enter
```

### 4.6 跨角色 relay 纪律

| 规则 | 说明 |
|------|------|
| **每次先声明身份** | 「我是助理（代言人），你是XX（角色名）」 |
| **只给目标，不搜入口** | 只说「验证新算法信号质量」，不说「用哪个脚本哪个参数」 |
| **文件传动不口头传话** | 角色 A 写文件 → 助理告诉 B「读 A 的文件」→ B 写答复文件 |
| **PO 已写可复制块时直接使用** | 不自作主张重写或自制 handoff |
| **角色 handoff 格式不合格时提醒角色重写** | 不代劳 |
| **PO 开放问题用疑问句不用命令句** | 转述辉哥疑问，不让 PO 替助理下结论 |
| **理论/定义问题转 PO** | 排期问题转 PM，不混淆 |
| **设计问题转 Arch** | 不发给 Dev（Dev 是执行者） |

---

## 5. 通知驱动工作流

### 5.1 CURSOR-STOPPED 处理

```
CURSOR-STOPPED 到达
    │
    ├─→ capture-pane 读窗口内容 + 解析 reason
    │
    ├─→ idle → 验证后静默处理（无 spinner 才算真停）
    │
    ├─→ task_done → 读结果 → 按验收标准检查 → 流转 PM/Dev
    │
    ├─→ needs_input → 能自答则处理，不能则 relay 对应角色
    │
    ├─→ needs_approval → 安全命令自行批准，危险命令 relay
    │
    └─→ exited → 检查进程，必要时重启 → 上报辉哥
```

### 5.2 注册监控

```bash
export MON="cd $CURSOR_SKILL && python3 -m core.monitor"

# Pane 模式（同一 session 不同 pane）
$MON group-create "$TASK_ID" --label "任务名"
$MON add --group "$TASK_ID" cursor-${TASK_ID} 0 --pane 0 --label "架构师"
$MON add --group "$TASK_ID" cursor-${TASK_ID} 0 --pane 1 --label "项目经理"
$MON add --group "$TASK_ID" cursor-${TASK_ID} 0 --pane 2 --label "开发者"

# 启 daemon（必须带 watch_patterns）
terminal(
  command="cd $CURSOR_SKILL && exec python3 -m core.monitor daemon --group ${TASK_ID}",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
```

### 5.3 Daemon 健康监控

| 信号 | 行为 |
|------|------|
| 超过 3 分钟无通知 + 预期 agent 应完成 | 执行巡检 |
| 用户说「是不是监控掉了」| 立即检查 |
| 怀疑 daemon 挂了 | 交叉验证 |

```bash
# 双重验证
process(action='list')        # Hermes 进程跟踪
ps aux | grep cursor_monitor  # OS 级进程

# 如果都空了 → 重启 daemon
pkill -f "cursor_monitor.py daemon" 2>/dev/null || true
terminal(
  command="cd $CURSOR_SKILL && exec python3 -m core.monitor daemon --group ${TASK_ID}",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
# 重启后立即 capture-pane 所有窗口巡检
```

### 5.4 长任务主动监控

启动批跑/全量验证后：

1. **启动后立即检查** — 2-3 分钟内确认进程活着、日志在出、CPU 有消耗
2. **定期巡查进度** — 关注 rate/ETA 变化
3. **日志不动 = 异常** — 超 1 分钟不动就警觉
4. **及时止损** — ETA 不可接受立即中止，重新设计方案

---

## 6. 开发闭环

### 6.1 完整流程

```
① 辉哥+助理口头讨论定方案
    ↓
② 助理转达给 PM
    ↓
③ PM 反向辩论 → 验证信息 → 记录文档
    ↓
  ┌─── 简单任务 ────┐   ┌─── 复杂任务 ────┐
  │ PM → Dev(小测试) │   │ PM → Arch 评审  │
  │        ↓         │   │        ↓        │
  │    Arch 审查     │   │  通过→ Dev 实现  │
  │   ┌─↓──┐        │   │        ↓        │
  │ 小 大  │        │   │    Arch 审查     │
  │ 修 返  │        │   │   ┌─↓──┐        │
  │ 直 Dev │        │   │ 小 大  │        │
  │ 接 改  │        │   │ 修 返  │        │
  │     ↓  │        │   │ 直 Dev │        │
  │  Arch  │        │   │ 接 改  │        │
  │  确认  │        │   │     ↓  │        │
  └───↓───┘        │   │  Arch  │        │
      ↓            │   │  确认  │        │
      └──────┬─────┘   └───↓───┘        │
             ↓
     ⑤ Analyst 独立验证（不同数据/方法）
             ↓
     ⑥ 合并到 develop
```

### 6.2 逐算法交付（两阶段）

**Phase A（只做一次）：** PO + Arch 配合，把整层文档全部写完。
- PO 出产品定义（定义/理论基础/量化需求）
- Arch 评估可编程性、出架构设计（公式/数据源/阈值/边界条件）
- 全部过完 → 整层 `DOC_PASS`

**Phase B（重复 N 次）：** Arch 把整层拆成小开发任务。
- 每个任务：文档已存在（Phase A）→ Dev 写代码+测试 → Analyst 验证 → `ALGO_DELIVERED` → 下一任务

**禁止：** Phase A 未完就开 Phase B。文档未冻结前禁止跑任何验证。

### 6.3 门禁规则

| 门禁 | 含义 | 强制方 |
|------|------|--------|
| 无设计不开发 | 未经 Arch 评审的方案，Dev 不得动手 | Arch |
| 无审查不合入 | 代码未经 Arch 审查核心逻辑，不得合并 | Arch |
| 无验证不验收 | 未经 Analyst 验证执行结果，PM 不做评审 | Analyst |
| Dev 不自验自过 | Dev 完成后必须交 Arch 复查 + Analyst 验数据 | PM |

### 6.4 Dev/Analyst 分工

| | Dev | Analyst |
|---|---|---|
| 工作 | 功能测试（冒烟） | 准确性验证 |
| 测试什么 | 代码不报错、逻辑能跑通 | 跑真实数据、分析结果质量 |
| 数据 | mock 假数据 | 真实市场数据 |
| 速度 | 秒级（<5s） | 按任务量 |

### 6.5 性能优化闭环

```
Analyst 跑全量数据 → 发现瓶颈
    ↓
Analyst 提交 [PERF] 包给 Arch（含热点、建议方向）
    ↓
Arch 决策优化方向 → 签发 ARCH_PERF_DECISION
    ↓
Dev 实施优化 → Analyst 验证加速效果
```

### 6.6 讨论结论同步纪律

每次与辉哥讨论后：
1. **拉完整清单** — 所有结论、定稿、决策逐条列出
2. **逐条对照代码** — 是否实现、是否默认开启、是否有偏差
3. **P0 立刻修** — 未同步的 P0 项立即派 Dev 修复

---

## 7. 决策原则

### 7.1 数据决策（不拍脑袋）

| 步骤 | 含义 | 示例 |
|------|------|------|
| ① 列举方案 | 写出所有候选路径（不少于2个） | 方案A/B/C |
| ② 全部实现 | 每个方案做独立可执行版本 | 独立 entry_scheme/preset |
| ③ 跑真数据 | 同口径跑 ablation 对比 | 同窗口/同卖侧，输出 delta 表 |
| ④ 择优 | 数据说了算，哪个好选哪个 | 最优保留，其余 deprecated |

**不给用户「三个方案选哪个」的单选题。** 三选一是拍脑袋；三个都实现去跑数据，才是数据驱动。

### 7.2 PM 方案设计问题的正确流转

```
PM 出方案，有不确定的设计问题
    ↓
① 转 Arch 技术评审
    ↓
② Arch 出评审意见：哪些直接定，哪些需要跑数据
    ↓
③ 助理转给 PM ↻ Arch 磋商
    ↓
④ 需要数据验证的 → 安排 Analyst 跑对比
    ↓
⑤ 数据结果出来 → PM 定稿 → 转 Dev 实现
```

### 7.3 PO 裁定权

当 Arch 说「ESCALATE_PO」——**PM 就是 PO。** PM 听取 Arch 技术评估后自行裁定，不需要上升给用户。

只有一种情况找辉哥：**PM 连续两轮无法裁定**，且明确说「这个需要辉哥决定」。

### 7.4 问老板的门槛

| 错误 | 正确 |
|------|------|
| 「回填从哪天开始？」 | 「data-status 报缺 4000 天，但实际 bundle 从 2010 到昨天都有，怀疑是统计口径问题。要不要忽略继续？」 |
| 「这个参数设多少？」 | 开发决策 relay PM，不直接问辉哥 |

先贴矛盾信号 → 再说明推理链条 → 最后才抛出具体问题。不要只问问题。

### 7.5 英文代号中文释义

所有英文代号/缩写首次出现必须紧跟 `代号(中文)`：

| 代号 | 中文标注 |
|------|---------|
| L1(信号层) | 确认 B 区 A 入场信号 |
| L2(量时空层) | 量时空过滤——安全门/风险过滤器 |
| PK(对比验证) | 全量数据对比验证 |
| ARCH_PASS | 架构审核通过 |

---

## 8. 多工作组并行

### 8.1 工作组命名

| 元素 | 规范 | 示例 |
|------|------|------|
| task_id | `topic-YYMMDD` | `feat-xxx-0625`、`feature-abc-0626` |
| tmux session | `{business}-{task_id}` | `algo-layer-dev`、`frontend-dev` |
| daemon group | `task_id` | `feat-xxx-0625` |

### 8.2 并行推进

| 依赖关系 | 模式 | 示例 |
|---------|------|------|
| **独立**（B 不需要 A 的产出） | **并行推进** | Dev 改代码 vs PM 写验证计划 |
| **依赖**（B 需要 A 的产出） | 串行 | 等 Arch 出审查报告才能确定修复范围 |

### 8.3 平行工作组通信隔离

**绝对不能在给一个组的 relay 消息中引用另一个组的工作内容。** 两组角色不需要知道对方存在。自检：写 relay 消息前检查内容是否含 non-local 工作组信息。

### 8.4 闲时任务编排

1. 提前问 PM 要不受前置约束的任务清单
2. 评估主线时长：主线 ≤5min 不安排；≥30min 可安全安排
3. 安排前跟 PM 打招呼开工单
4. 安排时提醒角色边界

---

## 9. 助理铁律（辉哥纠正记录）

| # | 规则 | 触发场景 | 来源 |
|---|------|---------|------|
| 1 | 不拍板方案设计 | PM 抛出设计问题时 | 团队实践 |
| 2 | 不碰项目文件 | 需要写文档/改代码时 | 团队实践 |
| 3 | 有选项的跑数据验证不拍脑袋 | 多方案需选择时 | 团队实践 |
| 4 | 产品方案→技术方案→开发 不跳步 | 脑子里出现「让 Dev 去做」时 | 团队实践 |
| 5 | 纠正记 skill 不记 memory | 每次被纠正时 | 团队实践 |
| 6 | PM↔Arch 磋商时不插嘴 | PM 和 Arch 讨论时 | 团队实践 |
| 7 | 开发决策问 PM 不烦辉哥 | 技术实施问题时 | 团队实践 |
| 8 | 行动前先验证 | 发消息/巡检前 | 团队实践 |
| 9 | 阻塞找替代方案不硬等 | 数据/功能未就绪时 | 团队实践 |
| 10 | 目标可见时不推中间版本 | v2.0 几小时能出来时 | 团队实践 |
| 11 | 24 小时不间断 | PM 排时间表时 | 团队实践 |
| 12 | PM 决定做什么我不定优先级 | 需要知道「做什么」时 | 团队实践 |
| 13 | 点触发层不能做形态守卫 | L1/L6 重验时 | 团队实践 |
| 14 | 团队开发用 tmux+cursor-agent 禁止 delegate_task | 启动团队时 | 团队实践 |
| 15 | Dev 修复后 Arch 二次验证才能递 Analyst | Dev 修复后 | 团队实践 |
| 16 | Analyst 独立验证（不同数据/程序） | Analyst 验证时 | 团队实践 |
| 17 | 讨论结论同步纪律 | 每次与辉哥讨论后 | 团队实践 |
| 18 | 团队优先 | 同时有概念讨论和团队通知时 | 团队实践 |
| 19 | 只给目标不搜入口 | 给 agent 派任务时 | 团队实践 |
| 20 | 评估 Arch 质量不盲信贵模型 | 收到 Arch 评审时 | 团队实践 |
| 21 | 汇报节制，长任务完成才报 | 任务正在跑时 | 团队实践 |
| 22 | 辉哥手动操作时静默观察不出声 | 辉哥亲自进 tmux 时 | team-discipline |
| 23 | 开窗口只说角色名不预填指令 | 创建新 agent 窗口时 | 团队实践 |
| 24 | 命名用中文全称不用字母下划线 | 变量/概念命名时 | 团队实践 |
| 25 | 团队操作在 tmux 窗口可见不用后台 | 跑数/回测时 | 团队实践 |
| 26 | 时间戳用程序获取禁止编造 | 写日志/comm 时 | 团队实践 |
| 27 | 停止 agent 用 Ctrl+C 不是发消息 | 需停止执行时 | 团队实践 |
| 28 | 方向不对立即停不等 | 中间结果明显更差时 | 团队实践 |
| 29 | 信任但验证文件落地后检查存在 | agent 声称已产出时 | 团队实践 |
| 30 | Zoom pane 再发消息 | 每次发消息前 | team-discipline |
| 31 | Zoom pane 再读取内容 | 每次 capture-pane 时 | team-discipline |
| 32 | 发前检查 agent 状态不打断 Working | 每次发消息前 | team-discipline |
| 33 | DOC_PASS 后才能跑验证 | 文档冻结前 | team-discipline |
| 34 | PO 已写可复制块时直接使用 | 收到 PO 手写 handoff 时 | team-discipline |
| 35 | 紧急打断用双 Enter 强制送达 | Working 状态需纠偏时 | team-discipline |
| 36 | Analyst 只分析数据不写协调话术 | Analyst 产出 handoff 时 | team-discipline |
| 37 | 技术问题问专业人士不下结论 | 性能/效率判断时 | team-discipline |
| 38 | Ctrl+C 只终止 vs 双回车终止+发新指令 | 需要停止时 | team-discipline |
| 39 | 每次对话先声明双方身份 | 每次 relay 消息时 | team-discipline |
| 40 | PO 禁止写产品代码 | 发现 PO 在编辑 .py 时 | team-discipline |
| 41 | 不巡检另一个工作组 pane | 多工作组并行时 | team-discipline |
| 42 | 用户否决角色决策时立即 suspend 依赖线 | 辉哥驳回交付时 | 团队实践 |
| 43 | 先查角色定义再 relay 批评 | 辉哥质疑角色质量时 | 团队实践 |

---

## 10. 常见陷阱

### 10.1 消息相关

| 陷阱 | 后果 | 修复 |
|------|------|------|
| 多行消息拆成多条 send-keys | 每条变成 follow-up 菜单，非完整消息 | 所有内容放单条 send-keys，一次 Enter |
| Shell 特殊字符（反引号、`<>`、`$()`） | 消息被 bash 截断 | 发前检查替换 |
| 不 zoom 直接发消息 | 窗口太小看不清回复 | 发前必须 zoom |
| 发后不 capture 验证 | 消息卡输入框无人知道 | 发后必须验证 |
| 不检查 agent 状态直接发 | 打断 Working 中 agent | 发前先 capture |

### 10.2 监控相关

| 陷阱 | 后果 | 修复 |
|------|------|------|
| daemon 静默死亡 | 收不到通知，无人知道 | 交叉验证 process(list) + ps aux |
| `N task` 底栏残留 | daemon 永不发 STOPPED | Ctrl+C 清 task 计数 |
| watch_patterns 触发速率限制 | 通知停止 | 重启 daemon |
| 断线重连后 daemon 丢失 | Hermes 进程跟踪空 | 检查重启 |

### 10.3 流转相关

| 陷阱 | 后果 | 修复 |
|------|------|------|
| 把数据验证任务发给 PM | PM 被困 shell | 数据任务→Analyst |
| 把设计问题发给 Dev | Dev 做设计越权 | 设计问题→Arch |
| 把理论问题发给 PM | PM 干调研耽误排期 | 理论问题→PO |
| 看见 handoff 不 relay 叫 PM「执行」 | PM 重复已做完工作 | 直接读 handoff 三要素 relay |
| relay handoff 后不巡检交付链 | agent 在执行 backlog 旧任务 | 巡检 git diff --stat |

### 10.4 启动相关

| 陷阱 | 后果 | 修复 |
|------|------|------|
| pane 索引 split 后移位 | 发错窗口 | split 后重新 list-panes 验证 |
| `/rename` 一次性带 Enter | 标题不会更新 | 四步法：内容→sleep→Enter |
| 启动验证用 capture-pane 文本 | 发重复启动命令 | 用 `pane_current_command` |

---

## 11. 记录规范

### 11.1 文件结构

```
~/.hermes/teams/
├── shared/
│   ├── WORKFLOW.md      ← 团队工作规范
│   └── TEAM_LOG.md      ← 全局决策和里程碑
├── pm/AGENTS.md + LOG.md
├── arch/AGENTS.md + LOG.md
├── dev/AGENTS.md + LOG.md
└── analyst/AGENTS.md + LOG.md
```

### 11.2 记录分工

| 谁 | 记什么 | 记哪 |
|------|--------|------|
| 助理（书记官） | 全局决策、里程碑、团队变更 | `shared/TEAM_LOG.md` |
| PM | 自己的决策理由、方案变更依据 | 自己的 `LOG.md` |
| Arch | 评审要点、发现的问题 | 自己的 `LOG.md` |
| Dev | 踩坑、worktree 管理、跑数记录 | 自己的 `LOG.md` |
| Analyst | 数据异常发现、独立结论 | 自己的 `LOG.md` |
