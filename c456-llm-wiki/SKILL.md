---
name: c456-llm-wiki
description: "C456 LLM Wiki / c456-sync：当用户要把 llm-wiki 页面发布到 C456、用引用型镜像或 versioned snapshot 绑定线上版本、后接 C456 同步、从 C456 拉回内容、维护 c456-sync/meta.yml 或处理 orphan_local 时触发；用于可插拔 C456 扩展层和 CLI 同步流程。"
version: 1.4.0
related_skills:
  - llm-wiki
  - llm-wiki-versioned
  - c456-cli
  - c456-sync
  - llm-wiki-domains
---

# C456 LLM Wiki — C456 双向同步

## 架构依赖

本技能是本仓库 `llm-wiki` 的 **C456 同步扩展层**。它不提供新的知识库方法论；标准摄取、查询、索引、日志、health-check 仍遵循 `llm-wiki`。

```
llm-wiki                      ← 通用知识库方法论：ingest / query / lint / health-check
    ↑
c456-llm-wiki                ← C456 扩展：c456-sync/ ↔ c456.com
```

多领域场景可再叠加 `llm-wiki-domains`：

```
llm-wiki                      ← 每个领域内的知识库协议
    ↑
llm-wiki-domains             ← 可选：root + domains/ 多领域导航
    ↑
c456-llm-wiki                ← C456 同步：c456-sync/ ↔ c456.com
```

**前置依赖：**

- 必须安装本仓库的 `llm-wiki`。本技能只负责 C456 特有功能。
- 如果当前知识库使用 `domains/<name>/` 多领域结构，再配合 `llm-wiki-domains` 做领域路由。
- 发布、更新、拉取 C456 线上内容时，配合 `c456-cli`。
- 准备对外正文或 `--body-file` 前，配合 `c456-sync` 自检。
- 如果项目启用了 `llm-wiki-versioned`，引用型镜像可绑定具体 wiki 版本或 snapshot，用于判断线上内容是否落后。

## 核心思想

在标准 `llm-wiki` 知识库旁边增加 `c456-sync/` 镜像层，实现本地 wiki 与 c456.com 之间的内容发布、拉取、更新和冲突处理。`wiki/` 继续承担长期知识网络，`c456-sync/` 承担 C456 线上目录、名称、远端 ID、同步状态和必要正文。

`c456-sync/` 是可插拔插件层：一个已有 `llm-wiki` 可以之后再接入 C456 同步；不需要 C456 时，也可以移除或忽略整个 `c456-sync/`，不污染核心 `wiki/` schema。

如果项目是多领域知识库，每个领域都可以独立拥有自己的 `c456-sync/` 和 C456 映射；根层只负责跨领域导航，不替代领域内的 C456 同步。

## 必读：仓库根 `AGENTS.md`

- **§1.2**：c456-wiki **定位、目的、受众**（收集整理 → 对外分享 → 帮互联网读者选择高价值工具与方案）。
- **§1.3**：`c456-sync/` 与 C456 **上行正文**的六条原则——**准确性、可读性、整洁性、逻辑性、推荐性、推广性**（含与 `wiki/` 分工：镜像层单篇自洽、面向陌生读者）。
- **§6.5**：远端记录已删、本地 `c456-sync` / `meta` / `wiki` 仍在时（**orphan_local**）——**先列清单、用户确认后再删或归档**，禁止自动删除；详见下文「orphan_local」与 `AGENTS.md` 全文。

**冷启动 / 初始化目录时**：先打开仓库根 `AGENTS.md`，确认已包含 **§1.2–1.3** 与 **§6.5**（若缺失则补全后再建 `c456-sync/` 或首次 Ingest）；旧模板仅有 §1.2–1.3 时至少补 **§6.5**。可在首条 `wiki/log.md` 注明「已对齐 §1.2–1.3 / §6.5」。

任何写入 **`c456-sync/`**、或组装将提交给 **`c456 intake` / `c456 playbook` / `c456 walkthrough` 的正文** 之前，重读 **§1.3** 自检一遍；**Walkthrough** 另见 `c456-sync` 与 `c456-cli` 的 content-syntax §3（正文勿嵌本页录屏）。

## 扩展结构

```
raw/                  ← llm-wiki 原始素材层，保持可追溯
wiki/                 ← llm-wiki 知识层，长期维护和互联
c456-sync/            ← C456 镜像层，面向线上读者的单篇正文
c456-sync/meta.yml    ← C456 ID 与本地文件的映射索引
AGENTS.md / SCHEMA.md ← 本地 schema 与同步规则
```

## 目录结构

```
.
├── raw/
│   ├── articles/  books/  papers/  transcripts/
│   ├── assets/  work/
├── c456-sync/
│   ├── meta.yml
│   ├── signal/  tool/  channel/  playbook/  walkthrough/
├── wiki/
│   ├── purpose.md  overview.md  index.md  log.md
│   ├── sources/  entities/  concepts/  comparisons/
│   ├── threads/  queries/  _meta/
└── AGENTS.md
```

多领域项目中，上述结构可以出现在某个领域下，例如：

```text
domains/<domain-name>/
├── raw/
├── c456-sync/
├── wiki/
└── AGENTS.md
```

### 三层关系

| 层级           | 谁维护   | 用途      | 与 C456 关系 |
| ------------ | ----- | ------- | --------- |
| `raw/`       | 用户放入  | 原始素材    | 上行时作为内容来源 |
| `c456-sync/` | AI 同步 | C456 镜像或引用描述 | 与线上目录和名称一一对应 |
| `wiki/`      | AI 生成 | 提炼后的知识库 | 多对多映射     |


**关键原则**：`c456-sync/` 与 `wiki/` 之间不用 symlink。关联通过 Frontmatter 引用 + `c456-sync/meta.yml` 实现。C456 同步状态属于插件层，不属于核心 wiki schema。

### c456-sync 与上行正文（执行摘要）

`c456-sync/` 保持 C456 线上的类型目录和文件名。它有两种模式：

- **引用模式 `sync-mode: reference`**：当 C456 内容直接来自某个 wiki 页面时，`c456-sync/<kind>/<slug>.md` 只保存 C456 frontmatter、线上路径/名称和 `source-wiki-path`，正文写简短引用说明。发布时从 `source-wiki-path` 读取并转换正文。
- **正文模式 `sync-mode: body`**：当 C456 需要面向外部读者单独改写、拼接多页、或从线上拉回尚未进入 wiki 的内容时，`c456-sync/<kind>/<slug>.md` 保存完整对外正文。

正文模式的内容须视同 **对外读者可读版本**：事实可核对、结构清晰、有推荐结论与诚实边界、CTA 明确；细节与表格见 **`AGENTS.md` §1.3**。引用模式则检查源 wiki 页面是否能被转换为合格对外正文。

---

## 页面类型

页面类型遵循 `llm-wiki`：`sources/`、`entities/`、`concepts/`、`comparisons/`、`threads/`、`queries/`、`_meta/`。本技能不改变页面分类，只在需要同步 C456 时补充 C456 字段。

### C456 Frontmatter 扩展

准备上行或已从 C456 拉回的 wiki 页面，可补充：

- `c456-kind`: `signal | tool | channel | playbook | walkthrough`
- `c456-title`: 上行 C456 的标题
- `c456-summary`: 上行 C456 的列表/卡片摘要
- `c456-id`: 发布后回填的远端 ID
- `c456-status`: `draft | published | outdated | conflict`
- `c456-sync-path`: 对应 `c456-sync/<kind>/...md`
- `c456-sync-mode`: `reference | body`
- `c456-source-version`: 发布到 C456 时引用的 wiki 当前版本（启用 `llm-wiki-versioned` 时优先写）

来源摘要页 `wiki/sources/` 通常最适合承载 `c456-title` 与 `c456-summary`；实体、概念、线索、比较、查询页也可以在需要直接发布时添加这些字段。

---

## 链接规范

- 使用 Obsidian Wikilink：`[[page-name]]`
- 链接目标文件名不带 `.md` 后缀
- 页面标题使用一级标题 `# Title`

---

## 知识提取边界

知识摄取、查询、检查、书籍逐章提取、图片理解和 wiki 页面维护，优先交给 `llm-wiki`、`book-extract`、`wiki-book-ingest`。本技能只在以下环节介入：

- 判断资料应该对应哪种 C456 类型
- 生成或更新 `c456-sync/` 镜像正文，或引用型镜像描述
- 补充 `c456-title`、`c456-summary`、`c456-kind`、`c456-status`
- 维护 `c456-sync/meta.yml`
- 调用 `c456-cli` 发布、更新或拉取远端内容
- 处理冲突、远端删除和 `orphan_local`

### Ingest 后的 C456 扩展

先遵循 `llm-wiki` 完成定位、分析、写入、索引、日志。只有当资料需要进入 C456 发布或镜像时，再执行以下扩展：

1. **验证基础信息**：用户提供的仓库名、账号名、URL 等可能不准确（如 `lan` 实际是 `ian`）。通过 GitHub API 搜索或直接访问候选 URL 验证后再使用。
2. 判定 C456 类型（signal/tool/channel/playbook/walkthrough）。
3. 选择或创建对应 `c456-sync/<kind>/...md`，保持 C456 线上目录和 slug。
4. 判断镜像模式：若内容直接来自一个 wiki 页面，优先使用 `sync-mode: reference`；若需要外部化改写、组合多页或下行拉回，使用 `sync-mode: body`。
5. 在来源摘要页或目标 wiki 页补充 `c456-title`、`c456-summary`、`c456-kind`、`c456-status`、`c456-sync-mode`。
6. 维护 `c456-sync/meta.yml`：记录本地 wiki 页、镜像文件、远端 ID、checksum、模式和状态。
7. 更新 `wiki/index.md` 与 `wiki/log.md`，说明本次 C456 同步关系。

**C456 类型判定**：介绍工具用法 → `tool`；介绍作者/频道 → `channel`；step-by-step → `walkthrough`；策略/框架 → `playbook`；其余 → `signal`。

### Query（查询）中的 C456 信息

查询仍按 `llm-wiki` 执行。若问题涉及 C456 线上状态，还要读取：

- `c456-sync/meta.yml`
- 相关 wiki 页的 `c456-*` frontmatter
- 对应 `c456-sync/<kind>/...md`
- 必要时通过 `c456-cli` 获取远端最新状态

### Lint / Health-check 中的 C456 信息

通用健康检查交给 `llm-wiki`。本技能额外检查：

1. `c456-sync/` 是否有孤立镜像（找不到对应 wiki 页或远端 ID）。
2. `c456-sync/meta.yml` 是否指向不存在的本地文件。
3. 已发布内容是否缺少 `c456-id`、`c456-kind`、`c456-title`、`c456-summary`。
4. 远端删除时是否形成 `orphan_local`，且是否等待用户确认。
5. `sync-mode: reference` 是否有有效的 `source-wiki-path`，且源文件存在。
6. 若启用 `llm-wiki-versioned`，检查 `source-wiki-version` / `source-wiki-snapshot` 是否落后于当前 wiki 页面版本。
7. `sync-mode: body` 正文是否符合 `c456-sync`。

---

## C456 集成规范

### 内容类型映射


| C456 类型         | 含义     | 常见 raw 来源 | 常见 wiki 映射 | `c456-sync/` 路径 |
| --------------- | ------ | ------------ | ------------- | ---------------- |
| **signal**      | 信息片段   | articles/, papers/, transcripts/, work/ | wiki/sources/, wiki/threads/ | c456-sync/signal/ |
| **tool**        | 工具/软件  | articles/, work/ | wiki/entities/, wiki/comparisons/ | c456-sync/tool/ |
| **channel**     | 频道/账号  | articles/, transcripts/, work/ | wiki/entities/, wiki/sources/ | c456-sync/channel/ |
| **playbook**    | 方法论/框架 | books/, papers/, work/ | wiki/concepts/, wiki/threads/ | c456-sync/playbook/ |
| **walkthrough** | 教程     | articles/, transcripts/, work/ | wiki/threads/, wiki/queries/ | c456-sync/walkthrough/ |


### Frontmatter 扩展

收录五种 C456 类型并准备**上行**时，须在 Frontmatter 中写明 **`c456-title`** 与 **`c456-summary`**，作为同步到 C456 的展示标题信息（与页面正文的一级标题 `# Title` 区分，避免与通用 `title` 字段混淆）。

- **`c456-title`**：主标题（单行，对应 CLI/API 的标题字段）。
- **`c456-summary`**：紧跟标题语义的一句简短说明，用于列表/卡片上的补充展示；上行时与 `c456-title` 一并交给 Agent 或写入请求（具体拼接格式以当次 CLI/API 为准）。

**这句简短描述叫什么**：若强调「从属于主标题的补充短语」，中文常用 **副标题**，英文 **subtitle**；若强调「一句话概括、列表摘要」，产品与 API 语境常用 **摘要**，英文 **summary**（C456 Intake 卡片上与标题配对展示的也是 summary）。营销语境也可称 **标语 / tagline**。本规范 Frontmatter 使用字段名 **`c456-summary`**，语义与上述「摘要」对齐。

```yaml
---
type: source
c456-kind: signal      # signal | tool | channel | playbook | walkthrough
c456-title: "主标题"
c456-summary: "一句简短描述，用作上行列表/卡片摘要（副标题语义）"
c456-sync-mode: reference
c456-source-version: 3
c456-id: 42            # 发布后回填
c456-status: draft     # draft | published | outdated | conflict
date: 2026-05-08
---
```

### 发布工作流（上行）

1. 扫描带 `c456-kind` 但缺 `c456-id` 或 `status: draft` 的页面
2. 读取对应 `c456-sync/<kind>/<slug>.md`，判断 `sync-mode`。
3. 若为 `reference`，从 `source-wiki-path` 读取源 wiki 页面生成发布正文；若为 `body`，直接使用镜像文件正文。
4. **格式自检**：发布正文前，先加载 `c456-sync` 技能。正文必须符合对外格式规范——无 `#` 一级标题、无制作备忘（仓库路径/截图命令/asset ID 解释）、无 `## 总结` / `## TL;DR` 等标签式二级标题；核心判断写在首节正文段落中。
5. 转换 Markdown 为 C456 富文本格式（移除 Wikilink、Frontmatter）
6. 选择命令：signal/tool/channel → `c456 intake new -k <kind>`；playbook/walkthrough → `c456 playbook new`
7. 正文写入 `.tmp/`，通过 `--body-file` 传入 CLI
8. 回填 ID 到 Frontmatter `c456-id`，改 `c456-status: published`，并记录发布时的源 wiki 版本或 checksum
9. 记录日志到 `wiki/log.md`

更新已有内容：用 `c456 intake update <id>` 或 `c456 playbook update <id>`，不重复新建。

### 引用型镜像（减少冗余）

当用户要把知识库中的某个页面直接发布到 C456，例如把 `wiki/entities/andrej-karpathy.md` 作为 C456 的 `channel` 发布时，默认使用引用型镜像：

```text
c456-sync/
└── channel/
    └── andrej-karpathy.md
```

`c456-sync/channel/andrej-karpathy.md` 示例：

```yaml
---
c456-kind: channel
c456-title: "Andrej Karpathy"
c456-summary: "AI 研究者、教育者与 LLM Wiki 方法提出者"
c456-id:
c456-status: draft
sync-mode: reference
source-wiki-path: wiki/entities/andrej-karpathy.md
source-wiki-version: 3
source-wiki-snapshot:
source-wiki-sha256:
remote-slug: andrej-karpathy
---

本文发布内容引用自 `wiki/entities/andrej-karpathy.md`。

发布前请从 `source-wiki-path` 读取源页面，按 `c456-sync` 转换为 C456 对外正文。
```

规则：

- `c456-sync/` 的目录和文件名跟随 C456 线上类型与 slug，而不是 wiki 页面分类。
- `source-wiki-path` 使用相对当前知识库根目录的路径。
- 引用型镜像不复制正文；只保存发布元数据、远端状态、引用关系和必要说明。
- 若需要对 C456 正文做与 wiki 不同的营销化改写、组合多页或删减敏感内容，改用 `sync-mode: body`。
- 发布时记录源 wiki 版本。若启用了 `llm-wiki-versioned`，优先记录 `source-wiki-version`，必要时记录 `source-wiki-snapshot`；否则计算并记录 `source-wiki-sha256`。
- 后续源 wiki 变化但 C456 未更新时，标记 `c456-status: outdated`，并提示用户是否同步到线上。

### 版本化引用（配合 llm-wiki-versioned）

如果当前知识库启用了 `llm-wiki-versioned`，引用型镜像可以指定发布时绑定的源版本：

```yaml
---
sync-mode: reference
source-wiki-path: wiki/entities/andrej-karpathy.md
source-wiki-version: 3
source-wiki-snapshot: wiki/.versioned/entities/andrej-karpathy.md/v3-2026-07-08.md
source-wiki-sha256: "..."
c456-status: published
---
```

规则：

- `source-wiki-version` 表示 C456 线上内容对应的 wiki 页面版本。
- `source-wiki-snapshot` 可选；当发布内容必须严格追溯到某次历史快照时填写。
- 如果当前 `source-wiki-path` 的 frontmatter `version` 大于 `source-wiki-version`，或当前文件 hash 与 `source-wiki-sha256` 不一致，说明本地知识已更新而 C456 线上仍是旧内容。
- 发现版本漂移时，不自动更新线上；先向用户提示差异，并询问是否执行 `c456 intake update <id>` / `c456 playbook update <id>`。
- 用户确认同步后，从当前 wiki 页面重新生成正文，发布成功后更新 `source-wiki-version`、`source-wiki-snapshot`、`source-wiki-sha256`、`c456-status: published` 和 `c456-sync/meta.yml`。
- 如果用户选择暂不同步，保留 `c456-status: outdated`，并在 `wiki/log.md` 记录“本地版本已领先线上”。

### 后接入同步（从 C456 拉回本地）

当本地已经有 `llm-wiki`，用户之后才决定接入 C456，或用户已经在 C456 上发布过内容，需要拉回本地时：

1. **初始化插件层**：只创建 `c456-sync/`、`c456-sync/meta.yml` 和五类镜像目录；不要改动既有 `wiki/` 结构。
2. **拉取远端清单**：通过 `c456-cli` 获取 C456 线上 signal/tool/channel/playbook/walkthrough 列表和详情。
3. **先写镜像**：把远端正文保存为 `c456-sync/<kind>/<slug>.md`，Frontmatter 记录 `c456-id`、`c456-kind`、`remote-updated-at`、`checksum`、`sync-direction: pull`、`sync-mode: body`。
4. **匹配既有 wiki**：用标题、URL、实体名、来源链接和正文关键词搜索 `wiki/`，找到可能的 `local-wiki-source`、`local-wiki-entities`、`local-wiki-concepts`。
5. **更新 meta**：在 `c456-sync/meta.yml` 记录远端 ID、镜像路径、候选 wiki 页面、匹配置信度、同步方向和时间戳。
6. **用户确认关联**：低置信度或一对多匹配时，先列出候选关系让用户确认，避免把线上内容误并入错误知识页。
7. **按 llm-wiki 摄取**：若远端内容包含本地 wiki 还没有的知识，再按 `llm-wiki` 的 ingest 流程生成来源摘要、实体、概念、线索或查询页。
8. **记录日志**：在 `wiki/log.md` 追加 `c456-down-ingest`，说明拉回了哪些远端内容、建立了哪些映射、哪些条目仍待确认。

**原则**：下行同步先保护本地知识库。远端内容先进入 `c456-sync/` 镜像层，不直接覆盖 `wiki/` 页面；是否摄取进知识层由 `llm-wiki` 流程和用户确认决定。

### 双向同步

**c456-sync/ 目录**：作为 C456 镜像层，按五类型分目录存储。`reference` 模式保持线上目录与元数据，正文来自 wiki；`body` 模式保存独立对外正文。从线上拉回后的内容默认是 `body` 模式，之后可在用户确认后改为引用某个 wiki 页面。

**关联方式**：`c456-sync/` 文件 Frontmatter 标注 `source-wiki-path`、`source-wiki-version`、`source-wiki-snapshot`、`local-wiki-source`、`local-wiki-entities` 等字段；`wiki/` 页面 Frontmatter 只保留轻量引用，如 `c456-id`、`c456-kind`、`c456-sync-path`、`c456-sync-mode`、`c456-source-version`；`c456-sync/meta.yml` 记录完整总索引。

**双向索引**：`wiki/index.md` 中已发布条目可标注 `[c456:#id]`。C456 正文可保留回链到本地 Wiki 的链接。

### 远程已删、本地仍存（orphan_local）

见仓库根 **`AGENTS.md` §6.5**：须先向用户输出 **待删除/待处理清单** 并取得 **明确确认** 后，方可删除 `c456-sync/` 或调整 `wiki/` 与 `c456-sync/meta.yml`；可选路径含删镜像、wiki 归档、`meta` 去幽灵 id、或 `intake new` 重发。

### 状态流转

```
draft → publishing → published → outdated → published
                                    ↘ conflict
```

---

## 特殊文件规范

### `wiki/index.md`

内容导向的目录，每页一行摘要 + 链接。按分类组织。每次 Ingest 后更新。

### `wiki/log.md`

时间导向的追加日志。条目格式：`## [YYYY-MM-DD] 操作类型 | 标题/简述`
操作类型：`ingest`、`query`、`lint`、`update`、`create`、`c456-publish`、`c456-down-ingest`、`c456-conflict`
保持 append-only。

### `c456-sync/meta.yml`

C456 ↔ 本地映射总索引。记录每个 C456 ID 的 `sync_path`、`sync_mode`、`source_wiki_path`、`source_wiki_version`、`source_wiki_snapshot`、`wiki_pages[]`、状态、时间戳、checksum。AI 在同步操作中自动维护。

### 与 `llm-wiki-versioned` 配合

- 未启用版本化时：引用型镜像用 `source-wiki-sha256` 判断源 wiki 是否变化。
- 已启用版本化时：引用型镜像优先用 `source-wiki-version` 判断线上内容对应哪个 wiki 版本，必要时用 `source-wiki-snapshot` 指向发布时的快照。
- 普通查询仍只看当前 wiki；只有用户要追溯“发布时的旧版本”或做 C456 线上差异检查时，才读取 `.versioned/`。
- 发现当前 wiki 版本领先线上版本时，先提示“本地已有新版本，C456 线上仍是 vN”，再让用户选择同步、保持线上旧版或查看 diff。

---

## 产品录入调研与数据自动补充（Enrichment）

录入产品（tool 类型）时，若提供的信息不完整（如仅给 GitHub 仓库 URL），AI 应主动上网调研并自动补充多种数据类型。

### 调研来源

| 信息类型 | 调研方法 | 示例 |
|---|---|---|
| **官网** | 从 GitHub README 或组织页提取 | `github.com/rails/rails` → `rubyonrails.org` |
| **包管理器** | 搜索 npm / RubyGems / PyPI / Crates.io / Homebrew | `github.com/rails/rails` → `gem rails` |
| **GitHub 元数据** | 读取仓库页（stars、license、语言、最新发布） | 自动记录 stars 数、许可证、主要语言 |
| **产品描述** | 从官网首页或 README 提炼一句话简介 | 用于 `c456-summary` |
| **核心功能** | 从官网 Features 页或 README 提取 | 用于正文 |
| **安装方式** | 从 README 或官网提取 | apt / brew / npm / Docker 等 |

### 调研流程

1. **输入**：用户提供任意信息（官网 URL、GitHub URL、产品名等）
2. **调研**：AI 使用 WebFetch 工具获取官网、GitHub、包管理器页面
3. **交叉验证**：确认官网与 GitHub 的对应关系
4. **补充**：将调研结果填入 raw 素材、`c456-sync/` 镜像、wiki 页面
5. **发布**：按标准 Ingest 流程创建/更新所有页面

### 数据填充规则

- **c456-title**：`品牌名 | 定位 · 特色后缀`
- **c456-summary**：一句话概括核心价值
- **正文**：包含核心功能模块表、安装方式、适用场景；并自检 **`AGENTS.md` §1.3**（对外可读、可推荐、不夸大）。
- **实体页**：包含关键属性表（官网、GitHub、stars、许可证、语言）、核心功能、差异化亮点、竞品对比
- **来源摘要**：包含核心信息、关键功能、开源信息

### 示例：GitHub URL → 多类型数据

给定 `github.com/rails/rails`，AI 应自动：
1. 读取 GitHub README → 提取官网 `rubyonrails.org`
2. 搜索 RubyGems → 找到 `gem rails`
3. 记录 GitHub stars、许可证（MIT）、主要语言（Ruby）
4. 访问官网 → 提取产品描述、核心功能
5. 创建完整 raw / c456-sync / wiki 页面
6. 发布到 C456

---

## 产品方案讨论（持续更新）

本地 Wiki 与 **C456 SaaS**（`c456-react`）统一演进的产品讨论主本：

- **`wiki/threads/c456-llm-wiki-产品方案讨论.md`** — 类型映射、双轨笔记本、Ruby 学习场景、Public+Personal 共创、演进阶段与 Open Questions

续写讨论时 **append** 该文件 §10「讨论记录」，并更新 `wiki/log.md`。
