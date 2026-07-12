---
name: using-c456
description: "C456 技能路由入口 / using C456 platform skills：当用户明确输入 `/using-c456` 触发路由时使用；用于自动识别当前 C456 工作场景（写文章、做对比、发 playbook、同步 wiki、团队协作、CLI 运维等），并路由到正确的 C456 技能。"
version: 1.0.0
triggers:
  - 用户在对话中输入 `/using-c456` 时强制触发
  - 当 C456 相关技能命中描述但不确定加载哪一个时
related_skills:
  - c456-product-channel-article
  - c456-signal-product-vs
  - c456-signal-researcher
  - c456-playbook-publishing
  - c456-sync-public-markdown
  - c456-llm-wiki
  - c456-cli
  - c456-rails-startup
  - c456-team-work
  - c456-software-dev-sop
---

# using-c456 — C456 技能路由入口

> C456 平台技能的统一入口。**不是 always apply**，用户明确输入 `/using-c456` 时触发。
>
> 加载后自动诊断当前工作场景，推荐并加载最合适的 C456 技能。

## 何时使用

**当用户输入 `/using-c456` 时，必须加载本技能。**

这条指令的优先级高于「先检查技能再行动」。用户输入 `/using-c456` 意味着：

1. 当前任务与 C456 平台相关
2. 用户不确定用哪个 C456 技能
3. Agent 应当先诊断场景、再路由技能，然后执行

**不要**在以下情况自动触发：

- 用户只提到 C456 但未输入 `/using-c456` — 让 description 触发机制正常工作
- 用户在使用第三方技能或非 C456 通用技能 — 不需要此路由

## 场景识别

加载 `/using-c456` 后，Agent 应当：

1. 检查当前打开的目录、文件、对话历史
2. 匹配对话关键词和任务描述
3. 确定最可能的 C456 工作场景
4. 按路由优先级加载技能

### 场景识别表

| 场景 | 对话关键词 | 推荐主技能 | 辅助技能 |
|------|-----------|-----------|---------|
| 产品/渠道长文 | 产品介绍、tool、channel、渠道稿、公众号、五段式 | `c456-product-channel-article` | — |
| 产品对比 | 对比、vs、选型、Auth vs Auth、竞品差异、tool vs tool | `c456-signal-product-vs` | — |
| 新闻/研究 | 新闻、收录、行业动态、signal、研究员、事实核验 | `c456-signal-researcher` | `c456-signal-product-vs`(含对比) |
| Playbook 发布 | 发布、playbook、上传、软文、blog、长文、字数校验 | `c456-playbook-publishing` | `c456-cli` |
| 公共 Markdown | public markdown、对外稿、--body-file、frontmatter 剥离 | `c456-sync-public-markdown` | `c456-cli` |
| Wiki 同步 | 同步、拉回、发布到 C456、引用型镜像、版本绑定 | `c456-llm-wiki` | `c456-cli` |
| CLI 运维 | intake、收录 asset、搜索 C456、截图上传、API | `c456-cli` | — |
| 团队协作 | team、团队开工、工作组、多角色、汇报 | `c456-team-work` | `tmux-pane-workspace` |
| 软件开发 | 需求、编码、测试、SOP、修 bug、验收 | `c456-software-dev-sop` | `llm-wiki` |
| Rails 启动 | 脚手架、Rails、Inertia、从零搭建 | `c456-rails-startup` | — |
| 技术写作+发布 | 写一篇 C456 文章 → 发布 | `c456-product-channel-article` → `c456-playbook-publishing` | 顺序执行 |

## 技能总览

### C456 业务技能

| 技能 | 一句话触发条件 |
|------|--------------|
| [c456-product-channel-article](c456-product-channel-article/SKILL.md) | 写 tool/channel 介绍、公众号渠道稿、五段式产品叙事 |
| [c456-signal-product-vs](c456-signal-product-vs/SKILL.md) | 做 Auth/IdP/SaaS/开源工具深度对比、选型建议、竞品差异分析 |
| [c456-signal-researcher](c456-signal-researcher/SKILL.md) | 新闻收录、行业动态、研究 signal、事实核验短文 |
| [c456-playbook-publishing](c456-playbook-publishing/SKILL.md) | 写软文/blog/playbook 长文、配图上传、字数校验、CLI 发布 |
| [c456-sync-public-markdown](c456-sync-public-markdown/SKILL.md) | 编写/发布 tool/signal/channel/walkthrough 对外正文、frontmatter 剥离 |
| [c456-llm-wiki](c456-llm-wiki/SKILL.md) | 把 llm-wiki 页面发布到 C456、引用型镜像、版本绑定、拉回内容 |
| [c456-cli](c456-cli/SKILL.md) | intake、playbook、assets、搜索、截图上传、C456 API 工作流 |
| [c456-rails-startup](c456-rails-startup/SKILL.md) | Rails + Inertia + React 从零脚手架搭建 |
| [c456-team-work](c456-team-work/SKILL.md) | 启动/管理多角色 AI Agent 团队、工作组、handoff/relay、汇报 |
| [c456-software-dev-sop](c456-software-dev-sop/SKILL.md) | 需求→调研→编码→测试→验收完整开发 SOP |

## 路由优先级

当多个技能可能匹配时：

| 优先级 | 类型 | 说明 |
|--------|------|------|
| 1 | 主技能 | 当前场景的核心执行技能（例如写文章 → `c456-product-channel-article`） |
| 2 | 辅助技能 | 主技能执行过程中可能需要额外加载的技能（例如 CLI 操作、wiki 记录） |
| 3 | 顺序执行 | 从前到后依次使用多个技能（例如先写稿、再发布） |

### 路由规则

- **主技能优先加载**：场景识别后立即加载主技能
- **辅助技能按需加载**：主技能执行过程中若需要 CLI、wiki 记录等能力，再加载对应技能
- **顺序执行**：当任务需要多个阶段时（如写稿→发布），先完第一个技能再进入下一个
- **团队场景走 `c456-team-work`**：如果场景识别为团队协作，直接路由到 `c456-team-work`，由它决定是否需要其他技能

## 场景识别示例

### 示例 1：写产品文章

```
用户: /using-c456  最近 C456 上线了 Supabase Auth 集成，写一篇 tool 介绍

Agent 诊断:
- 关键词: "tool"、"写一篇"、"介绍"
- 推断: 产品/渠道长文
- 推荐: c456-product-channel-article
- 动作: 先加载 c456-product-channel-article，按技能 SOP 执行
```

### 示例 2：做产品对比后发布

```
用户: /using-c456  Auth0 vs Supabase Auth，对比后发到网站上

Agent 诊断:
- 关键词: "vs"、"对比"、"发到网站"
- 推断: 产品对比 → 发布
- 推荐: 顺序执行 c456-signal-product-vs → c456-playbook-publishing
- 动作: 先加载对比技能，完成后再加载发布技能
```

### 示例 3：同步 wiki 到 C456

```
用户: /using-c456  把刚写好的 transformer 笔记同步到线上

Agent 诊断:
- 关键词: "同步"、"笔记"、"线上"
- 推断: Wiki 同步
- 推荐: c456-llm-wiki
- 动作: 加载 c456-llm-wiki，按同步流程执行
```

## 执行纪律

- **路由决定后立即加载技能**：不要先开始执行再路由，必须按诊断结果先加载技能
- **不跨场景执行**：识别到哪个场景就路由到哪个技能，不要自行编造流程
- **不确定时问用户**：如果诊断置信度 < 70%，先向用户确认推断场景再加载
