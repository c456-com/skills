---
title: 团队配置 Schema 参考
type: reference
status: active
last-reviewed: 2026-07-03
---

# Team Config Schema

> `team-config.yaml` 保存团队结构、角色分配、文档路径和工程偏好，避免技能每次会话都重新询问。

## 文件位置

| 范围 | 路径 | 行为 |
|-------|------|----------|
| **全局（跨项目共享）** | `~/.config/skills/doc-driven-multi-agent/team-config.yaml` | 每次调用技能时自动加载。可由 onboarding interview 创建，也可手动创建。 |
| **项目级覆盖** | `<project-root>/.skills/team-config.local.yaml` | 如果存在，会深度合并到全局配置上。只需填写要覆盖的字段。 |

Agent 会先检查全局配置；如果存在则加载。随后检查项目级覆盖；如果存在，则把字段深度合并到全局配置上（例如 `roles.*` 这样的嵌套字段会逐项合并，而不是整体替换）。

## 完整 Schema

```yaml
# ~/.config/skills/doc-driven-multi-agent/team-config.yaml
version: "1.0"
team_name: "我的 AI 团队"
created: "2026-07-03T14:30CST"
last_used: "2026-07-03T14:30CST"

# ── 角色 ──────────────────────────────────────────────────────
# 协议中的 5 个角色。enabled=false 表示该角色会在 handoff 链路中跳过
# （例如你的团队暂时不需要 Analyst）。
roles:
  project_manager:
    enabled: true
    played_by: "Hermes Agent"                # 人类可读名称
    agent_type: "hermes"                     # hermes | cursor-agent | claude-code | copilot | human
    session_template: ""                     # 例如 tmux session 使用 "cursor-pm-{task}"
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
    notes: "暂时不需要"

# ── 文档路径 ───────────────────────────────────────────────────
# 协议文档在项目中的位置。
# 如果你的项目使用不同目录结构，可以修改这些路径。
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

# ── Feature Slug 约定 ──────────────────────────────────────────
# 生成新 feature slug 的模板。
# 可用变量：{tag}, {date}, {ticket}
feature_slug_pattern: "{tag}-{date}"

# ── Handoff 链路 ───────────────────────────────────────────────
# 角色交接工作的默认顺序。
# 这是协议默认值；如果团队流程不同，可以覆盖
# （例如没有 Analyst，或 Arch 在 Dev 开工前预审）。
handoff_chain:
  - "po"          # 设计 / spec
  - "pm"          # plan / 排期
  - "arch"        # 预审（复杂任务，在 Dev 前）
  - "dev"         # 实现
  - "arch"        # 代码评审
  - "analyst"     # 数据验证（如果 disabled 则跳过）
  - "po"          # 产品验收
  - "pm"          # 关闭

# ── 工程偏好 ───────────────────────────────────────────────────
engineering:
  use_worktrees: true
  preferred_ci: "make ci"
  timestamp_tz: "Asia/Shanghai"
```

## 字段参考

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|-------|------|----------|-------------|
| `version` | string | 是 | Schema 版本（当前为 `"1.0"`） |
| `team_name` | string | 是 | 人类可读的团队名称 |
| `created` | string | 是 | 配置首次创建时的 ISO 时间戳 |
| `last_used` | string | 自动 | 每次加载配置时更新 |
| `roles` | object | 是 | 角色分配，见下文 |
| `document_paths` | object | 是 | 文档目录布局 |
| `feature_slug_pattern` | string | 否 | 自动生成 feature slug 的模板 |
| `handoff_chain` | array | 是 | handoff 流水线中的角色顺序 |
| `engineering` | object | 是 | CI、worktree、时区偏好 |

### Roles.`<role>`

每个 role key 是以下之一：`project_manager`、`product_owner`、`architect`、`developer`、`data_analyst`。

| 字段 | 类型 | 必填 | 说明 |
|-------|------|----------|-------------|
| `enabled` | boolean | 是 | 该角色是否在团队中启用 |
| `played_by` | string | 否 | 扮演该角色的人或 Agent 的可读名称 |
| `agent_type` | string | 否 | 可选值：`hermes`、`cursor-agent`、`claude-code`、`copilot`、`human` |
| `session_template` | string | 否 | tmux session 名称模板（如 `cursor-arch-{task}`），仅在使用具体 `tmux-*-agent` 技能时相关，例如 `tmux-cursor-agent` |
| `notes` | string | 否 | 关于该角色分配的自由文本备注 |

### Document Paths

| 字段 | 默认值 | 说明 |
|-------|---------|-------------|
| `root` | `.` | 项目根目录，通常保持默认 |
| `workflow` | `docs/ops/` | 工作流文档 |
| `product` | `docs/product/` | 产品目标和决策 |
| `specs` | `docs/superpowers/specs/` | Feature 规格文档 |
| `comms` | `docs/superpowers/comms/` | 沟通日志 |
| `plans` | `docs/superpowers/plans/` | 任务计划 |
| `reviews` | `docs/superpowers/reviews/` | 验证评审 |
| `daily` | `docs/ops/daily/` | 工程日报 |
| `worktrees` | `.worktrees/` | Git worktree 目录 |

### Handoff Chain

每一项都是角色代码：`pm`、`po`、`arch`、`dev`、`analyst`。顺序定义流水线；`enabled: false` 的角色会自动跳过。

### Engineering

| 字段 | 默认值 | 说明 |
|-------|---------|-------------|
| `use_worktrees` | `true` | 是否用 git worktree 做任务隔离 |
| `preferred_ci` | `make ci` | handoff 前运行的 CI 命令 |
| `timestamp_tz` | `Asia/Shanghai` | comm log 时间戳使用的 IANA 时区 |

## 项目级覆盖示例

在项目根目录创建 `.skills/team-config.local.yaml`，覆盖特定字段：

```yaml
# .skills/team-config.local.yaml — 只覆盖当前项目的全局配置
document_paths:
  specs: "docs/specs/"            # 当前项目使用不同 spec 目录
  comms: "docs/handoffs/"

engineering:
  preferred_ci: "pnpm ci"         # 当前项目使用不同 CI 工具
```

只会合并指定字段；其他字段继续使用全局配置。

## 自动生成

此文件可由 onboarding interview 自动生成，详见 [onboarding-interview.md](onboarding-interview.md)。你也可以：

- **手动编辑**：用任意文本编辑器，保持 YAML 语法
- **重新访谈**：在聊天中说 “reconfigure team”
- **复制模板**：用 [templates/team-config.yaml](../templates/team-config.yaml) 作为起点
