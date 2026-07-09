---
name: wiki-book-ingest
description: "书籍知识摄取 / book ingest：当用户要把 raw/books/ 编译进 llm-wiki、逐章提取概念/来源/线索、处理图表文字化或做章节 lint 时触发；用于书籍知识库写入和质量检查。"
version: 1.4.1
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

### 所有衍生页通用出处规则

> 从书籍编译的概念/线索/实体/来源页，**每页都必须记录出处**，格式统一：

```markdown
## 来源

- **书籍**: [[source-page-name]] — 第X章：章节名
- **页码范围**: 第XX-YY页（PDF页码约第XX-YY页）
- **PDF**: `{{PDF_FILENAME}}`（完整路径在 `.extract-meta.yml`）
```

出处信息来自 raw/books/ 的 `.extract-meta.yml`（PDF路径）和各 page-*.md 的内容分析（章节标题、页码）。

### 页面类型选用规则

知识库默认 4 种页面类型：`concepts/`、`entities/`、`threads/`、`sources/`。

当内容明显不适合以上类型时（例如工厂型号、化学物质、法律案卷等），**不允许强行塞入现有类型**，流程如下：

1. 识别到「新类型内容」时，先判断现有没有可容纳的目录
2. **停下来问用户**：建议新建什么类型目录（如 `products/`、`substances/`、`cases/`），用户确认后才创建
3. 新目录首次创建后，在领域 `AGENTS.md` 的「页面类型」章节登记，后续同类内容不再重复询问
4. **不需要预先创建空目录**，有内容时才创建

### 来源摘要 `wiki/sources/`

- 模板：[`references/source-page-template.md`](references/source-page-template.md)
- 命名与 raw 呼应；frontmatter 含 `raw:` 溯源
- **frontmatter 必须维护 `derived:` 字段**，记录本来源衍生的所有概念/线索/实体页（自动随 Ingest 更新）
- **页内「衍生知识」章节**，列出所有从本来源编译的 wiki 页，每页一行

### 概念页 `wiki/concepts/`

- 定义与原理、分类、适用场景、与其他概念 Wikilink
- **每个独立战法/方法单独成页**
- **行级出处标注**：每个关键事实/结论后面用 `^[page-NNN.md]` 标注来源的 raw 页面，实现「事实→raw页面→PDF页码」的双向追溯。编译时：
  1. 读取 raw 页面的内容 + frontmatter（含 `page-indices` → PDF 页码）
  2. 提取该页的核心论据，写入概念页后立即追加 `^[page-NNN.md]`
  3. **1 张图片 = 1 个 page-*.md**（book-extract 产出已是 1:1），不存在「两页合一份」的情况
- **页尾出处章节**：按照上方「通用出处规则」格式

### 线索页 `wiki/threads/`

- 多章串联的方法论、全书脉络
- **页尾出处章节**：按照「通用出处规则」格式，标注覆盖的章/页码范围
- 关键节点也可用 `^[page-NNN.md]` 标记

### 实体页 `wiki/entities/`

- 人物、机构、工具
- **页尾出处章节**：按照「通用出处规则」格式，标注首次出现/主要描述的章节和页码

### 图片 / K 线图（必做）

遇到 `![](images/...)` 或书中截图：

1. 读上下文 + 看图（Agent Read 或 raw 中已有文字）
2. 记录：图形特征、出现位置、后续含义、操作信号
3. wiki 中 **保留图片引用 + 文字解释**
4. 案例保留：股票代码、买卖价、时间周期、幅度

### 每批完成后

- 更新 `wiki/index.md`
- 追加 `wiki/log.md`：`## [DATE] ingest | <书名> <章节范围>`
- **更新来源页**：在来源页的 `derived:` frontmatter 和「衍生知识」章节添加新建的概念/线索/实体链接
- **更新共享来源图谱**：`shared/wiki/来源图谱.md` 中对应书籍条目下添加衍生页链接

---

## Phase 4 — 完整性 Lint

对照章节清单，输出 [`references/lint-report-template.md`](references/lint-report-template.md) 格式报告：

1. 遗漏章节（参考财学堂补录：曾遗漏 68%，分 P0/P1 批次补）
2. 孤立 wikilink
3. 矛盾表述
4. 图表未转文字
5. **出处缺失** — 抽查所有衍生页（概念/线索/实体），确认每页有「来源」章节；概念页还需抽查 `^[page-NNN.md]` 行级标记；缺失率 > 20% 则退回补充

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
