---
name: c456-llm-wiki
description: >-
  Extends llm-wiki-domains (multi-domain wiki) with C456.com bidirectional sync.
  Adds c456-sync/ mirror layer, C456 content type mapping (signal/tool/channel/playbook/walkthrough),
  publish workflow via c456 CLI, and orphan_local remote-deletion handling.
  Depends on llm-wiki-domains for the multi-domain structure and llm-wiki for per-domain operations.
---

# C456 LLM Wiki — C456 双向同步

## 架构依赖

本技能基于分层架构构建：

```
llm-wiki (Hermes 核心)       ← 单知识库引擎：ingest / query / lint
    ↑
llm-wiki-domains             ← 多领域导航：root + domains/
    ↑
c456-llm-wiki                ← C456 同步：c456-sync/ ↔ c456.com
```

**前置依赖：** 确保 `llm-wiki` 和 `llm-wiki-domains` 已安装。本技能只负责 C456 特有功能。

## 核心思想

在 llm-wiki-domains 多领域架构基础上增加 C456 双向同步层，实现本地知识库与 c456.com 之间的内容发布与拉取。每个领域可独立配置同步范围。

## 必读：仓库根 `AGENTS.md`

- **§1.2**：c456-wiki **定位、目的、受众**（收集整理 → 对外分享 → 帮互联网读者选择高价值工具与方案）。
- **§1.3**：`c456-sync/` 与 C456 **上行正文**的六条原则——**准确性、可读性、整洁性、逻辑性、推荐性、推广性**（含与 `wiki/` 分工：镜像层单篇自洽、面向陌生读者）。
- **§6.5**：远端记录已删、本地 `c456-sync` / `meta` / `wiki` 仍在时（**orphan_local**）——**先列清单、用户确认后再删或归档**，禁止自动删除；详见下文「orphan_local」与 `AGENTS.md` 全文。

**冷启动 / 初始化目录时**：先打开仓库根 `AGENTS.md`，确认已包含 **§1.2–1.3** 与 **§6.5**（若缺失则补全后再建 `c456-sync/` 或首次 Ingest）；旧模板仅有 §1.2–1.3 时至少补 **§6.5**。可在首条 `wiki/log.md` 注明「已对齐 §1.2–1.3 / §6.5」。

任何写入 **`c456-sync/`**、或组装将提交给 **`c456 intake` / `c456 playbook` / `c456 walkthrough` 的正文** 之前，重读 **§1.3** 自检一遍；**Walkthrough** 另见 `c456-sync-public-markdown` 与 `c456-cli` 的 content-syntax §3（正文勿嵌本页录屏）。

## 四层架构

```
raw/（原始素材层）  ← 你存放，AI 只读
    ↑↓
c456-sync/（镜像层）← C456 线上内容的本地镜像
    ↑↓
wiki/（知识库层）   ← AI 生成的结构化 Markdown，互相链接
    ↑↓
AGENTS.md（Schema） ← 定义 AI 如何组织 Wiki
```

## 目录结构

```
.
├── raw/
│   ├── articles/  books/  papers/  courses/
│   ├── resources/  quotes/  tools/  work/
├── c456-sync/
│   ├── signal/  tool/  channel/  playbook/  walkthrough/
├── wiki/
│   ├── index.md  log.md  c456-meta.yml
│   ├── entities/  concepts/  threads/  sources/  agents/
├── output/
└── AGENTS.md
```

### 四层关系


| 层级           | 谁维护   | 用途      | 与 C456 关系 |
| ------------ | ----- | ------- | --------- |
| `raw/`       | 用户放入  | 原始素材    | 上行时作为内容来源 |
| `c456-sync/` | AI 同步 | C456 镜像 | 与线上一一对应   |
| `wiki/`      | AI 生成 | 提炼后的知识库 | 多对多映射     |
| `output/`    | 用户创作  | 主动产出    | 可发布到 C456 |


**关键原则**：`c456-sync/` 与 `wiki/` 之间不用 symlink。关联通过 Frontmatter 引用 + `wiki/c456-meta.yml` 实现。

### c456-sync 与上行正文（执行摘要）

`c456-sync/` 虽是镜像层，正文须视同 **对外读者可读版本**：事实可核对、结构清晰、有推荐结论与诚实边界、CTA 明确；细节与表格见 **`AGENTS.md` §1.3**。

---

## 页面类型

### 实体页 `wiki/entities/`

- 命名：小写 kebab-case，如 `andrej-karpathy.md`
- Frontmatter：`type: entity` + `c456-id` + `c456-kind` + `c456-sync-path` + `tags: [...]`

### 概念页 `wiki/concepts/`

- 命名：小写 kebab-case，如 `rag.md`

### 线索页 `wiki/threads/`

- 命名：小写 kebab-case，如 `ai-engineering-trilogy.md`

### 来源摘要页 `wiki/sources/`

- 命名：与 raw 文件名呼应
- Frontmatter：`type: source` + `c456-kind` + **`c456-title`** + **`c456-summary`**（上行必备）+ `c456-id` + `c456-status` + `date: YYYY-MM-DD` + `raw: raw/.../xxx.md`

---

## 链接规范

- 使用 Obsidian Wikilink：`[[page-name]]`
- 链接目标文件名不带 `.md` 后缀
- 页面标题使用一级标题 `# Title`

---

## 核心原则：完整知识提取

**知识库的目的不是存储原文，而是存储可被问答的知识。** 录入书籍时：

1. **逐章提取** — 按目录逐项创建 wiki 页面，每个策略/概念独立成页，不可遗漏任何章节
2. **图片理解** — 遇到图表/K线图/示意图时，必须结合上下文理解其含义并记录为文字知识。例如 K 线形态图需说明：图形特征、出现位置（底部/顶部）、后续走势含义、操作信号
3. **条件与参数完整保留** — 选股条件、技术指标阈值、软件操作步骤等不可省略
4. **案例保留关键信息** — 股票代码、买卖价格、时间周期、获利幅度等数据需记录
5. **知识密度优先** — 每页 wiki 应包含可被问答的实质性内容，而非目录级概述

### Ingest（摄入）— 书籍专项流程

对书籍类素材（raw/books/），执行以下额外步骤：

1. **解析目录** — 提取所有章节标题，建立章节清单
2. **逐章读取** — 按章节顺序完整读取 Markdown 内容
3. **图片处理** — 遇到 `![](images/...)` 时：
   - 读取图片上下文（前后文字说明）
   - 理解图形含义并转化为文字描述
   - 在 wiki 页面中保留图片引用 + 文字解释
4. **策略提取** — 每个独立战法/方法创建为 `wiki/threads/` 或 `wiki/concepts/` 页面，包含：
   - 核心逻辑（为什么有效）
   - 优选条件（选股参数、技术指标阈值）
   - 操作步骤（具体执行流程）
   - 案例说明（股票代码、价格、时间、结果）
   - 注意事项（风险点、适用环境）
5. **概念提取** — 通用知识创建为 `wiki/concepts/` 页面，包含：
   - 定义与原理
   - 分类与形态
   - 应用场景
   - 与其他概念的关联
6. **实体提取** — 人物/产品/工具创建为 `wiki/entities/` 页面
7. **完整性检查** — 对比目录清单，确认所有章节都有对应 wiki 页面

### Ingest（摄入）

1. 读取素材
2. **验证基础信息**：用户提供的仓库名、账号名、URL 等可能不准确（如 `lan` 实际是 `ian`）。通过 GitHub API 搜索或直接访问候选 URL 验证后再使用。
3. 判定 C456 类型（signal/tool/channel/playbook/walkthrough）
4. 创建/更新来源摘要页（Frontmatter 含 `c456-title` + `c456-summary`，供后续上行）
5. 提取实体（无则新建，有则追加）
6. 提取概念（无则新建，有则整合）
7. 更新线索页
8. 更新 `wiki/index.md`
9. 追加 `wiki/log.md`

**C456 类型判定**：介绍工具用法 → `tool`；介绍作者/频道 → `channel`；step-by-step → `walkthrough`；策略/框架 → `playbook`；其余 → `signal`。

### Query（查询）

1. 先读 `wiki/index.md`
2. 定位相关页
3. 读取并综合
4. 引用来源
5. 回写好答案：若用户认可，提议保存为 wiki 新页面

### Lint（检查）

1. 扫描矛盾
2. 发现孤立页
3. 检查缺失页
4. 评估数据缺口
5. 输出 Markdown 报告

---

## C456 集成规范

### 内容类型映射


| C456 类型         | 含义     | 对应 raw/                        | 对应 wiki/                      | 对应 output/ |
| --------------- | ------ | ------------------------------ | ----------------------------- | ---------- |
| **signal**      | 信息片段   | articles/, quotes/, resources/ | wiki/sources/                 | 短评         |
| **tool**        | 工具/软件  | tools/                         | wiki/entities/                | 工具评测       |
| **channel**     | 频道/账号  | resources/                     | wiki/entities/                | 频道推荐       |
| **playbook**    | 方法论/框架 | work/, books/                  | wiki/concepts/, wiki/threads/ | 方法论文章      |
| **walkthrough** | 教程     | courses/, articles/            | wiki/threads/                 | 教程         |


### Frontmatter 扩展

收录五种 C456 类型并准备**上行**时，须在 Frontmatter 中写明 **`c456-title`** 与 **`c456-summary`**，作为同步到 C456 的展示标题信息（与页面正文的一级标题 `# Title` 区分，避免与通用 `title` 字段混淆）。

- **`c456-title`**：主标题（单行，对应 CLI/API 的标题字段）。
- **`c456-summary`**：紧跟标题语义的一句简短说明，用于列表/卡片上的补充展示；上行时与 `c456-title` 一并交给 Agent 或写入请求（具体拼接格式以当次 CLI/API 为准）。

**这句简短描述叫什么**：若强调「从属于主标题的补充短语」，中文常用 **副标题**，英文 **subtitle**；若强调「一句话概括、列表摘要」，产品与 API 语境常用 **摘要**，英文 **summary**（C456 Intake 卡片上与标题配对展示的也是 summary）。营销语境也可称 **标语 / tagline**。本规范 Frontmatter 使用字段名 **`c456-summary`**，语义与上述「摘要」对齐。

```yaml
---
type: source
c456-kind: signal      # signal | tool | channel | playbook | walkthrough
c456-title: "主标题"
c456-summary: "一句简短描述，用作上行列表/卡片摘要（副标题语义）"
c456-id: 42            # 发布后回填
c456-status: draft     # draft | published | outdated | conflict
date: 2026-05-08
---
```

### 发布工作流（上行）

1. 扫描带 `c456-kind` 但缺 `c456-id` 或 `status: draft` 的页面
2. **格式自检**：发布正文前，先加载 `c456-sync-public-markdown` 技能。正文必须符合对外格式规范——无 `#` 一级标题、无制作备忘（仓库路径/截图命令/asset ID 解释）、无 `## 总结` / `## TL;DR` 等标签式二级标题；核心判断写在首节正文段落中。
3. 转换 Markdown 为 C456 富文本格式（移除 Wikilink、Frontmatter）
4. 选择命令：signal/tool/channel → `c456 intake new -k <kind>`；playbook/walkthrough → `c456 playbook new`
5. 正文写入 `.tmp/`，通过 `--body-file` 传入 CLI
6. 回填 ID 到 Frontmatter `c456-id`，改 `c456-status: published`
7. 记录日志到 `wiki/log.md`

更新已有内容：用 `c456 intake update <id>` 或 `c456 playbook update <id>`，不重复新建。

### 双向同步

**c456-sync/ 目录**：作为 C456 镜像层，按五类型分目录存储。撰写、从线上拉回后的润色、以及准备 `--body-file` 的正文，须满足 **`AGENTS.md` §1.3**。

**关联方式**：`c456-sync/` 文件 Frontmatter 标注 `local-wiki-source`、`local-wiki-entities` 等字段；`wiki/` 页面 Frontmatter 标注 `c456-id`、`c456-sync-path`；`wiki/c456-meta.yml` 记录总索引。

**双向索引**：`wiki/index.md` 中已发布条目可标注 `[c456:#id]`。C456 正文可保留回链到本地 Wiki 的链接。

### 远程已删、本地仍存（orphan_local）

见仓库根 **`AGENTS.md` §6.5**：须先向用户输出 **待删除/待处理清单** 并取得 **明确确认** 后，方可删除 `c456-sync/` 或调整 `wiki/` 与 `c456-meta.yml`；可选路径含删镜像、wiki 归档、`meta` 去幽灵 id、或 `intake new` 重发。

### 状态流转

```
draft → publishing → published → outdated → published
                                    ↘ conflict
```

---

## 特殊文件规范

### `wiki/index.md`

内容导向的目录，每页一行摘要 + 链接。按分类组织。每次 Ingest 后更新。

### `wiki/log.md`

时间导向的追加日志。条目格式：`## [YYYY-MM-DD] 操作类型 | 标题/简述`
操作类型：`ingest`、`query`、`lint`、`update`、`create`、`c456-publish`、`c456-down-ingest`、`c456-conflict`
保持 append-only。

### `wiki/c456-meta.yml`

C456 ↔ 本地映射总索引。记录每个 C456 ID 的 `sync_path`、`wiki_pages[]`、状态、时间戳、checksum。AI 在同步操作中自动维护。

---

## 产品录入调研与数据自动补充（Enrichment）

录入产品（tool 类型）时，若提供的信息不完整（如仅给 GitHub 仓库 URL），AI 应主动上网调研并自动补充多种数据类型。

### 调研来源

| 信息类型 | 调研方法 | 示例 |
|---|---|---|
| **官网** | 从 GitHub README 或组织页提取 | `github.com/rails/rails` → `rubyonrails.org` |
| **包管理器** | 搜索 npm / RubyGems / PyPI / Crates.io / Homebrew | `github.com/rails/rails` → `gem rails` |
| **GitHub 元数据** | 读取仓库页（stars、license、语言、最新发布） | 自动记录 stars 数、许可证、主要语言 |
| **产品描述** | 从官网首页或 README 提炼一句话简介 | 用于 `c456-summary` |
| **核心功能** | 从官网 Features 页或 README 提取 | 用于正文 |
| **安装方式** | 从 README 或官网提取 | apt / brew / npm / Docker 等 |

### 调研流程

1. **输入**：用户提供任意信息（官网 URL、GitHub URL、产品名等）
2. **调研**：AI 使用 WebFetch 工具获取官网、GitHub、包管理器页面
3. **交叉验证**：确认官网与 GitHub 的对应关系
4. **补充**：将调研结果填入 raw 素材、c456-sync 镜像、wiki 页面
5. **发布**：按标准 Ingest 流程创建/更新所有页面

### 数据填充规则

- **c456-title**：`品牌名 | 定位 · 特色后缀`
- **c456-summary**：一句话概括核心价值
- **正文**：包含核心功能模块表、安装方式、适用场景；并自检 **`AGENTS.md` §1.3**（对外可读、可推荐、不夸大）。
- **实体页**：包含关键属性表（官网、GitHub、stars、许可证、语言）、核心功能、差异化亮点、竞品对比
- **来源摘要**：包含核心信息、关键功能、开源信息

### 示例：GitHub URL → 多类型数据

给定 `github.com/rails/rails`，AI 应自动：
1. 读取 GitHub README → 提取官网 `rubyonrails.org`
2. 搜索 RubyGems → 找到 `gem rails`
3. 记录 GitHub stars、许可证（MIT）、主要语言（Ruby）
4. 访问官网 → 提取产品描述、核心功能
5. 创建完整 raw / c456-sync / wiki 页面
6. 发布到 C456

---

## 产品方案讨论（持续更新）

本地 Wiki 与 **C456 SaaS**（`c456-react`）统一演进的产品讨论主本：

- **`wiki/threads/c456-llm-wiki-产品方案讨论.md`** — 类型映射、双轨笔记本、Ruby 学习场景、Public+Personal 共创、演进阶段与 Open Questions

续写讨论时 **append** 该文件 §10「讨论记录」，并更新 `wiki/log.md`。