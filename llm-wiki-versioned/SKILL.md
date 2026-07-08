---
name: llm-wiki-versioned
description: "LLM Wiki versioned / history / provenance：当用户要更新知识页但保留旧结论、查历史版本、做 version diff、恢复页面、追踪事实漂移或检查 snapshot/search history 时触发；用于 .versioned/ 快照和历史搜索规则。"
version: 3.0.1
author: c456-com
license: MIT
platforms: [linux, macos, windows]
tags:
  - wiki
  - llm-wiki
  - knowledge-base
  - versioning
  - history
  - provenance
  - snapshot
  - search
related_skills:
  - llm-wiki
  - llm-wiki-domains
---

# llm-wiki-versioned

给 `llm-wiki` 增加页面级版本历史。它不是替代 `llm-wiki`，而是在标准知识库读写流程上增加三条约束：

1. 更新知识页前，先保存当前版本的完整快照。
2. 当前 wiki 搜索默认只看最新页面，不混入历史版本。
3. 只有用户明确要查旧结论，或当前 wiki 找不到且用户确认追溯时，才搜索历史快照。

适合快速变化的知识库，例如市场情报、竞品分析、产品判断、研究结论、客户洞察和长期决策记录。

## 何时使用

当用户表达以下意图时触发本技能：

- “查一下以前怎么写的”“旧版本是什么”“历史结论是什么”
- “更新这个知识页，但保留旧判断”
- “对比当前版本和之前版本”
- “这个事实变了，记录一下变化”
- “做一次知识库版本 / provenance / history / snapshot 检查”
- “恢复误删的 wiki 页面”

如果用户只是普通摄取、查询或整理知识库，优先使用 `llm-wiki`。只有涉及历史、追溯、版本、恢复、变更记录时，再叠加本技能。

## 存储结构

历史快照集中放在当前 wiki 根目录的 `.versioned/` 下，不放在每个页面旁边。

```text
wiki/
├── .versioned/
│   ├── _registry.yml
│   ├── entities/
│   │   └── baklib-overview.md/
│   │       ├── v1-2026-07-04.md
│   │       ├── v2-2026-07-10.md
│   │       └── INDEX.md
│   └── concepts/
├── entities/
│   └── baklib-overview.md
├── concepts/
├── index.md
└── log.md
```

集中式 `.versioned/` 的目的：

- 删除 `entities/`、`concepts/` 等目录时，历史快照仍可保留。
- 搜索当前知识时可以稳定排除 `.versioned/`。
- 文件和目录的创建、重命名、删除事件统一记录在 `_registry.yml`。

不要使用 `entities/.page-name.md/` 这类同级隐藏目录。它会跟随原目录一起被删除，不利于恢复。

## 当前页 frontmatter

当前有效页面继续保存在正常 wiki 目录中，并增加版本字段。

```yaml
---
title: Baklib 产品概览
created: 2026-07-04
updated: 2026-07-10
version: 2
type: entity
tags: [baklib, product-overview]
confidence: medium
---
```

规则：

- `version` 从 `1` 开始，每次实质更新递增。
- `updated` 写当前更新日期。
- 如果新资料削弱旧结论，更新 `confidence`，不要静默覆盖。
- raw 原始材料不做版本管理，只保留来源和可选 `sha256`。

## 快照格式

更新页面前，把当前页面完整复制到 `.versioned/<relative-path>/<file-name>/vN-YYYY-MM-DD.md`。

```yaml
---
title: Baklib 产品概览
version: 1
snapshot_reason: update
snapshot_date: 2026-07-10
superseded: 2026-07-10
superseded_by: v2
summary: 更新 HelpLook 定价数据，旧价格判断保留为历史版本。
---

这里是被替换前的完整页面内容。
```

`snapshot_reason` 可用值：

| 值 | 场景 |
|----|------|
| `create` | 初始化历史版本 |
| `update` | 普通内容更新 |
| `confidence_change` | 可信度调整 |
| `contradiction` | 新资料与旧结论冲突 |
| `rewrite` | 页面结构或核心论点大幅重写 |
| `archive` | 当前页归档或迁移 |
| `restore` | 从历史版本恢复 |

## 版本索引

每个页面的历史目录下维护一个 `INDEX.md`：

```markdown
# baklib-overview.md 版本历史

| 版本 | 日期 | 原因 | 摘要 |
|------|------|------|------|
| v1 | 2026-07-04 | create | 初始创建 |
| v2 当前 | 2026-07-10 | update | 更新 HelpLook 定价 |
```

当单个 `INDEX.md` 超过 50 条时，可以按年份拆分，例如 `INDEX-2026.md`，主 `INDEX.md` 保留最近版本和归档链接。

## `_registry.yml`

`.versioned/_registry.yml` 记录文件和目录级元数据。保持简单、人工可读，不要求依赖专用工具。

```yaml
version: "1.0"
wiki_root: wiki
created: 2026-07-04

directories:
  entities:
    created: 2026-07-04
    renamed: ~
    deleted: ~
    rename_history: []
    files:
      baklib-overview.md:
        created: 2026-07-04
        deleted: ~
```

需要记录的事件：

| 事件 | 操作 |
|------|------|
| 新建目录 | 在 `directories` 下增加条目 |
| 重命名目录 | 追加 `rename_history` |
| 删除目录 | 设置 `deleted` 日期，必要时移到 `_deleted` |
| 新建页面 | 在对应目录的 `files` 下增加条目 |
| 删除页面 | 设置文件的 `deleted` 日期 |
| 恢复页面 | 记录 `restore` 快照，并清理 deleted 标记 |

## 搜索规则

默认搜索当前 wiki，不搜索 `.versioned/`。

```bash
rg "HelpLook" wiki --glob "*.md" --glob "!.versioned/**"
```

只有在以下情况才搜索历史：

- 用户明确说要查旧版本、历史版本、以前的判断、之前怎么写。
- 当前 wiki 没找到，且用户确认要追溯历史。
- 正在执行版本对比、恢复、provenance 检查。

历史搜索：

```bash
rg "HelpLook" wiki/.versioned --glob "*.md"
```

不要在普通查询中自动 fallback 到 `.versioned/`。这会把过时结论混进当前答案。

## 更新流程

更新任意 wiki 页面时执行：

1. 读取当前页面、相关来源、`index.md` 和近期 `log.md`。
2. 判断是否是实质更新。只改错别字、链接或排版，可不生成快照。
3. 若是实质更新，先把当前页面复制为历史快照。
4. 更新当前页面内容、`version`、`updated`、`confidence`。
5. 更新该页面的 `.versioned/.../INDEX.md`。
6. 更新 `.versioned/_registry.yml` 中的文件记录。
7. 追加 `wiki/log.md`，说明更新原因和新旧版本关系。

## 对比与恢复

对比版本时：

1. 读取当前页面。
2. 读取目标历史版本。
3. 比较事实、判断、置信度、来源、结构变化。
4. 明确哪些结论已过时，哪些仍可复用。

恢复页面时：

1. 先确认用户要恢复的版本。
2. 将当前页面保存为 `snapshot_reason: restore` 或 `archive`。
3. 复制目标历史版本为当前页面。
4. 递增当前页面 `version`，更新 `updated`。
5. 更新 `INDEX.md`、`_registry.yml` 和 `log.md`。

## Health-Check

执行版本化知识库检查时，至少检查：

- 当前页面是否有 `version`、`created`、`updated`。
- 每个当前页面是否有对应 `.versioned/` 历史目录。
- `.versioned/.../INDEX.md` 是否包含当前版本记录。
- `_registry.yml` 是否包含当前目录和文件。
- 已删除页面是否仍可在 `.versioned/` 中找到历史。
- 普通搜索命令是否排除了 `.versioned/`。
- 过时结论是否标记了低置信度或迁移说明。

## 与其他技能配合

| 技能 | 配合方式 |
|------|----------|
| `llm-wiki` | 基础知识库方法：ingest、query、lint、purpose、overview、index、log |
| `llm-wiki-domains` | 多领域容器；每个领域可以独立启用 `.versioned/` |

在多领域项目中，`.versioned/` 应放在对应 wiki 根下：

```text
domains/<domain>/wiki/.versioned/
```

根层 meta-wiki 如果也需要保留历史，则使用：

```text
wiki/.versioned/
```

## 维护原则

- `.versioned/` 通常不提交 Git，可在 `.gitignore` 中排除。
- 历史快照只读，不要直接修改。
- 不要把 raw 原始材料放入 `.versioned/`。
- 不要让历史版本参与默认查询答案。
- 对重大事实变化，优先保留旧判断并解释变化，不要静默覆盖。
