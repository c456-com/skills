# 变更日志

## 1.2.0 (2026-07-08)

- 分层集成：改为与 `tmux-pane-workspace`、`tmux-cursor-agent` 协作，明确协议层 / 工作空间层 / 运行时层边界。
- 相关技能：移除旧编排技能入口，新增 tmux workspace 与 Cursor runtime 入口。
- 配置说明：`session_template` 改为面向通用 `tmux-*-agent` 技能。

## 1.1.2 (2026-07-08)

- 文档中文化：`SKILL.md`、`README.md`、references 与 templates 改为中文说明。
- 相关技能修正：移除不存在的 `opencode`、`hermes-agent` 引用，改为仓库内真实存在的协作相关技能。
- 模板一致性：保留角色代码、状态码、路径和命令等协议锚点，同时将用户可读说明改为中文。

## 1.1.0 (2026-07-03)

- 团队引导：为首次使用者提供 7 阶段交互式访谈协议。
- 配置持久化：团队结构保存到 `~/.config/skills/doc-driven-multi-agent/team-config.yaml`，后续会话自动加载。
- 项目级覆盖：项目根目录可放置 `.skills/team-config.local.yaml` 作为项目专属配置。
- 稳定性检测：会话结束清单会在角色结构稳定后提示保存团队配置。
- 新增 references：`team-config-schema.md`、`onboarding-interview.md`。
- 新增模板：`team-config.yaml` 起始配置。
- `SKILL.md`：新增「团队引导与配置」章节，更新触发条件和接入指南。

## 1.0.0 (2026-06-30)

- 初始发布。
- 协议：文档链、handoff 三要素、G0–G4 门禁、会话协议、边界执行。
- 5 个角色 SOP：PM、PO、Arch、Dev、Analyst。
- 覆盖所有默认流转方向的 handoff 聊天模板。
- 文档模板：spec、plan、comm entry、arch review、analyst review。
- 相关技能：早期 Cursor 编排入口。
