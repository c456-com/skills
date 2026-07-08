# doc-driven-multi-agent

> **跨平台的文档驱动多代理协作协议**：包含角色 SOP、handoff 协议、G0–G4 门禁和越界拒绝规则。

这个协议用于通过**文档驱动 handoff** 协调多个 AI Agent，而不是依赖聊天记录传话。每个决策、任务流转和评审都记录在项目文档中，形成可审计的责任链。

**核心规则：** 没有文档 = 没有交接 = 不能开工。

## 快速开始

```bash
# 通过 npx skills 安装
npx skills add c456-com/skills --skill doc-driven-multi-agent -y
```

然后在你的项目中：

1. 阅读 `SKILL.md` 获取完整协议
2. 创建 `AGENTS.md` 作为 Agent 入口文件
3. 定义角色并创建文档骨架
4. 用 spec + comm log 启动第一个 feature

## 目录内容

```
doc-driven-multi-agent/
├── SKILL.md                    # 完整协议定义
├── references/
│   ├── role-sop-pm.md          # Project Manager SOP
│   ├── role-sop-po.md          # Product Owner SOP
│   ├── role-sop-arch.md        # Architect SOP
│   ├── role-sop-dev.md         # Developer SOP
│   ├── role-sop-analyst.md     # Data Analyst SOP
│   └── handoff-chat-templates.md # 聊天 handoff 消息模板
├── templates/
│   ├── spec-header.md          # spec 文档模板
│   ├── plan-header.md          # plan 文档模板
│   ├── comm-entry.md           # comm log 条目模板
│   ├── arch-review.md          # 架构评审模板
│   └── analyst-review.md       # 数据验证报告模板
├── LICENSE                     # MIT
└── README.md
```

## 核心概念

### 文档链

```
AGENTS.md → WORKFLOW.md → GOALS → spec → comm → plan → code → review → daily
```

每项工作都沿这条文档链流转。没有文档 = 没有交接 = 不能开工。

### 五个角色

| 角色 | 代码 | 写代码？ |
|------|------|:------------:|
| Project Manager | PM | 否 |
| Product Owner | PO | 否 |
| Architect | Arch | 有限 |
| Developer | Dev | 是 |
| Data Analyst | Analyst | 否 |

### Handoff 协议（三要素）

每次角色交接都必须在 comm log 中包含三个字段：
- **Target**（对象）：谁接收交接
- **Address**（地址）：相关文档路径
- **Task**（事项）：下一个角色要做什么

### G0–G4 门禁

G0（启动）→ G1（设计冻结）→ G2（实现放行）→ G3（产品验收）→ G4（关闭）

## 相关技能

- **[tmux-pane-workspace](https://github.com/c456-com/skills/tree/main/tmux-pane-workspace)**：tmux 工作空间层，负责 pane 聚焦缩放、多 pane 布局和会议工作区
- **[tmux-cursor-agent](https://github.com/c456-com/skills/tree/main/tmux-cursor-agent)**：Cursor Agent 运行时层，负责状态检测、四步消息协议和监控 daemon
- **[c456-team-work](https://github.com/c456-com/skills/tree/main/c456-team-work)**：C456 团队工作流，负责多角色协作闭环
- **[c456-software-dev-sop](https://github.com/c456-com/skills/tree/main/c456-software-dev-sop)**：通用软件开发 SOP

## 许可证

MIT
