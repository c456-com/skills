# LLM Wiki 维护规范（Schema）

## 1. 目录结构（Meta-Wiki）

本仓库采用 **多层级架构**：顶层为全局索引层，每个 `domains/` 子目录都是完整的独立知识库。

```
{{PROJECT_NAME}}/                   ← Meta-Wiki（全局层）
├── AGENTS.md                       ← 本文件
├── raw/                            ← 跨领域原始素材（AI 只读）
│   ├── articles/  books/  papers/  courses/
│   ├── resources/  quotes/  tools/  work/
├── wiki/                           ← 全局知识库层（AI 生成）
│   ├── index.md                    ← 全局目录 + 领域注册表
│   ├── log.md                      ← 全局操作日志
│   ├── entities/  concepts/  threads/  sources/  agents/
├── shared/wiki/                    ← 跨领域总索引（可选）
│   ├── index.md
│   └── log.md
├── domains/                        ← 领域知识容器
│   └── <domain-name>/              ← 每个领域自包含三层架构
│       ├── AGENTS.md
│       ├── raw/  wiki/  output/
├── output/                         ← 全局主动产出（可选）
└── .tmp/                           ← 临时文件
```

### 1.1 Meta-Wiki 架构说明

| 层级 | 职责 | 检索范围 |
|---|---|---|
| **项目根** | 跨领域碎片、工具调研、全局索引 | 根层 `rg` |
| **domains/<name>/** | 完整三层架构，可单独共享、单独 git init | 领域内检索 |
| **shared/wiki/** | 跨领域线索汇总 | 全局导航 |

**关键原则**：每个 `domains/<name>/` 都是自包含的独立知识库，可以单独共享、单独检索；全局用 `rg -l "关键词" domains/` 跨所有领域搜索。

> **历史兼容**：部分仓库用 `books/` 代替 `domains/`，语义相同。注册表注明实际路径即可，不强制改名。

### 1.2 双层检索协议

1. **全局**：先读 `wiki/index.md`（及可选 `shared/wiki/index.md`）
2. **定位领域**：从「领域注册表」获得 `domains/<name>/` 路径
3. **领域内**：读该领域 `wiki/index.md`；Ingest / Query / Lint **默认 scope 限定在领域内**
4. **跨域**：`rg -l "关键词" domains/` 或根层 `rg`

### 1.3 四层关系（领域内部）

| 层级 | 谁维护 | 用途 |
|---|---|---|
| `raw/` | 用户放入 | 原始素材，AI 只读 |
| `wiki/` | AI 生成 | 提炼后的结构化知识 |
| `output/` | 用户或 AI | 主动产出（论文、指南等） |
| `AGENTS.md` | 用户与 AI 共演进 | 领域专属规范 |

---

## 2. 页面类型

### 实体页 `wiki/entities/`
- 命名：小写 kebab-case
- Frontmatter：`type: entity` + `tags: [...]`

### 概念页 `wiki/concepts/`
- 命名：小写 kebab-case

### 线索页 `wiki/threads/`
- 命名：小写 kebab-case

### 来源摘要页 `wiki/sources/`
- 命名：与 raw 文件名呼应
- Frontmatter：`type: source` + `date: YYYY-MM-DD` + `raw: raw/.../xxx.md`

---

## 3. 链接规范

- 使用 Obsidian Wikilink：`[[page-name]]`
- 链接目标文件名不带 `.md` 后缀
- 页面标题使用一级标题 `# Title`

---

## 4. 三种核心操作

### Ingest（摄入）
1. 读取素材 → 2. 创建/更新来源摘要 → 3. 提取实体 → 4. 提取概念 → 5. 更新线索 → 6. 更新 `index.md` → 7. 追加 `log.md`

### Query（查询）
1. 先读 `index.md` → 2. 定位相关页 → 3. 读取并综合 → 4. 引用来源 → 5. 认可的结果回写 wiki

### Lint（检查）
1. 扫描矛盾 → 2. 发现孤立页 → 3. 检查缺失页 → 4. 评估数据缺口 → 5. 输出报告

---

## 5. 特殊文件规范

### `wiki/index.md`
内容导向的目录，每页一行摘要 + 链接。根层须含「领域注册表」区块。

### `wiki/log.md`
时间导向的追加日志。格式：`## [YYYY-MM-DD] 操作类型 | 标题/简述`
操作类型：`ingest`、`query`、`lint`、`update`、`create`、`init`
保持 append-only。
