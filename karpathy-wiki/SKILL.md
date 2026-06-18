---
name: karpathy-wiki
description: >-
  通过 LLM 构建持续进化的个人知识库（卡帕西知识库）：将 AI 从一次性检索器升级为知识编译器。
  当用户提到 karpathy-wiki、Karpathy Wiki、LLM Wiki、个人知识库编译、RAG 替代方案、raw/wiki/schema 三层架构时使用。
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

## 目录结构

```
.
├── raw/
│   ├── articles/  books/  papers/  courses/
│   ├── resources/  quotes/  tools/  work/
├── wiki/
│   ├── index.md  log.md
│   ├── entities/  concepts/  threads/  sources/  agents/
├── output/
└── AGENTS.md
```

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

### Query（查询）

1. 先读 `wiki/index.md`
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

内容导向的目录，每页一行摘要 + 链接。按分类组织。每次 Ingest 后更新。

### `wiki/log.md`

时间导向的追加日志。条目格式：`## [YYYY-MM-DD] 操作类型 | 标题/简述`
操作类型：`ingest`、`query`、`lint`、`update`、`create`
保持 append-only。

## 与代码项目的关系

Karpathy Wiki 适合存**理论知识**（概念、原理、方法论），不适合存代码实现细节。代码项目的技术文档应放在项目自己的 `docs/` 目录。

### 标准对接模式

```
c456-wiki/                          ← 理论知识库
  books/<domain>/                   ← 某领域理论
    wiki/concepts/                  ← 概念定义
    wiki/entities/                  ← 实体说明

huichang-stock-picker/              ← 代码项目
  docs/20-domain/                   ← 领域文档（含理论映射表）
  AGENTS.md                         ← AI 开发规范
```

### 理论映射表

在代码项目的 `docs/` 中建一个**理论映射文档**，说明代码中的每项功能/算法对应哪个 wiki 理论：

```markdown
## 量时空（LiangShiKong）

理论定义 → c456-wiki/books/股是股非/wiki/concepts/liang-shi-kong.md

代码实现:
- 入口: stock_picker/strategies/liang_shi_kong.py
- 调用链: select → filter_by_lsk → compute_lsk → score_lsk
```

### AI 开发时的读取规则

1. 改代码前，先读理论映射表，找到对应的 wiki 理论路径
2. 从 c456-wiki 读取理论定义，理解设计意图
3. 改完代码后，更新映射表（如果有函数签名变化）
4. 理论知识本身不动（c456-wiki 只存理论，不存代码细节）
