---
name: llm-wiki-domains
description: "LLM Wiki Domains / multi-domain knowledge base：当用户要为多个主题建立隔离知识库、跨领域搜索/query、路由资料、维护根层 purpose/overview 或做多领域 health-check 时触发；用于每域独立 llm-wiki 与 meta-wiki 导航。"
version: 0.4.0
tags:
  - wiki
  - knowledge-base
  - domains
  - multi-domain
  - meta-wiki
  - llm-wiki
  - ingest
  - search
  - query
related_skills:
  - llm-wiki
---

# LLM Wiki Domains — 多领域知识库导航

> **构建跨领域知识库：每个领域都是独立的 [llm-wiki](../llm-wiki/SKILL.md) 实例，并通过根索引互相连接。**

本技能在标准 llm-wiki 模式之上增加一个**多领域容器层**。它不是单一扁平知识库，而是以下结构：

```
my-brain/
├── AGENTS.md                    ← 根级 schema
├── raw/                         ← 跨领域或待路由源材料
├── wiki/                        ← 根层 meta-wiki
│   ├── purpose.md               ← 全局目标、领域边界、关键问题
│   ├── overview.md              ← 跨领域概要、共享主题、知识空白
│   ├── index.md                 ← 全局索引 + 领域注册表
│   └── log.md                   ← 全局操作日志
├── domains/
│   ├── stock-trading/           ← 独立 llm-wiki 实例
│   │   ├── AGENTS.md
│   │   ├── raw/
│   │   └── wiki/
│   ├── ai-research/             ← 独立 llm-wiki 实例
│   │   ├── AGENTS.md
│   │   ├── raw/
│   │   └── wiki/
```

## 前置条件

- 必须安装本仓库的 **`llm-wiki`** 技能。本技能负责多领域导航层；实际的摄取、查询、检查操作委托给各领域内的 llm-wiki 方法论。
- **Obsidian**（可选）— wiki 目录可直接作为 Obsidian vault 使用。`[[wikilinks]]` 会渲染为可点击链接，Graph View 可用，YAML frontmatter 可供 Dataview 查询。

## 架构

### 双层结构

| 层级 | 路径 | 职责 |
|-------|------|----------------|
| **根层** | `./` | 跨领域目标、领域注册表、共享概念、待路由材料、全局 health-check |
| **领域层** | `domains/<name>/` | 自包含的 llm-wiki 实例（raw + wiki + schema/purpose） |

根层在 `wiki/index.md` 中维护**领域注册表**，用于把领域名称映射到路径。每个领域都是完全独立的知识库，遵循标准 llm-wiki 三层架构（raw → wiki → schema/purpose）。根层自身也是一个轻量 meta-wiki，负责跨领域导航、共享概念和知识空白。

### 目录布局

```text
{{PROJECT_NAME}}/
├── AGENTS.md                    ← 根级 schema（本导航层）
├── .gitignore                   ← 包含 .config/ 规则
├── .config/                     ← 技能专用配置（不提交 Git）
├── raw/                         ← 跨领域源材料（子目录按需创建）
├── wiki/                        ← 全局知识层（根层）
│   ├── purpose.md               ← 全局目标、领域边界、关键问题
│   ├── overview.md              ← 跨领域概要、共享主题、知识空白
│   ├── index.md                 ← 全局索引 + 领域注册表
│   └── log.md                   ← 仅追加操作日志
├── domains/                     ← 领域容器
│   └── <domain-name>/
│       ├── AGENTS.md            ← 领域专用 schema
│       ├── raw/                 ← 领域源材料（子目录按需创建）
│       └── wiki/                ← 领域 wiki
│           ├── purpose.md  overview.md  index.md  log.md
└── .tmp/                        ← 临时文件
```

> **子目录按需创建原则**：`raw/articles/`、`raw/books/`、`wiki/concepts/`、`wiki/entities/` 等子目录不在初始化时创建。只有当首次写入对应类型的内容时，才创建对应目录。这样避免了大量空目录占用视野。

### 跨领域检索协议

1. **先读根层**：读取 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`
2. **判断领域**：从领域注册表和全局目的判断问题属于单领域、跨领域，还是待路由
3. **领域内定位**：进入相关 `domains/<name>/`，读取该领域 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`、近期 `wiki/log.md`
4. **跨领域查询**：分别查询相关领域，再把可复用综合写回根层 `wiki/queries/`、`wiki/comparisons/` 或 `wiki/overview.md`
5. **范围隔离**：摄取默认只作用于一个明确领域；跨领域材料先放根层 `raw/work/` 并记录待路由

## 初始化（Init）

### 步骤 1 — 确认需求

- 询问项目路径（默认：当前工作目录）
- 询问项目名（kebab-case，例如 `my-brain`）
- 询问全局知识库目标：这个多领域 wiki 要长期回答哪些问题
- 询问初始领域列表：每个领域需要名称（kebab-case）、显示名称、范围边界和一句话描述

### 步骤 2 — 扫描现有状态

```bash
ls -la <path>                    # 检查目录是否存在
git rev-parse --is-inside-work-tree  # 检查是否位于 Git 仓库内
```

- 空目录 → `fresh` 模式（创建全部内容）
- 部分存在 → `merge` 模式（补齐缺失内容，跳过已有内容）

### 步骤 3 — 展示预览表

| 类别 | 路径 | 操作 |
|----------|------|--------|
| 新目录 | `raw/` | 创建 |
| 新文件 | `AGENTS.md` | 从模板创建 |
| 新文件 | `wiki/purpose.md` | 从模板创建 |
| 新文件 | `wiki/overview.md` | 从模板创建 |
| 新文件 | `wiki/index.md` | 从模板创建 |
| 跳过 | `wiki/log.md` | 若已存在则跳过 |
| 新目录 | `domains/<name>/` | 创建 |
| 新文件 | `domains/<name>/AGENTS.md` | 从模板创建 |

> **不预先创建子目录**（如 `raw/articles/`、`wiki/concepts/` 等）。在首次写入内容时按需创建。

### 步骤 4 — 创建脚手架

从 `references/` 模板创建文件，并替换占位符：
- `{{PROJECT_NAME}}` — 项目目录名
- `{{DATE}}` — 今天日期（YYYY-MM-DD）
- `{{DOMAIN_NAME}}` — kebab-case 领域名
- `{{DOMAIN_DISPLAY_NAME}}` — 人类可读的领域名
- `{{DOMAIN_DESCRIPTION}}` — 一句话领域描述
- `{{DOMAIN_ROWS}}` — 注册表行（`| name | path | description |`）

先创建目录，再创建文件。对每个领域创建完整领域脚手架，包括 AGENTS.md + raw/ + wiki/。默认不创建 `output/`；若用户需要产出物目录，再单独添加。

### 步骤 5 — Git 检测

如果项目位于 Git 仓库内，询问用户是否要提交初始脚手架。如果不是 Git 仓库，建议执行 `git init`，但不要自动执行。

提交信息规范见下方[Git 工作流](#git-工作流)。

### 添加新领域（add-domain）

流程与初始化相同，但范围更小：
1. 询问领域名、显示名称和描述
2. 扫描是否已存在（已存在则跳过）
3. 展示预览（单个领域脚手架）
4. 确认 → 创建 → 更新根层 `wiki/index.md` 注册表和 `wiki/overview.md` → 追加 `wiki/log.md`

## 领域内操作

本技能将单个领域内的操作委托给 **`llm-wiki`**。在任一领域目录中，适用标准 llm-wiki 操作：

### 摄取（单领域）

1. 先读根层 `wiki/purpose.md` 和领域注册表，判断材料属于哪个领域
2. 进入领域，按 `llm-wiki` 的定位流程读取 `purpose.md`、`overview.md`、`index.md`、近期 `log.md`
3. 执行两阶段摄取：先分析实体、概念、矛盾、待更新页面，再生成/更新 wiki 文件
4. 更新领域 `sources/`、`entities/`、`concepts/`、`comparisons/`、`threads/`、`queries/`
5. 更新领域 `wiki/index.md`、`wiki/overview.md`、`wiki/log.md`
6. 若材料影响跨领域主题，再更新根层 `wiki/overview.md` 或 `wiki/queries/`

跨领域材料先放入根层 `raw/work/`，再在摄取时路由到合适领域。

### 查询（单领域）

1. 读取根层 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`
2. 判断是单领域查询还是跨领域查询
3. 单领域：进入领域后按 `llm-wiki` 查询流程读取 `purpose.md`、`overview.md`、`index.md` 并搜索相关页面
4. 跨领域：分别查询相关领域，汇总共享概念、差异、冲突和知识空白
5. 如果答案有保存价值，单领域结果写入领域 `queries/`；跨领域结果写入根层 `queries/` 或 `comparisons/`

跨领域查询：先检查根层注册表，再搜索各领域。

### 检查（单领域或跨领域）

1. 查找孤立页面（没有入站 wikilink）
2. 查找断开的 wikilink（链接到不存在页面）
3. 检查索引完整性（每个 wiki 文件都在 index.md 中）
4. 校验 frontmatter
5. 检查 `purpose.md` 对齐度、`overview.md` 是否过期
6. 检查过期内容、低置信度内容、来源漂移和矛盾内容
7. 跨领域检查领域边界是否重叠、注册表是否准确、根层是否遗漏共享主题
8. 输出 Markdown 报告，并追加对应 `wiki/log.md`

## Git 工作流

### 重要里程碑后的提交建议

完成初始化、整本书摄取或大批量更新后：

1. 检查 `git rev-parse --is-inside-work-tree`
2. 如果位于 Git 仓库内，提供建议提交信息并询问是否提交
3. 默认提交范围：`wiki/`、`AGENTS.md`、`domains/*/AGENTS.md`、`domains/*/wiki/`
4. **暂存 `raw/` 前必须询问**（可能很大）— 若超过 50MB，建议加入 gitignore

### 建议提交格式

```
ingest: <domain> <topic> — N concepts, M sources

- 已更新 wiki/index.md、wiki/log.md
- raw: 已包含 / 已忽略（仅本地）
```

### .gitignore

```gitignore
.config/
.tmp/
```

配置目录默认不提交 Git（包含技能专用配置、API key 等）。

## 模板文件

本技能在 `references/` 中提供以下模板：

| 模板 | 用途 |
|----------|---------|
| `root-AGENTS.md` | 定义目录结构、领域注册表和跨领域协议的根级 schema |
| `domain-AGENTS.md` | 领域级 schema（名称、内容类型、范围规则） |
| `root-index.md` | 带领域注册表的根索引模板 |
| `domain-index.md` | 领域级索引模板 |
| `gitignore-snippet.md` | wiki 项目的 .gitignore 内容 |

## 常见问题

- **一个实例一个领域**：不要为同一主题创建重叠领域。如果两个领域覆盖范围相同，考虑合并，或在注册表中写清边界。
- **注册表必须准确**：每次新增领域都必须更新根层 `wiki/index.md` 的领域注册表。过期注册表会造成检索盲区。
- **跨领域 wikilink 限制**：`[[domain-page]]` 链接只在同一领域内有效。跨领域导航应使用注册表。
- **不要嵌套领域**：不支持 `domains/<name>/domains/`。每个领域都应是叶子节点。
- **根层用于片段**：根层 `raw/` 与 `wiki/` 用于跨领域或尚未归类的材料。若材料明显属于某个领域，应放入该领域。
- **根层不是 shared/wiki 的替身**：默认不创建 `shared/wiki/`。跨领域综合写在根层 `wiki/`；只有用户明确需要可独立发布的专题集时，才创建额外目录。
- **默认不创建 output/**：产出物目录属于项目工作流，不是 llm-wiki 核心结构。需要时按项目约定单独添加。
- **初始化预览是强制步骤**：展示预览表并获得用户确认前，不要创建文件。
