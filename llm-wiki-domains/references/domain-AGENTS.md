# {{DOMAIN_DISPLAY_NAME}} 知识库

本目录是位于 `domains/{{DOMAIN_NAME}}/` 的独立 llm-wiki 实例。它有自己的 raw、wiki、purpose、overview、index 和 log，默认与其他领域隔离。

## 领域范围

{{DOMAIN_DESCRIPTION}}

## 内容类型

| 类型 | 说明 | 位置 |
|------|-------------|----------|
| 文章 | 外部文章、报告、新闻 | `raw/articles/` |
| 书籍 | 书籍章节 Markdown | `raw/books/` |
| 论文 | 学术论文 | `raw/papers/` |
| 转写 | 会议、访谈、课程、视频转写 | `raw/transcripts/` |
| 附件 | 图片、图表、音视频、其他资产 | `raw/assets/` |
| 工作笔记 | 想法、片段、未处理或待判断材料 | `raw/work/` |

## 领域约定

- 摄取 / 查询 / 检查的默认**范围是本目录**
- 跨领域材料先放入根层 `raw/work/`，再路由到本领域
- 每次开始前先读取 `wiki/purpose.md`、`wiki/overview.md`、`wiki/index.md`、近期 `wiki/log.md`
- 每次变更都要更新 `wiki/index.md` 和 `wiki/log.md`，必要时更新 `wiki/overview.md`
- 添加新领域时同步根层 `wiki/index.md` 中的领域注册表；普通领域内摄取不需要改注册表
- 有价值的查询结果写入 `wiki/queries/`、`wiki/comparisons/` 或相关概念页，不要只留在聊天里

## 命名

- 页面文件：小写 kebab-case
- Wikilinks：`[[page-name]]`，不带 `.md` 后缀

## 标准目录

```text
domains/{{DOMAIN_NAME}}/
├── AGENTS.md
├── raw/
│   ├── articles/  books/  papers/  transcripts/
│   ├── assets/  work/
└── wiki/
    ├── purpose.md
    ├── overview.md
    ├── index.md
    ├── log.md
    ├── sources/
    ├── entities/
    ├── concepts/
    ├── comparisons/
    ├── threads/
    ├── queries/
    └── _meta/
```

## 操作协议

### 摄取

1. 保存 raw，保留来源、日期、原文和可选 `sha256`。
2. 读取 `purpose.md`、`overview.md`、`index.md`、近期 `log.md` 并搜索相关页面。
3. 先做分析阶段：抽取实体、概念、论点、矛盾、建议更新页面。
4. 再做生成阶段：更新 `sources/`、`entities/`、`concepts/`、`comparisons/`、`threads/`、`queries/`。
5. 更新 `index.md`、必要时更新 `overview.md`，并追加 `log.md`。

### 查询

1. 先读 `purpose.md`、`overview.md`、`index.md`。
2. 搜索相关页面，必要时回到 raw 验证关键结论。
3. 回答时引用 wiki 页面或 raw 来源。
4. 如果答案有长期价值，写回 `queries/`、`comparisons/` 或相关页面，并追加 `log.md`。

### 检查

检查断链、孤立页、索引缺失、frontmatter 缺失、来源漂移、低置信度、矛盾内容、过长页面、知识空白，以及页面是否仍服务 `purpose.md` 中的关键问题。
