# {{DOMAIN_DISPLAY_NAME}} 知识库规范

本目录为 **{{DOMAIN_DISPLAY_NAME}}** 独立知识库，位于 `domains/{{DOMAIN_NAME}}/`。

## 知识库定位

{{DOMAIN_DESCRIPTION}}

## 内容类型

| 类型 | 说明 | 存放位置 |
|------|------|----------|
| 文章/资料 | 外部文章、政策、报道 | `raw/articles/` |
| 书籍 | 书籍章节 Markdown | `raw/books/` |
| 论文 | 学术论文 | `raw/papers/` |
| 课程 | 课程笔记、视频转录 | `raw/courses/` |
| 资源 | 链接合集、参考文档 | `raw/resources/` |
| 摘录 | 金句、短评 | `raw/quotes/` |
| 工具 | 工具调研素材 | `raw/tools/` |
| 工作笔记 | 灵感、碎片、待整理 | `raw/work/` |

## 领域操作约定

- Ingest / Query / Lint 默认 **scope 限定在本目录**
- 跨领域素材可先落根层 `raw/work/`，再路由 ingest 到本领域
- 更新本领域 `wiki/index.md` 与 `wiki/log.md`；新增领域条目时同步根层注册表

## 命名

- 页面文件：小写 kebab-case（中文主题可用拼音或英文别名）
- Wikilink：`[[page-name]]`，不带 `.md` 后缀
