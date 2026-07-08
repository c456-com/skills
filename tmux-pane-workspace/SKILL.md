---
name: tmux-pane-workspace
description: "Tmux pane workspace / zoom / layout / meeting：当用户要在 tmux 中聚焦或放大 pane、读取/输入/发送消息、管理多 pane 工作区、创建圆桌会议/多窗口讨论、维护会议日志、从 Agency Agents 等职业角色库选择专家 pane，或为 tmux-cursor-agent、tmux-trae-agent、tmux-codex-agent 等具体 Agent 技能提供 workspace 边界时触发；用于通用 pane 可见性、布局与会议协作。"
version: 2.1.0
related_skills:
  - tmux-cursor-agent
  - doc-driven-multi-agent
---

# Tmux Pane Workspace

本技能定义 tmux pane 工作空间的通用规范：聚焦、放大、布局、会议工作区、会议日志，以及不同 `tmux-*-agent` 技能接入同一 workspace 的边界。

它不关心 pane 里运行的是 shell、编辑器、日志、Cursor Agent、Trae Agent、Codex，还是其他程序。具体程序的状态判断、消息发送协议、登录、恢复和监控，由对应的 `tmux-*-agent` 技能负责。

核心原则：**与哪个窗口或 pane 对话，就把哪个 pane 选中并放大；要让多个 pane 协作，就先把 workspace 布局和日志规则定义清楚。**

---

## 职责边界

| 能力 | 本技能负责 | 具体 Agent 技能负责 |
|------|------------|--------------------|
| pane 可见性 | `select-pane`、`resize-pane -Z`、读取前聚焦 | 判断 Agent 是否可接收消息 |
| workspace 布局 | 多列、网格、聚焦、恢复 | 启动具体 Agent 进程 |
| 圆桌会议 | 主题、目的、约束、议程、日志结构 | 具体消息投递方式和停止信号 |
| pane 角色 | 记录和验证 pane 标题 / 角色 | 询问具体 Agent 身份、读取其回复 |
| 扩展接口 | 定义 `tmux-*-agent` 应提供哪些能力 | 实现 Cursor / Trae / Codex 等专属协议 |

已有实现：

- `tmux-cursor-agent`：Cursor Agent over tmux 的启动、状态检测、四步消息协议、daemon 与恢复。

未来可增加：

- `tmux-trae-agent`：Trae Agent over tmux 的运行协议。
- `tmux-codex-agent`：Codex over tmux 的运行协议。

---

## 基础 Pane 操作

### 先选中，再放大

在读取、输入、发送消息、观察输出前，先聚焦目标 pane：

```bash
tmux select-pane -t session:window.pane \; resize-pane -Z
```

不要直接对未激活的 pane 调用 `resize-pane -Z -t ...`。稳定做法是：先 `select-pane`，再 `resize-pane -Z`。

### 读取时保持可见

使用 `capture-pane` 前，也先选中并放大目标 pane。这样用户能看到你正在关注哪个窗口，避免基于错误 pane 做判断。

```bash
tmux select-pane -t session:window.pane \; resize-pane -Z
tmux capture-pane -t session:window.pane -p -S -20
```

如果已经放大到同一个 pane，可以直接读取；如果要切换对话对象，先切换并放大新的 pane。

### 对话时跟随对象

当你要和某个 pane 交互：

1. 选中目标 pane。
2. 放大目标 pane。
3. 读取当前内容，确认它就是要交互的对象。
4. 按具体 Agent 技能规定的协议输入或发送内容。
5. 发送后再次读取少量输出，确认内容已进入目标 pane。

发送后默认保持目标 pane 的放大状态，让用户继续看到后续输出。

### 缩小与切换

当需要回到总览或切换到另一个 pane：

```bash
tmux resize-pane -Z
tmux select-pane -t session:window.other-pane \; resize-pane -Z
```

如果当前已经处于 zoom 状态，第一次 `resize-pane -Z` 会缩小；选中新 pane 后再次 `resize-pane -Z` 会放大新 pane。

`resize-pane -Z` 不会改变 pane 索引。真正需要避免的是 `swap-pane`、重排布局脚本或手动拆分导致的 pane 索引和角色映射漂移。

---

## Workspace 布局

### 常用布局

| 目标 | 命令 | 使用场景 |
|------|------|----------|
| 网格总览 | `tmux select-layout -t session:window tiled` | 同时观察多个 pane |
| 横向多列 | `tmux select-layout -t session:window even-horizontal` | 多个角色同时输出短内容 |
| 纵向多行 | `tmux select-layout -t session:window even-vertical` | 逐段阅读长输出 |
| 聚焦单 pane | `tmux select-pane -t session:window.pane \; resize-pane -Z` | 与某个 pane 对话 |
| 恢复总览 | `tmux resize-pane -Z` | 从聚焦回到总览 |

### 动态布局脚本

可将 [`scripts/layout.sh`](scripts/layout.sh) 放到项目或技能目录中使用：

```bash
bash scripts/layout.sh grid
bash scripts/layout.sh cols
bash scripts/layout.sh focus PM
bash scripts/layout.sh zoom
```

默认脚本使用环境变量配置目标：

```bash
TMUX_WORKSPACE_SESSION=roundtable TMUX_WORKSPACE_WINDOW=Agents bash scripts/layout.sh grid
```

---

## 会议工作区

在打开任何 pane 之前，先定义会议六要素：

1. **主题**：讨论什么，例如“产品升级方向”或“架构方案评审”。
2. **目的**：为什么讨论，例如“评估可行性”或“决定 Go/No-Go”。
3. **约束条件**：团队规模、预算、时间线、目标成果。没有约束时，Agent 往往默认假设资源充足。
4. **角色与交付物**：每个 pane 的角色和预期输出。
5. **议程**：谁先发言，谁评审，谁总结。
6. **输出文件**：会议日志、时间线、最终结论写到哪里。

### 可选角色来源

如果会议需要默认 PM / Arch / Dev / Analyst 之外的专家视角，可以参考 [Agency Agents](https://github.com/msitarzewski/agency-agents) 选择职业角色。先按主题检索 Growth、Security、Finance、UX、QA、SRE、Legal、Marketing 等角色，再把其职责和交付物压缩成当前 pane 的角色定义。

本技能已整理一份速查参考：[references/agency-agents-roster.md](references/agency-agents-roster.md)。它不是硬依赖；没有下载上游仓库时，也可以直接手写角色定义。

### 会议日志建议

```text
MEETING_TIMELINE.md       # 主持人维护的时间线索引
MEETING_LOG_HOST.md       # 主持人日志
MEETING_LOG_PM.md         # 角色个人日志
MEETING_LOG_ARCH.md
MEETING_LOG_DEV.md
MEETING_LOG_ANALYST.md
```

每段发言建议格式：

```markdown
## T01 | 角色名 | 2026-07-08T15:30CST | Opinion

正文内容。

---
```

### 推荐讨论流程

| 阶段 | 方式 | 说明 |
|------|------|------|
| 第一轮：开场陈述 | 并行或顺序 | 每个角色独立给初始观点 |
| 第二轮：交叉碰撞 | 中继 | 主持人把关键观点转给特定角色评审 |
| 第三轮：收敛 | 并行或指定总结者 | 要求每个角色给唯一建议或风险 |
| 最终总结 | 主持人 | 写入时间线和最终结论 |

如果会议要做决策，优先使用顺序讨论，避免同时广播后得到多份互不相干的报告。

---

## Agent-Agnostic 接口

任何未来的 `tmux-*-agent` 技能接入 workspace 时，应该说明以下能力：

| 接口 | 说明 |
|------|------|
| 启动命令 | 如何在目标 pane 中启动 Agent |
| 就绪判断 | 如何确认 Agent 已登录、信任工作区并可接收输入 |
| 状态检测 | 如何判断 executing / stopped / waiting / exited |
| 安全发送 | 如何把消息投递到 Agent，而不是 shell 或输入残留 |
| 停止 / 恢复 | 如何取消当前执行、优雅退出、resume 会话 |
| pane 角色验证 | 如何确认某个 pane 里的 Agent 实际扮演哪个角色 |
| monitor 集成 | 如支持 daemon 或通知，说明注册方式和事件格式 |

本技能只消费这些接口，不复制具体实现。

---

## 常见陷阱

| 陷阱 | 症状 | 修复方法 |
|------|------|----------|
| 没选中就 zoom | 放大的不是目标 pane，或焦点没有切过去 | 始终使用 `select-pane ... \; resize-pane -Z` |
| 切换对象后未放大 | 用户看不出你正在和谁交互 | 每次换对象都重新 select + zoom |
| 读取错 pane | 基于错误窗口做判断 | 读取前确认目标 `session:window.pane` |
| 把会议协议写进聊天 | 下个 Agent 找不到上下文 | 写入会议日志或 `doc-driven-multi-agent` 的 comm log |
| 广播给所有 pane | 得到多份孤立报告 | 决策型会议使用顺序讨论和主持人中继 |
| 依赖 pane 标题 | 角色和 pane 对不上 | 发送前用具体 Agent 技能验证身份 |
| 使用 `swap-pane` 重排 | pane 索引 / 角色映射漂移 | 用 `resize-pane -Z` 聚焦，重排后重新 `list-panes` |
