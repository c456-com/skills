# {{PROJECT_NAME}} Wiki Schema（Meta-Wiki 根层）

## 1. 目录结构

本仓库采用**双层架构**：根层是 meta-wiki，负责跨领域目的、注册表、共享概念和查询路由；每个 `domains/` 子目录都是完全独立的 llm-wiki 实例。

```
{{PROJECT_NAME}}/
├── AGENTS.md                       ← 本文件（根级 schema）
├── raw/                            ← 跨领域源材料（AI 只读）
│   ├── articles/  books/  papers/  transcripts/
│   ├── assets/  work/
├── wiki/                           ← 全局知识层（AI 生成）
│   ├── purpose.md                  ← 全局目标、领域边界、关键问题
│   ├── overview.md                 ← 跨领域概要、共享主题、知识空白
│   ├── index.md                    ← 全局索引 + 领域注册表
│   ├── log.md                      ← 全局操作日志
│   ├── sources/  entities/  concepts/  comparisons/
│   ├── threads/  queries/  _meta/
├── domains/                        ← 领域知识容器
│   └── <domain-name>/              ← 每个都是自包含的 llm-wiki
│       ├── AGENTS.md
│       ├── raw/
│       └── wiki/
└── .tmp/                           ← 临时文件
```

### 1.1 层级职责

| 层级 | 内容 | 搜索范围 |
|-------|--------------|--------------|
| **根层** | 全局 purpose、overview、领域注册表、共享概念、待路由材料 | 根层 + 领域注册表 |
| **domains/<name>/** | 自包含 llm-wiki，可独立分享 | 领域内 |

### 1.2 检索协议

1. **全局定位**：读取 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`
2. **判断领域**：从注册表、关键问题和关键词判断单领域、跨领域或待路由
3. **领域定位**：进入相关领域，读取 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`、近期 `wiki/log.md`
4. **跨领域查询**：分别查询相关领域，再把可复用综合写回根层 `wiki/queries/`、`wiki/comparisons/` 或 `wiki/overview.md`
5. **待路由材料**：无法归类的材料先放根层 `raw/work/`，并在 `wiki/log.md` 中记录

## 2. 页面类型

### 实体页 `wiki/entities/`
- 命名：小写 kebab-case
- Frontmatter: `type: entity` + `tags: [...]`

### 概念页 `wiki/concepts/`
- 命名：小写 kebab-case

### 线索页 `wiki/threads/`
- 命名：小写 kebab-case

### 来源摘要页 `wiki/sources/`
- 命名：与 raw 文件名一致
- Frontmatter: `type: source` + `date: YYYY-MM-DD` + `raw: raw/.../xxx.md`

### 比较页 `wiki/comparisons/`
- 用于跨领域横向分析、差异比较、决策依据

### 查询页 `wiki/queries/`
- 保存值得复用的跨领域查询结果，不保存一次性闲聊

### 元信息 `wiki/_meta/`
- 用于 `topic-map.md`、lint 报告、领域边界检查等维护文件

## 3. 链接

- Obsidian Wikilinks：`[[page-name]]`
- 链接中不带 `.md` 后缀
- 页面标题使用 `# Title`（H1）

## 4. 操作

### 摄取
1. 读取根层 `purpose.md` 和领域注册表，判断材料归属
2. 单领域材料进入对应 `domains/<name>/`
3. 跨领域或不确定材料先放入根层 `raw/work/`
4. 在领域内按 llm-wiki 两阶段摄取：先分析，再生成/更新页面
5. 更新领域 `index.md`、`overview.md`、`log.md`
6. 如影响跨领域主题，更新根层 `overview.md` 或 `queries/`

### 查询
1. 读取根层 `purpose.md`、`overview.md`、`index.md`
2. 判断单领域或跨领域
3. 单领域查询进入领域 wiki
4. 跨领域查询分别读取相关领域，再综合共享概念、差异、冲突和知识空白
5. 将有价值的答案保存到领域或根层 `queries/` / `comparisons/`

### 检查
1. 检查断链、孤立页面、索引缺失、frontmatter 缺失
2. 检查 `purpose.md` 对齐度和 `overview.md` 是否过期
3. 检查低置信度、来源漂移、矛盾内容、过长页面
4. 检查领域边界是否重叠，注册表是否准确
5. 输出报告并追加对应 `wiki/log.md`

## 5. 特殊文件

### `wiki/index.md`
内容目录。每页一行（wikilink + 摘要）。根索引必须包含列出所有领域的“领域注册表”章节。

### `wiki/purpose.md`
全局目标、关键问题、领域边界和待验证假设。摄取、查询、检查前必须先读取。

### `wiki/overview.md`
当前跨领域知识地图：共享主题、重要连接、主要矛盾、知识空白、下一步建议摄取资料。

### `wiki/log.md`
仅追加的时间顺序日志。格式：`## [YYYY-MM-DD] action | 标题`
动作：`ingest`、`query`、`lint`、`update`、`create`、`init`
