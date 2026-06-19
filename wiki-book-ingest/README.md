# wiki-book-ingest

将 `raw/books/` 书籍 Markdown **编译**为 `wiki/` 概念页、来源摘要、线索页（逐章 Ingest + Lint 查漏）。

技能目录：<https://github.com/c456-com/skills/tree/main/wiki-book-ingest>

## 快速开始

```
请用 npx skills 安装 c456-com/skills 的 wiki-book-ingest（未安装则先安装；缺 book-extract / karpathy-wiki 也一并安装），
对 domains/stock-trading/raw/books/股是股非 做书籍 ingest。
先列出章节计划和拟建 wiki 页，我确认后再写入。
```

## 流水线位置

```
karpathy-wiki → book-extract → wiki-book-ingest → karpathy-wiki (Query/Lint)
```

## 核心规则

1. **逐章提取** — 每策略/概念独立成页，不可只写目录级概述
2. **图片必转文字** — K 线：形态、位置、信号、案例数据
3. **条件参数不丢** — 选股条件、阈值、操作步骤完整保留
4. **先预览、后写入** — 章节计划须用户确认
5. **Lint 查漏** — 对照章节清单，输出遗漏报告

## 配置（可选）

```bash
cp references/wiki-book-ingest.example.json .config/wiki-book-ingest.json
```

默认 `compile_mode: agent_native`（执行技能的 AI 直接读 raw 写 wiki）。

## 安装

```bash
npx skills add c456-com/skills --skill wiki-book-ingest -y
npx skills update wiki-book-ingest -y
```

## 模板

| 文件 | 用途 |
|------|------|
| [references/chapter-checklist.md](references/chapter-checklist.md) | 章节清单 |
| [references/source-page-template.md](references/source-page-template.md) | 来源摘要 frontmatter |
| [references/lint-report-template.md](references/lint-report-template.md) | 完整性检查报告 |
