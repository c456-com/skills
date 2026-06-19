---
name: karpathy-wiki
description: >-
  通过 LLM 构建持续进化的个人知识库（卡帕西知识库）：Meta-Wiki 双层架构（根 + domains/）、
  目录初始化、Ingest / Query / Lint。当用户提到 karpathy-wiki、初始化知识库、Meta-Wiki、
  domains、Karpathy Wiki、LLM Wiki、个人知识库编译、RAG 替代方案时使用。
---

# Karpathy Wiki（卡帕西知识库）

通过 LLM 构建持续进化的个人知识库，将 AI 从一次性检索器升级为知识编译器。

## 核心思想

传统 RAG 每次提问都要重新读原始文档，知识无法积累。Karpathy 的方法：让 AI 把原始资料编译成一个**持续进化的 Wiki**，AI 不再是检索秘书，而是知识库工程师。

## 三层架构

```
raw/（原始素材层）  ← 你存放，AI 只读
    ↑↓
wiki/（知识库层）   ← AI 生成的结构化 Markdown，互相链接
    ↑↓
AGENTS.md（Schema） ← 定义 AI 如何组织 Wiki
```

## Meta-Wiki 双层架构

多领域知识库在根层再套一层 **领域容器** `domains/`：

```
<project>/                    ← 总知识大脑（跨领域索引）
├── AGENTS.md
├── raw/  wiki/  shared/wiki/
├── domains/
│   └── <domain-name>/        ← 每个领域自包含 raw/wiki/output
│       ├── AGENTS.md
│       ├── raw/  wiki/  output/
├── output/
└── .tmp/
```

| 层级 | 职责 |
|------|------|
| **根** | 跨领域碎片、工具调研、领域注册表 |
| **domains/<name>/** | 单主题深度知识（书、课程、垂直研究等） |

**双层检索**：先读根 `wiki/index.md` 领域注册表 → 进入 `domains/<name>/wiki/index.md` → Ingest/Query/Lint 默认 scope 限定在领域内。跨域：`rg -l "关键词" domains/`。

> **历史兼容**：部分仓库用 `books/` 代替 `domains/`，语义相同，注册表注明实际路径即可。

---

## 初始化知识库（Init）

技能目录：<https://github.com/c456-com/skills/tree/main/karpathy-wiki>

模板：[`references/`](references/)（Agent 读取后按需渲染，**不使用脚本**）

**本技能不包含可执行脚本。** 初始化完全由 Agent 通过对话询问、扫描目录、预览变更、用户确认后，再逐目录、逐文件创建。

### 硬性约束：先预览、用户确认、再执行

**禁止**在未获用户明确确认前创建或修改任何文件。

#### 对话式流程（Agent 执行）

**Phase 1 — 理解意图**

读取技能后，用自然语言确认用户要什么：

- 全新初始化，还是给已有仓库补领域？
- 目标路径（默认当前工作目录）
- 项目名（写入 `AGENTS.md`，如 `my-brain`）
- 首批领域：名称（kebab-case）、中文显示名、一句话定位

信息不足时**逐项追问**，不要一次抛出一长串表单。已给出的参数不要重复问。

**Phase 2 — 扫描现状**

用 `ls` / `Glob` / `Read` 检查目标路径：

- 空目录 → `fresh` 模式
- 已有部分结构 → `merge` 模式（只补缺，**不覆盖**已有 `wiki/*.md` 正文与 `AGENTS.md`）

**Phase 3 — 生成预览表**（必须展示）

| 类别 | 路径 | 操作 | 说明 |
|------|------|------|------|
| 新建目录 | `raw/articles/` … | create | 8 个 raw 子目录 |
| 新建文件 | `AGENTS.md` | create | 根 Schema，自 references 渲染 |
| 新建文件 | `wiki/index.md` | create | 含领域注册表 |
| 跳过 | `wiki/log.md` | skip | 已存在，merge 不覆盖 |
| 新建目录 | `domains/stock-trading/` | create | 首批领域 |

预览末尾附：

- **模式**：`fresh` 或 `merge`
- **将创建**：N 个目录、M 个文件
- **将跳过**：K 个已存在项
- **将覆盖**：0 项（默认禁止；覆盖须单独列出并二次确认）

结尾固定话术：

> 请确认以上变更。回复「确认」后我将开始创建；回复「取消」则中止；可补充修改领域名或路径。

**Phase 4 — 等待确认**

- 用户明确肯定 → 进入 Phase 5
- 用户修改参数 → 重新扫描 + 重新预览
- 用户取消 → 中止，不写入

**Phase 5 — Agent 逐文件创建**

按 `references/` 模板渲染并写入，规则：

1. 目录已存在 → 跳过
2. 文件已存在 → 跳过（merge 默认）
3. 替换占位符：`{{PROJECT_NAME}}`、`{{DATE}}`（今天）、`{{DOMAIN_NAME}}`、`{{DOMAIN_DISPLAY_NAME}}`、`{{DOMAIN_DESCRIPTION}}`、`{{DOMAIN_ROWS}}`
4. 根层与每个领域层按顺序创建，见下文「脚手架清单」
5. 完成后运行验收 checklist 并向用户汇报

**Phase 6 — 可选后续**

询问用户是否：

- 拉取 Karpathy Gist 作为种子素材（`raw/resources/karpathy-llm-wiki.md` + `wiki/sources/` 摘要）
- `git init` 并首 commit（仅用户明确要求时）

#### 脚手架清单（Agent 手动创建）

**根层** — 模板 [`references/root-AGENTS.md`](references/root-AGENTS.md)、[`references/root-index.md`](references/root-index.md)、[`references/log-entry.md`](references/log-entry.md)：

```
raw/{articles,books,papers,courses,resources,quotes,tools,work}/
wiki/{index.md,log.md,entities,concepts,threads,sources,agents}/
shared/wiki/{index.md,log.md}
domains/  output/  .tmp/
AGENTS.md
```

**每个领域** — 模板 [`references/domain-AGENTS.md`](references/domain-AGENTS.md)、[`references/domain-index.md`](references/domain-index.md)：

```
domains/<name>/
├── AGENTS.md
├── raw/{articles,books,papers,courses,resources,quotes,tools,work}/
├── wiki/{index.md,log.md,entities,concepts,threads,sources,agents}/
└── output/
```

根 `wiki/index.md` 的 `{{DOMAIN_ROWS}}` 填注册表行，例如：

`| 股票交易 | \`domains/stock-trading/\` | 技术分析与选股体系 |`

#### 新增领域（add-domain）

同样走 Phase 1–5：先问领域名与定位 → 扫描是否已存在 → 预览 → 确认 → 创建领域目录 + 回写根注册表 + 追加根 `wiki/log.md`（`create | 新增领域 <name>`）。

#### 验收 checklist

- [ ] 根 `AGENTS.md` 含双层检索与 `domains/` 说明
- [ ] 根 `wiki/index.md` 有「领域注册表」
- [ ] 每个领域有 `AGENTS.md` + `wiki/index.md` + `wiki/log.md`
- [ ] `shared/wiki/index.md` 与注册表一致
- [ ] 根 `wiki/log.md` 有 init 记录

---

## 页面类型

### 实体页 `wiki/entities/`
- 命名：小写 kebab-case，如 `andrej-karpathy.md`
- Frontmatter：`type: entity` + `tags: [...]`

### 概念页 `wiki/concepts/`
- 命名：小写 kebab-case，如 `rag.md`

### 线索页 `wiki/threads/`
- 命名：小写 kebab-case，如 `ai-engineering-trilogy.md`

### 来源摘要页 `wiki/sources/`
- 命名：与 raw 文件名呼应
- Frontmatter：`type: source` + `date: YYYY-MM-DD` + `raw: raw/.../xxx.md`

## 链接规范

- 使用 Obsidian Wikilink：`[[page-name]]`
- 链接目标文件名不带 `.md` 后缀
- 页面标题使用一级标题 `# Title`

## 三种核心操作

### Ingest（摄入）

1. 读取素材
2. 创建/更新来源摘要页
3. 提取实体（无则新建，有则追加）
4. 提取概念（无则新建，有则整合）
5. 更新线索页
6. 更新 `wiki/index.md`
7. 追加 `wiki/log.md`

领域素材默认 ingest 到对应 `domains/<name>/`；跨领域碎片可先落根 `raw/work/` 再路由。

### Query（查询）

1. 先读 `wiki/index.md`（根或领域）
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

## 特殊文件规范

### `wiki/index.md`
内容导向的目录，每页一行摘要 + 链接。根层须含领域注册表。每次 Ingest 后更新。

### `wiki/log.md`
时间导向的追加日志。格式：`## [YYYY-MM-DD] 操作类型 | 标题/简述`
操作类型：`ingest`、`query`、`lint`、`update`、`create`、`init`
保持 append-only。

## 与代码项目的关系

Karpathy Wiki 适合存**理论知识**（概念、原理、方法论），不适合存代码实现细节。代码项目的技术文档应放在项目自己的 `docs/` 目录。

### 标准对接模式

```
my-wiki/                            ← 理论知识库
  domains/<domain>/                 ← 某领域理论
    wiki/concepts/                  ← 概念定义
    wiki/entities/                  ← 实体说明

my-code-project/                    ← 代码项目
  docs/20-domain/                   ← 领域文档（含理论映射表）
  AGENTS.md                         ← AI 开发规范
```

### 理论映射表

在代码项目的 `docs/` 中建**理论映射文档**，说明代码功能对应哪个 wiki 理论：

```markdown
## 示例概念

理论定义 → my-wiki/domains/stock-trading/wiki/concepts/example.md

代码实现:
- 入口: src/strategies/example.py
- 调用链: select → filter → score
```

### AI 开发时的读取规则

1. 改代码前，先读理论映射表，找到对应 wiki 路径
2. 从知识库读取理论定义，理解设计意图
3. 改完代码后，更新映射表（若函数签名变化）
4. 理论知识本身不动（wiki 只存理论，不存代码细节）

## 可选扩展：C456 四层

若需与 C456.com 双向同步，读取同仓库 [`c456-llm-wiki`](../c456-llm-wiki/SKILL.md) 技能，在根层或领域层补 `c456-sync/` 与 `wiki/c456-meta.yml`。非默认，用户显式要求时才执行。
