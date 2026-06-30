---
name: wiki-book-ingest
description: >-
  将 raw/books/ 书籍 Markdown 编译为 wiki 概念页、来源摘要与线索（逐章 Ingest、Lint）。
  用户提到书籍 ingest、raw 编译进知识库、逐章提取、书籍补录、wiki-book-ingest 时使用。
---

# Wiki Book Ingest（书籍知识编译）

将 **book-extract** 产出（或手放的 `raw/books/`）编译为 `wiki/` 可问答知识。

技能目录：<https://github.com/c456-com/skills/tree/main/wiki-book-ingest>

## 技能安装（执行前必做）

按 [`references/skill-install.md`](references/skill-install.md)：**检测 → 缺则安装 → 已装则 update → 从 path 加载**。

1. 检测 `wiki-book-ingest` 是否已安装
2. **未安装** → `npx skills add c456-com/skills --skill wiki-book-ingest -y`
3. 通常还需 `book-extract`、`llm-wiki-domains` — 缺则 `add`；**早已安装**的 → `npx skills update llm-wiki-domains book-extract wiki-book-ingest -y`
4. 从 `npx skills list` 的 `path` 加载 — **禁止** `../book-extract/...` 相对路径

## 前置

- 领域目录已存在（**llm-wiki-domains** Init；无则先安装并执行 Init）
- `domains/<domain>/raw/books/<book>/` 已有 Markdown + `images/`

## 硬性约束

1. **先预览章节计划，用户确认后再批量写 wiki**
2. **知识库目的不是存原文** — 每页须可被问答（定义、条件、步骤、案例数据）
3. **禁止遗漏章节** — 完成后对照 [`references/chapter-checklist.md`](references/chapter-checklist.md) Lint
4. 配置：`.config/wiki-book-ingest.json`（可选；默认可 `compile_mode: agent_native`）

---

## Phase 1 — 解析目录

1. 读取 `raw/books/<book>/` 全部 Markdown（含 `pages/page-*.md` 或 `book.md`）
2. 提取章节标题清单 → 写入 `domains/<domain>/.tmp/<book>-chapter-checklist.md`（基于 [`references/chapter-checklist.md`](references/chapter-checklist.md)）
3. 展示给用户：章节数、拟建 wiki 页类型（concepts / threads / sources / entities）

---

## Phase 2 — 预览计划（必须确认）

| 章节 | 拟建页面 | 路径 |
|------|----------|------|
| 第三章 A 区 | concept | `wiki/concepts/a-qu.md` |
| 案例 600011 | source | `wiki/sources/案例-600011.md` |

结尾：

> 请确认章节编译计划。回复「确认」后开始写入 wiki。

---

## Phase 3 — 逐章 Ingest

对每个章节 / 策略 / 概念：

### 来源摘要 `wiki/sources/`

- 模板：[`references/source-page-template.md`](references/source-page-template.md)
- 命名与 raw 呼应；frontmatter 含 `raw:` 溯源

### 概念页 `wiki/concepts/`

- 定义与原理、分类、适用场景、与其他概念 Wikilink
- **每个独立战法/方法单独成页**

### 线索页 `wiki/threads/`

- 多章串联的方法论、全书脉络

### 实体页 `wiki/entities/`

- 人物、机构、工具

### 图片 / K 线图（必做）

遇到 `![](images/...)` 或书中截图：

1. 读上下文 + 看图（Agent Read 或 raw 中已有文字）
2. 记录：图形特征、出现位置、后续含义、操作信号
3. wiki 中 **保留图片引用 + 文字解释**
4. 案例保留：股票代码、买卖价、时间周期、幅度

### 每批完成后

- 更新 `wiki/index.md`
- 追加 `wiki/log.md`：`## [DATE] ingest | <书名> <章节范围>`

---

## Phase 4 — 完整性 Lint

对照章节清单，输出 [`references/lint-report-template.md`](references/lint-report-template.md) 格式报告：

1. 遗漏章节（参考财学堂补录：曾遗漏 68%，分 P0/P1 批次补）
2. 孤立 wikilink
3. 矛盾表述
4. 图表未转文字

有遗漏 → 列补录计划，用户确认后继续。

---

## LLM 模式

| `compile_mode` | 做法 |
|----------------|------|
| **`agent_native`**（默认） | 执行技能的 Agent 直接读 raw、写 wiki |
| **`external_api`** | 读 `.config/wiki-book-ingest.json` 的 `llm` 块；首版仍由 Agent 写文件，API 仅辅助长文归纳（无需单独脚本） |

示例配置：[`references/wiki-book-ingest.example.json`](references/wiki-book-ingest.example.json)

---

## 验收 checklist

- [ ] 章节清单覆盖率 ≥ 用户预期（通常 95%+）
- [ ] 每概念页含可问答实质内容
- [ ] K 线/图有文字解释
- [ ] `wiki/index.md` 与 `wiki/log.md` 已更新
- [ ] Lint 报告已交付
- [ ] 若在 Git 仓库内：按 **llm-wiki-domains** 安装目录下 `SKILL.md`「Git 版本控制与提交建议」询问是否提交；`raw/` 过大时询问是否排除原始素材

## 相关技能

- 上一步：**book-extract**
- 结构规范：**llm-wiki-domains**
- 安装约定：[`references/skill-install.md`](references/skill-install.md)
