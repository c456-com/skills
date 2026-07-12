---
name: using-c456
description: "C456 技能路由入口 / using C456 platform skills：当用户明确输入 `/using-c456` 触发路由时使用；用于自动识别当前 C456 工作场景（写文章、做对比、发 playbook、同步 wiki、团队协作、CLI 运维等），并路由到正确的 C456 技能。"
version: 2.0.0
related_skills:
  - c456-sync
  - c456-write
  - c456-publish
  - c456-cli
  - c456-llm-wiki
  - c456-team-work
---

# C456 技能路由入口

> 用于 `/using-c456` 显式触发。输入你想做的事情，Agent 帮你路由到正确的技能。

## 场景 → 技能映射

| 场景 | 描述 | 主技能 | 辅技能 |
|------|------|--------|--------|
| 对外正文 | 写 c456-sync 格式、配图策略、格式自检 | `c456-sync` | — |
| 内容写作 | 信号、产品对比、工具/渠道文章 | `c456-write` | `c456-sync`（格式） |
| 发布上线 | 净稿、CLI new/update、回填元数据、SEO 分发 | `c456-publish` | `c456-sync`（格式）、`c456-cli`（命令） |
| CLI 操作 | intake、CDP、截图、assets、搜索 | `c456-cli` | — |
| Wiki 同步 | wiki ↔ c456-sync 双向同步 | `c456-llm-wiki` | `c456-sync` |
| 团队协作 | 多角色 AI Agent 团队 | `c456-team-work` | — |

## 复合流程

| 目标 | 执行顺序 |
|------|---------|
| 写内容 → 发布 | `c456-write` → `c456-sync`（格式自检）→ `c456-publish` |
| 从 wiki 同步到 C456 | `c456-llm-wiki` → `c456-sync` → `c456-publish` |
| 截图 → 收录 | `c456-cli`（screenshot）→ `c456-publish`（发布） |
| 写产品对比 → 发布 | `c456-write`（§B 产品对比）→ `c456-publish` |

## 分层体系

| 层级 | 技能 | 职责 |
|------|------|------|
| **基础能力** | `c456-cli` | CLI 命令、CDP、鉴权、Agent 规则 |
| **基础能力** | `c456-skills-repo` | 技能仓库维护 |
| **数据同步** | `c456-sync` | 对外正文格式 + 配图策略 |
| **数据同步** | `c456-write` | 信号/产品对比/工具渠道文章写作 |
| **数据同步** | `c456-llm-wiki` | wiki ↔ C456 双向同步 |
| **数据发布** | `c456-publish` | 净稿 → CLI 发布 → 回填 → SEO 分发 |

## 技能速查表

| 技能 | 用途 |
|------|------|
| [c456-sync](c456-sync/SKILL.md) | 对外正文格式规范 + 配图策略 |
| [c456-write](c456-write/SKILL.md) | 三种内容写作模式（信号/对比/文章） |
| [c456-publish](c456-publish/SKILL.md) | 从 c456-sync 发布到 C456 线上（净稿/CLI/回填/SEO） |
| [c456-cli](c456-cli/SKILL.md) | CLI 命令、CDP 截图、assets、intake/playbook 操作 |
| [c456-llm-wiki](c456-llm-wiki/SKILL.md) | wiki ↔ c456-sync 双向同步、引用型镜像、版本绑定 |
| [c456-team-work](c456-team-work/SKILL.md) | 多角色 AI Agent 团队协作工作流 |
| [c456-skills-repo](c456-skills-repo/SKILL.md) | c456-com/skills 仓库维护（元技能） |
| [c456-rails-startup](c456-rails-startup/SKILL.md) | Rails + Inertia + React 从零脚手架 |
| [c456-software-dev-sop](c456-software-dev-sop/SKILL.md) | 软件开发 SOP（需求→编码→测试→文档） |

## 路由逻辑

若用户输入不明确的 C456 任务，用此映射判断：

1. 主技能 = 最匹配的场景技能
2. 辅技能 = 可能同时需要的技能（建议加载但非必须）

> 主技能 + 辅技能按需加载；复合流程按表内顺序执行。
