---
name: doc-driven-multi-agent
category: autonomous-ai-agents
tags: [multi-agent, coordination, document-driven, handoff, roles, SOP, workflow, protocol]
description: "文档驱动多代理协作 / document-driven multi-agent：当用户要定义 AI Agent 角色 SOP、handoff 三要素、G0-G4 门禁、越界拒绝、团队配置持久化或跨平台协作协议时触发；适用于 Cursor/Claude Code/Copilot/Gemini/Hermes 等。"
version: 1.2.0
triggers:
  - 启动/重启多代理协作 session 时
  - 需要定义 AI Agent 角色及其职权边界时
  - 角色间需要通过文档 handoff 交接工作时
  - 代理不确定自己的角色或收到越界请求时
  - 设计/实现/验收流程需要通过 G0–G4 门禁控制时
  - 首次使用需要配置团队架构时
  - 需要保存或加载团队配置时
  - 团队配置过时需要更新时
related_skills: [tmux-pane-workspace, tmux-cursor-agent, c456-team-work, c456-software-dev-sop]
---

# 文档驱动多代理协作协议

通过**文档驱动的交接**协调多个 AI Agent，而不是依赖聊天记录传话。每个决策、任务流转和评审都必须写入项目文档，形成可审计、可追溯的责任链。

> **核心规则：** 没有文档 = 没有交接 = 不能开工。

---

## 为什么用文档驱动，而不是聊天驱动

| 方式 | 问题 |
|----------|---------|
| 聊天交接 | 信息埋在对话历史里，下一个 Agent 很难定位 |
| 只在会话里决策 | 会话结束或模型切换后容易丢失 |
| 口头分派任务 | 边界模糊，没有审计记录 |
| **文档驱动** | 每次交接、决策和评审都有稳定文件路径 |

这个协议来自在同一个代码库中运行 4–5 个 AI Agent 角色（PM、PO、Architect、Developer、Analyst）的实践；每个 Agent 都在独立会话里工作。关键原则是：**Agent 之间不直接聊天，它们为彼此写文件。** `comm` log（沟通日志）就是跨会话、跨模型、跨平台保存下来的共享记忆。

---

## 文档链（事实来源层级）

```
AGENTS.md                        ← 入口文件（每个 Agent 的必读清单）
  └── WORKFLOW.md                ← 标准工作流（本协议）
        └── GOALS.md             ← 产品 / 项目目标
              └── spec           ← 要做什么 + 验收标准
                    ├── comm     ← 沟通日志（决策、交接）
                    ├── plan     ← 带 checkbox 的任务拆解
                    └── code     ← worktree 实现与测试
                          └── review  ← 验证证据
                                └── daily  ← 工程日报
```

| 文档 | 路径约定 | 用途 | 维护者 |
|----------|----------------|---------|------------|
| 入口 | `<root>/AGENTS.md` | 会话必读清单 | 所有 Agent 读取 |
| 工作流 | `docs/ops/WORKFLOW.md` | 完整协议 | 所有 Agent 读取 |
| 目标 | `docs/product/GOALS.md` | 高层目标 | PO |
| 规格 | `docs/superpowers/specs/<feature>.md` | 要做什么 + 验收标准 | PO |
| **沟通日志** | `docs/superpowers/comms/<feature>.md` | **决策、交接、关键上下文** | **所有 Agent 追加** |
| 计划 | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` | 带 checkbox 的任务项 | PM |
| 评审 | `docs/superpowers/reviews/<feature>-YYYY-MM-DD.md` | 验证证据 | Arch / Analyst |
| 日报 | `docs/ops/daily/YYYY-MM-DD.md` | 工程日总结 | 所有 Agent |

**铁律：**
- **Comm Log** = 沟通与决策的唯一事实来源（SoT）
- **Spec / Plan** = 需求与任务的唯一事实来源
- **Reviews** = 验证证据的唯一事实来源
- 只有聊天记录，永远不足以完成交接或记录决策

---

## 五角色模型

协议定义五个角色，每个角色都有**严格职责和硬边界**。每个 Agent 开工前必须知道自己当前扮演的角色；如果不确定，必须停下来询问。

| 角色 | 代码 | 职责 | 写代码？ | 关键产出 |
|------|------|---------------|:------------:|------------------|
| **Project Manager** | `PM` | 任务规划、worktree 生命周期、G4 关闭 | **否** | plan、comm、worktree 管理 |
| **Product Owner** | `PO` | 产品定义、spec 编写、验收签字 | **否** | spec、验收决策、理论引用 |
| **Architect** | `Arch` | 架构决策（ADR）、代码评审、少量直接修正 | **有限** | ADR、arch-review、小修 |
| **Developer** | `Dev` | **唯一主要代码编写者**，负责实现与测试 | **是** | code、tests、验证证据 |
| **Data Analyst** | `Analyst` | 数据验证、bug 报告、验收证据 | **否** | review 报告、DATA_PASS/FAIL |

### 角色边界

| 角色 | 可以做 | 不能做 |
|------|--------|-----------|
| PM | 计划、排期、创建/合并/清理 worktree | 写产品代码、跑数据分析、做代码评审 |
| PO | spec、产品决策、验收、理论引用 | 写代码、修改架构 ADR |
| Arch | ADR、代码评审、小范围直接修正（命名/错别字/明显 bug） | 未经 PO 修改产品定义；承接完整 Dev 任务 |
| Dev | worktree 中写代码和测试、实现说明 | 修改 spec、PO 文档、ADR；未审批扩 scope |
| Analyst | 数据验证、带复现步骤的 bug 报告 | 修改产品代码、spec 或架构文档 |

### 升级链路

```
Dev 实现问题 / blocker ──→ Arch
Arch 发现产品语义问题 ──→ PO (ESCALATE_PO)
Arch 发现排期 / 范围影响 ──→ PM (ESCALATE_PM)
Analyst 发现数据 bug ──→ Dev（代码）| Arch（架构）| PO（产品定义）
```

**Dev 永远不能绕过 Arch 直接找 PO 改 spec。** 所有沟通必须沿链路流转。

---

## Handoff 协议（三要素）

这是本协议的**核心机制**。任意角色之间交接任务，都必须在 comm log 中写入结构化区块，并包含三要素：

| 要素 | 字段名 | 要求 |
|---------|-----------|-------------|
| **Target** | `对象` | 角色全名 + code，例如 `Developer (Dev)` |
| **Address** | `地址` | 仓库路径（当前 comm、spec、plan、review、code 等），至少 1 个 |
| **Task** | `事项` | 用一两句话说明下一个角色要做什么 |

### 标准 Handoff 区块

```markdown
**Handoff:**
- **Target:** Developer (Dev)
- **Address:** `docs/superpowers/comms/<feature>.md`（当前条目）, `docs/superpowers/specs/<feature>.md`
- **Task:** 按 spec §4 验收标准实现 plan Task 3.2；只在 worktree `.worktrees/feat-<topic>` 中工作
```

### 无效 Handoff（下一个 Agent 必须拒绝）

- Handoff 只存在于聊天 / Agent 回复中，没有写进 comm log
- comm log 里有 Handoff，但缺少 target、address 或 task 中任意一个（缺一项 → `BLOCKED`）
- 决策只存在于会话对话中，没有写入 comm/spec/plan/review
- 返工项只在 PR comments 里，没有登记到 comm entry
- 用 `@role` 或口头通知代替**追加 comm log**

### 接收 Handoff（开工前检查）

下一个 Agent 开工前必须：

1. 打开 comm log，找到最新一条 **Target** 匹配当前角色的记录
2. 确认 target、address、task 三项齐全；否则 → `BLOCKED: invalid handoff`
3. 阅读 `Address` 和 `Read:` 字段列出的所有文档
4. 在 comm 或会话回复中声明已读列表

---

## 门禁（G0–G4）

协议定义五个门禁控制工作推进。未满足门禁条件时，不得进入下一阶段：

| 门禁 | 名称 | 负责人 | 条件 |
|------|------|-------|-----------|
| **G0** | 启动 | PM + PO | `comms/<feature>.md` + spec 占位存在，或 `Status: exploring` |
| **G1** | 设计冻结 | PO | spec status ≠ `draft`；comm 中有 PO 的 `APPROVED` |
| **G2** | 实现放行 | PO | plan 存在；PO 在 comm 中分派 Dev；复杂任务需要 Arch 预审通过 |
| **G3** | 产品验收 | PO | Analyst `DATA_PASS` + review 文档；PO 签署 `PRODUCT_ACCEPTED` |
| **G4** | 关闭 | PM | 三方 `COMMIT_DONE`；合并 + 清理 worktree；记录 `TASK_CLOSED` |

**例外：** ≤3 个文件的小改动，或 comm 标记 `EXCEPTION: trivial` 并列出文件清单时，可以跳过 G1/G2。

---

## 会话协议（每个 Agent 必须遵守）

### 开始前（Checklist）

- [ ] 如果角色未知 → **停下来询问**当前被分配的角色；确认后再读对应 role SOP
- [ ] 阅读 AGENTS.md → WORKFLOW.md（本协议）→ role SOP
- [ ] 如果可用，调用 Superpowers 技能（先 `using-superpowers`，再调用阶段技能）
- [ ] 确认 feature slug；如果没有 → 进入 G0：创建 comm + spec 占位
- [ ] 完整阅读 **spec → plan → comm log**，并阅读相关模块文档 + GOALS
- [ ] 确认 **worktree** 路径；新功能禁止在 main workspace 工作，应采用 `using-git-worktrees` 模式
- [ ] 在回复或 comm 中声明已读列表
- [ ] **跨角色 handoff 检查：** 找到 Target 匹配当前角色的 comm entry；缺失或无效 → `BLOCKED: invalid handoff`

### 工作中

- 只修改 plan 范围内的文件
- 决策和 handoff 必须写入 comm log，**不能只写在聊天里**
- 聊天不能替代 comm handoff
- 策略 / 方向变化 → 追加专门的方向记录

### 结束前（Checklist）

- [ ] Comm timestamp：运行 `TZ='Asia/Shanghai' date +'%Y-%m-%dT%H:%M%Z'`，**不要编造时间戳**
- [ ] **追加 comm**，必须包含：`agent=`、`Skills used:`、`Read:`、`Said / Decided:`、**Handoff 三要素**、`Blockers:`
- [ ] 更新当前角色负责的文档（plan checkbox、review、ADR、daily log）
- [ ] **回复人类用户**，附上可复制的 handoff block（第一人称，fenced markdown）
- [ ] **团队稳定性检查**：如果同一套角色已稳定跑完 3+ 个 feature，且尚未保存 team config，询问：“团队结构看起来已经稳定，要保存为下次会话的默认配置吗？”（保存到 `~/.config/skills/doc-driven-multi-agent/team-config.yaml`）
- [ ] 更新 daily log（`docs/ops/daily/YYYY-MM-DD.md`）
- [ ] 通过角色对应的验证检查（Dev 跑 `make ci`，Arch/Analyst 写 review 文档）

---

## 边界执行（越界拒绝）

当 Agent 收到**明显超出自身角色边界**的请求时，即使请求来自人类，也必须主动拒绝，而不是直接执行：

| 轮次 | Agent 响应 |
|-------|---------------|
| **第 1 次请求** | **拒绝。** 说明应该由哪个角色处理；建议 comm handoff 路径；**不执行** |
| **第 2 次请求**（坚持） | **再次拒绝。** 重申边界以及破坏角色隔离的风险 |
| **第 3 次请求**（明确书面确认） | 可例外执行；comm log 必须记录 `OVERRIDE_ROLE_BOUNDARY` + 确认原文 |

**“明确确认”的定义：** 在 ≥2 次拒绝后，请求者必须书面明确说明希望**当前这个角色**执行该工作。模糊的“继续”“就这么做”“你决定”不算确认。

### 拒绝话术

```
我是 <Role Name> (<Code>)。你请求的任务（“<task summary>”）属于
<Correct Role Name> (<Code>)，不属于我的角色边界。我不会执行它。

正确路径：
1. comm Handoff → Target: <Correct Role>
2. Address: <spec/plan/review path>
3. Task: <该角色要做什么>

请为 <Correct Role> 打开一个会话，或请人类转发上面的 Handoff。

如果你仍坚持让我以 <current role> 身份执行，请在第 3 次或之后明确书面确认；
确认后我会记录 OVERRIDE_ROLE_BOUNDARY 并继续。
```

---

## 默认交付链路（Happy Path）

```
Step 1:  PM + PO      启动 ──→ comm + spec 占位
Step 2:  PO            设计冻结 ──→ spec `approved`，comm `APPROVED` → PM
Step 3:  PM            排期 ──→ 带任务的 plan，comm schedule → Arch（复杂）| PO（简单）
Step 4*: Arch          预审 ──→ comm `ARCH_PRE_PASS` + 必要 ADR → PO
Step 5:  PO            分派 ──→ comm Handoff → Dev（三要素）
Step 6:  Dev           实现 ──→ code + tests + verification evidence → Arch
Step 7:  Arch          代码评审 ──→ review + comm `ARCH_PASS/FAIL` → Analyst（PASS）| Dev（FAIL）
Step 8:  Analyst       验证 ──→ `DATA_PASS/FAIL` + review report → PO（PASS）| Dev（FAIL）
Step 9:  PO            验收 ──→ `PRODUCT_ACCEPTED` → PM
Step 10: PM            提交请求 ──→ `COMMIT_REQUEST` → PO + Dev + Analyst
Step 11: PO/Dev/Analyst 完成提交 ──→ git commit + daily；`COMMIT_DONE` → PM
Step 12: PM            关闭 ──→ merge + worktree cleanup；`TASK_CLOSED`；plan `[x]`
Step 13: PM            下一步 ──→ 新 worktree + plan；Handoff 下一个任务
```

\* 复杂任务必须执行 Step 4：>3 个文件、新模块、策略/规则变化、存储变化、跨模块 API 变化。

---

## 工程隔离（Git Worktree 模式）

每个任务使用独立 git worktree，避免分支冲突：

```bash
# PM 在分派任务前创建 worktree
git fetch origin
git worktree add .worktrees/feat-<topic> -b feat/<topic> origin/main
# 在 plan meta + comm 中记录：Worktree = .worktrees/feat-<topic>

# Dev 只在这个 worktree 中工作
cd .worktrees/feat-<topic>

# PM 在 TASK_CLOSED 后清理
git checkout main && git pull
git merge feat/<topic>
git worktree remove .worktrees/feat-<topic>
git branch -d feat/<topic>
```

**规则：** 每个任务一个 worktree；新功能禁止在 main workspace 中开发；PM 负责生命周期。

---

## 决策标签（Comm Log Labels）

| 标签 | 含义 | 使用者 |
|-----|---------|---------|
| `APPROVED` | 设计或方案已批准 | PO |
| `ARCH_PASS` | 代码评审通过 | Arch |
| `ARCH_FAIL` | 代码评审失败，需要返工 | Arch |
| `DATA_PASS` | 数据验证通过 | Analyst |
| `DATA_FAIL` | 数据验证失败，bug list 交给 Dev | Analyst |
| `PRODUCT_ACCEPTED` | PO 已验收，可进入 PM 关闭 | PO |
| `COMMIT_REQUEST` | PM 请求各方 commit + daily | PM |
| `COMMIT_DONE` | 某方已完成 commit + daily | PO / Dev / Analyst |
| `TASK_CLOSED` | PM 已关闭任务：合并并清理 worktree | PM |
| `ESCALATE_PO` | 需要产品定义决策 | Arch / Analyst |
| `ESCALATE_PM` | 需要排期 / 资源决策 | Arch / Dev / Analyst |
| `OVERRIDE_ROLE_BOUNDARY` | 三次确认后的角色越界例外 | 任意角色 |

---

## 角色 SOP（详细参考）

| 角色 | 文件 |
|------|------|
| Project Manager (PM) | [references/role-sop-pm.md](references/role-sop-pm.md) |
| Product Owner (PO) | [references/role-sop-po.md](references/role-sop-po.md) |
| Architect (Arch) | [references/role-sop-arch.md](references/role-sop-arch.md) |
| Developer (Dev) | [references/role-sop-dev.md](references/role-sop-dev.md) |
| Data Analyst (Analyst) | [references/role-sop-analyst.md](references/role-sop-analyst.md) |
| Handoff 聊天模板 | [references/handoff-chat-templates.md](references/handoff-chat-templates.md) |
| 团队配置 Schema | [references/team-config-schema.md](references/team-config-schema.md) |
| 首次配置访谈 | [references/onboarding-interview.md](references/onboarding-interview.md) |

## 模板

- **[Spec Header](templates/spec-header.md)** — 带状态、comm log、plan 引用的 spec 模板
- **[Plan Header](templates/plan-header.md)** — 带任务 checkbox 的 plan 模板
- **[Comm Entry](templates/comm-entry.md)** — 带 handoff 区块的 comm log 条目模板
- **[Arch Review](templates/arch-review.md)** — 架构评审文档模板
- **[Analyst Review](templates/analyst-review.md)** — 数据验证报告模板
- **[Team Config YAML](templates/team-config.yaml)** — 可编辑的团队配置起始模板

---

## 与 tmux 工作区技能的关系

| 技能 | 层级 | 职责 |
|------|------|------|
| `doc-driven-multi-agent` | 协作协议层 | Agent 做什么：角色 SOP、handoff、G0-G4、文档事实来源 |
| `tmux-pane-workspace` | 工作空间层 | Agent 在哪里协作：pane 聚焦、布局、会议工作区、会议日志 |
| `tmux-cursor-agent` | Cursor 运行时层 | Cursor Agent 怎么跑：启动、登录、状态检测、四步消息协议、daemon、恢复 |

三者可以配合使用：`tmux-pane-workspace` 管 tmux 可见工作区，`tmux-cursor-agent` 管 Cursor Agent 运行细节，本协议管跨角色任务流转和可审计文档。

---

## 接入到你的项目

1. **创建文档骨架：** `AGENTS.md` → `docs/ops/WORKFLOW.md` → `docs/product/GOALS.md`
2. **定义角色：** 首次使用时，Agent 会通过访谈生成可复用团队配置（保存到 `~/.config/skills/doc-driven-multi-agent/team-config.yaml`）；熟练用户也可以复制 [templates/team-config.yaml](templates/team-config.yaml) 手动编辑
3. **从一个 feature 开始：** 创建 `docs/superpowers/comms/my-first-feature.md` + spec
4. **第一天就执行 handoff 协议：** 不允许只靠聊天交接
5. **随着团队增长逐步引入 role SOP**
6. **使用 git worktree**，让多个 Agent 并行工作更安全

---

## 团队引导与配置

协议可以记住团队结构，避免每次会话重复描述角色分工。

### 快速开始

1. **第一次使用？** 加载此技能后，Agent 检测不到配置，会启动 onboarding interview
2. **回答约 7 个短问题**，说明团队角色、Agent 类型和偏好
3. 配置会保存到 `~/.config/skills/doc-driven-multi-agent/team-config.yaml`（全局配置，跨项目共享）
4. **下次会话：** Agent 自动加载配置，跳过访谈

### 配置 Schema

完整字段见 [references/team-config-schema.md](references/team-config-schema.md)。

### 访谈协议

完整访谈流程、分支逻辑和答案处理见 [references/onboarding-interview.md](references/onboarding-interview.md)。

### 配置生命周期

| 事件 | 行为 |
|-------|----------|
| **首次加载技能** | 没有配置 → 自动启动 onboarding interview |
| **配置已存在** | 静默加载；提示 “Loaded team: {name}” |
| **强制重新配置** | 用户说 “reconfigure team” → 重新访谈 → 覆盖配置 |
| **配置过期（>30 天）** | 提示 “Is your team config still accurate?” |
| **手动编辑** | 直接编辑 `~/.config/skills/doc-driven-multi-agent/team-config.yaml`；下次会话重新加载 |
| **项目级覆盖** | 在项目根目录放 `.skills/team-config.local.yaml`，字段会深度合并到全局配置上 |
| **检测到稳定团队** | 同一角色结构跑完 3+ 个 feature 后，询问是否保存为默认配置 |

## 文档写作方法论（自底向上，原子→组合）

> **不要靠读代码倒推文档。** 先理解产品和领域，再从零设计文档结构。<br>
> **像盖房子一样：** 地基（原子算法）→ 墙体（组合逻辑）→ 屋顶（策略层）。

### 什么时候使用

适用于**逻辑层 / 算法层 / 领域层**文档：每条规则或计算都有理论来源，并会组合成更高层策略。基础设施或纯数据层文档通常只需代码交叉检查，不一定需要这套方法。

### 单个算法模板

每个原子算法章节在适用时应记录这些字段：

| 字段 | 说明 |
|-------|-------------|
| **Definition** | 算法做什么 |
| **Theory source** | 来源（书籍、论文、行业标准、领域专家） |
| **Formula** | 精确的数学 / 逻辑表达 |
| **Input data** | 消耗哪些输入数据 |
| **Parameter source** | 阈值 / 系数为什么取这个值 |
| **Edge cases** | 边界条件下如何处理 |

### 文档层级（自底向上）

```
atomic algorithms（原语，单一职责函数）
         ↓
composite algorithms（原子算法组合）
         ↓
strategy / policy layer（规则、决策、评分）
```

每一层引用下一层，不能反向依赖。

### 角色边界（通用）

这些是功能描述，不是固定职位名；可映射到你项目中的角色：

- **结构设计者**：先定义章节层级和依赖图（暂不写正文）
- **内容写作者**：按单算法模板填充每一章
- **验证者**：文档写完后，再对照实际实现 / 实践交叉检查
- **实现者**：不写文档，只阅读文档并实现

重点是：**先写文档，再做验证。** 不要通过阅读最终代码倒推文档。

**SoT：** 项目本地文档标准应与此技能保持同步。

### 参考

- [Team Config Schema](references/team-config-schema.md) — 完整 YAML 字段说明
- [Onboarding Interview](references/onboarding-interview.md) — 给 AI Agent 使用的访谈协议
- [Team Config Template](templates/team-config.yaml) — 可编辑的起始配置

---

## 许可证

MIT
