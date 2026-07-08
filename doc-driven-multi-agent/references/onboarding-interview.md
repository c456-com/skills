---
title: Onboarding 访谈协议
type: reference
status: active
last-reviewed: 2026-07-03
---

# Onboarding 访谈协议

> AI Agent 如何执行团队配置访谈：触发条件、问题、答案处理和保存流程。

## 什么时候访谈

满足以下一个或多个条件时，启动访谈：

| 条件 | 触发 | 动作 |
|-----------|---------|--------|
| **首次使用** | `~/.config/skills/doc-driven-multi-agent/team-config.yaml` 不存在 | 提示“看起来这是你第一次使用，我问几个关于团队的问题。”然后自动启动访谈 |
| **强制重新配置** | 用户说 “reconfigure team”、“setup team”、“change team config” | 重新运行完整访谈；覆盖已有配置 |
| **配置过期** | 配置文件存在，但 `last_used` 超过 30 天 | 提示“你的团队配置已经 30+ 天没有更新，它仍然准确吗？(y/N)”；如果否，启动访谈 |
| **会话中检测到稳定团队** | 见下方 [稳定性检测](#稳定性检测) | 提示“团队结构看起来稳定，要保存为配置吗？” |

### 配置检测流程（决策树）

```
1. 检查：~/.config/skills/doc-driven-multi-agent/team-config.yaml 是否存在？
   ├─ 是 → 加载 → 检查 `last_used` 年龄
   │         ├─ >30 天 → 提示是否刷新
   │         └─ ≤30 天 → 提示 "Loaded team: {team_name}"；跳过访谈
   │
   └─ 否 → 检查：<project-root>/.skills/team-config.local.yaml 是否存在？
            ├─ 是 → 加载，并提示发现项目级覆盖
            └─ 否 → 启动 onboarding interview
```

## 访谈阶段

访谈是一个**对话序列**：一次只问一个问题，等待用户回答后再继续。不要一次性抛出所有问题。

### 阶段 1：团队身份

**问题：** “你的团队或项目叫什么名字？我会用它标记这份配置。”

**处理：** 将答案写入 `team_name`。默认值：`"我的 AI 团队"`。

---

### 阶段 2：启用哪些角色

**问题：** “这 5 个协议角色里，你的团队会用哪些？我列一下，你告诉我需要哪些即可：

1. **Project Manager (PM)**：计划、worktree、关闭
2. **Product Owner (PO)**：spec、产品决策、验收
3. **Architect (Arch)**：架构决策、代码评审
4. **Developer (Dev)**：实现、测试
5. **Data Analyst (Analyst)**：数据验证

你会用哪些角色？例如：‘all 5’、‘PM PO Arch Dev’、‘只有 Dev 和 PO’。”

**处理：**
- 如果用户说 “all” 或 “all 5” → 全部 `enabled: true`
- 如果用户列出具体角色 → 这些角色设为 `enabled: true`，其他设为 `false`
- 校验：至少必须启用 `po` + `dev`，否则协议无法完成设计与实现闭环

---

### 阶段 3：角色分配（每个启用角色一个子问题）

对每个启用角色询问：

**问题：** “谁扮演 **{Role Name} ({Code})**？可选：Hermes Agent、Cursor Agent、Claude Code、GitHub Copilot 或人类。”

**示例：**
- PM：“谁扮演 Project Manager (PM)？”
- Dev：“谁扮演 Developer (Dev)？”

**处理：** 将 `played_by` 设为用户答案，并把 `agent_type` 映射为：

| 用户说法 | agent_type |
|-----------|------------|
| "Hermes", "Hermes Agent", "myself" | `hermes` |
| "Cursor", "Cursor Agent" | `cursor-agent` |
| "Claude", "Claude Code" | `claude-code` |
| "Copilot", "GitHub Copilot" | `copilot` |
| "Human", "a person", "my boss", "人类" | `human` |

如果 `agent_type` 是 `cursor-agent`，继续问：“这个角色有 tmux session 模板吗？例如 `cursor-arch-{task}`。” → 设置 `session_template`。

**可选追问：** “这个角色还有备注吗？例如具体是谁，或特殊指令。” → 设置 `notes`。

---

### 阶段 4：Worktree 偏好

**问题：** “你是否使用 git worktree 做并行任务隔离？多 Agent 场景推荐使用。(Y/n)”

**处理：**
- Y 或空输入 → `use_worktrees: true`
- N → `use_worktrees: false`

---

### 阶段 5：CI 命令

**问题：** “handoff 前你用什么命令跑测试 / CI？默认是 `make ci`。”

**处理：** 将答案写入 `preferred_ci`。如果用户说 “default” 或留空，则保留默认值。

---

### 阶段 6：时区

**问题：** “comm log 时间戳使用哪个时区？默认 `Asia/Shanghai`，直接回车则使用默认。”

**处理：** 将答案写入 `timestamp_tz`。如可行，按 IANA timezone 列表校验；否则原样接受。

---

### 阶段 7：文档路径（可选深入）

**问题：** “协议默认使用 `docs/superpowers/specs/`、`docs/superpowers/comms/` 等路径。这些路径适合你的项目吗，还是你使用不同目录？（默认即可 / 自定义）”

- 如果用户说“默认即可” → 保留默认值，跳过子问题
- 如果用户说“自定义” → 一次问一个：
  1. “Spec 文档目录？”（默认：`docs/superpowers/specs/`）
  2. “Comm log 目录？”（默认：`docs/superpowers/comms/`）
  3. “Plan 目录？”（默认：`docs/superpowers/plans/`）
  4. “Review 目录？”（默认：`docs/superpowers/reviews/`）
  5. “Daily log 目录？”（默认：`docs/ops/daily/`）
  6. “Worktree 目录？”（默认：`.worktrees/`）

---

## 保存流程

所有阶段完成后：

1. **构造 YAML**：把所有答案组装成 schema
2. **设置时间戳**：`created` 和 `last_used` 使用当前时间（`TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'`）
3. **确保目录存在**：`mkdir -p ~/.config/skills/doc-driven-multi-agent/`
4. **写入文件**：`~/.config/skills/doc-driven-multi-agent/team-config.yaml`
5. **提示成功：**

```
团队配置已保存到 ~/.config/skills/doc-driven-multi-agent/team-config.yaml

下次加载此技能时，我会记住你的团队并跳过访谈。

之后如需修改：
  - 说 “reconfigure team” 重新运行访谈
  - 或用任意文本编辑器直接编辑该文件
  - 如需项目级覆盖，创建 .skills/team-config.local.yaml
```

## 错误处理

| 情况 | 响应 |
|-----------|----------|
| 用户回答不清楚 | 追问澄清，例如：“我听到你说 Dev 和 PO，你还需要 PM 或 Architect 吗？” |
| 用户说 “skip” 或 “I don't know” | 对该字段使用默认值，并在配置中用 `# auto-default` 注明 |
| 用户中断或切换话题 | 回到话题后复述：“我们刚才在设置团队配置，上一个问题是 {phase}。要继续吗？” |
| YAML 写入失败（权限） | 说明问题：“无法写入 ~/.config/skills/...，权限不足。请手动创建目录：mkdir -p ~/.config/skills/doc-driven-multi-agent” |

## 重新配置

当用户说 “reconfigure team”：

1. 询问：“你想从头开始覆盖全部配置，还是只更新特定字段？”
2. 完整重配 → 运行全部 7 个阶段
3. 部分更新 → 询问要改哪个字段，只更新 YAML 中该字段

## 稳定性检测

在会话协议的结束 checklist 中检测（见 SKILL.md）：

```
同一套角色分配跑完 3+ 个 feature cycle，且尚未存在 team-config.yaml：
  → 询问：“你的团队结构看起来已经稳定。要保存为默认团队配置吗？
          这样下次会话我就不用再询问团队结构了。”
```

如果用户同意 → 运行 mini-interview（只问阶段 1 + 阶段 2 → 保存），或如果当前会话已有完整信息，则直接构造配置。

## 项目级覆盖检测

加载配置时：

1. 从 `~/.config/skills/doc-driven-multi-agent/team-config.yaml` 加载全局配置
2. 检查 `<project-root>/.skills/team-config.local.yaml`
3. 如果本地覆盖存在：
   - 提示：“Found project-specific overrides in .skills/team-config.local.yaml”
   - 深度合并字段（嵌套对象合并，不整体替换）
   - `roles.*`：逐角色设置合并
   - `document_paths`：逐路径覆盖合并
   - `engineering`：逐字段合并
   - `team_name`、`created` 保持全局配置值
