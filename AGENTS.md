# c456 Skills — AI 与协作者指南

> 与 [`README.md`](README.md) 分工：`README` 面向**用户**（安装、技能索引）；**本文面向 AI 与仓库维护者**（结构、语言规范、维护流程）。

## 本仓库是什么

- C456 系列 **Agent 技能库**，通过 [`npx skills`](https://github.com/vercel-labs/skills) 从 GitHub 安装。
- 根目录每个文件夹（如 `llm-wiki-domains/`、`c456-cli/`）是一个技能；`registry.json` 登记可被 `npx skills add c456-com/skills` 发现的本地技能。
- `pm-skills/` 为 **git submodule**（上游 [phuryn/pm-skills](https://github.com/phuryn/pm-skills)），技能从上游仓库安装，不在 `registry.json` 中重复注册。

## 语言规范（必须遵守）

**本仓库一切面向用户的文档使用简体中文。**

| 元素 | 语言 | 说明 |
|------|------|------|
| 技能**名称** | 英文（原始） | 目录名、`SKILL.md` frontmatter 的 `name`、安装时的 `--skill` 短名均不改写，如 `create-prd`、`llm-wiki-domains` |
| 技能**描述** | 中文，可混入必要英文触发词 | `registry.json` 与本地技能 `SKILL.md` frontmatter 的 `description` 是 Agent 触发字段；`README.md` 技能表是面向用户的短摘要 |
| 正文文档 | 中文 | `README.md`、各技能目录下的 `README.md`、`references/` 等说明性文字 |
| 章节标题、表格列名 | 中文 | 如「名称」「说明」「安装」「维护」 |

**术语处理：**

- 广为人知的英文缩写可保留并在首次出现时括号注明，如 PRD、OKR、GTM、JTBD、ICP。
- 专有框架名可中英并列一次，如「机会-方案树（OST）」。
- 不要整段保留英文描述；从上游同步内容时，应翻译为中文后再写入本仓库文档。

**Submodule 例外：** 不修改 `pm-skills/` 内上游文件的英文原文；在本仓库 `README.md` 的第三方技能表中用**中文描述**索引即可。

## 技能 description 触发规范

`SKILL.md` frontmatter 的 `description` 与 `registry.json` 的 `"description"` 不是普通简介，而是 Agent 决定是否读取技能的**触发语义入口**。维护时优先把它写成「什么时候该用这个技能」。

参考 `skills.sh` 上高质量技能的写法，描述应包含：

- **任务域**：技能覆盖的对象或领域，如 `React / Next.js`、`tmux pane`、`LLM Wiki / knowledge base`。
- **用户意图**：用户可能说出的动作，如创建、摄取、搜索、查询、更新、监控、编排、恢复、排查、优化。
- **典型场景**：触发技能的具体问题，如“查旧结论”“选择 VM”“做前端页面”“监控 Cursor Agent 是否 STOPPED”。
- **产出或行为**：技能会帮助 Agent 做什么，如生成代码、推荐方案、执行消息协议、做 health-check。
- **常见中英文关键词**：对用户常用中英文混说的领域，保留关键英文，如 `ingest/search/query`、`snapshot/history/provenance`、`zoom/focus/pane`、`EXECUTING/STOPPED`。

描述中应避免：

- 只写功能实现细节、参数名、命令 flag 或内部路径，例如 `--pane 参数用于 session:window.pane`。
- 写成 README 风格的营销口号，缺少可触发的任务动词。
- 把多个技能的职责混在一起；需要协作时用 `related_skills` 和正文说明路由关系。
- 堆砌太多无关关键词，导致本不该触发的场景误触发。

推荐结构：

```yaml
description: "任务域 / English keyword：当用户要做 A、B、C，或提到 X/Y/Z 场景时触发；用于产出 P、执行 Q、检查 R。"
```

示例：

```yaml
description: "Tmux pane / zoom / focus 聚焦规范：当用户要在 tmux 中读取、发送、观察某个窗口或 pane，或需要放大当前对话对象时触发；用于 select-pane、resize-pane -Z 和可见性检查。"
```

`registry.json` 与 `SKILL.md` frontmatter 的 description 必须逐字一致；`README.md` 技能表说明应语义一致，但可以更短、更面向用户阅读。

## README.md 结构

面向用户，不要写维护者操作细节（那些放本文末尾或「维护」节）。

1. **安装** — 本地技能（`c456-com/skills`）与第三方技能（如 `phuryn/pm-skills`）分开说明；注明安装短名 vs 仓库内路径的区别。
2. **更新** — `npx skills check` / `update` / `experimental_install`。
3. **技能列表** — 分节表格：
   - 🧰 通用技能
   - 🏢 C456 通用技能
   - 📦 第三方技能（逐技能列出，路径形如 `pm-skills/pm-execution/create-prd`，链接到 `SKILL.md`）
4. **维护（仓库维护者）** — submodule 添加/更新等（仅 README 最底一节，用户可忽略）。

**不要在 README 中写：** 技能间依赖图、内部流水线拓扑、实现细节——这些属于各技能自己的 `SKILL.md` / `README.md`。

### 技能表格式

```markdown
| 名称 | 说明 |
|------|------|
| [llm-wiki-domains](llm-wiki-domains/SKILL.md) | 多领域知识库导航 — … |
| [pm-skills/pm-execution/create-prd](pm-skills/pm-execution/skills/create-prd/SKILL.md) | 用 8 段式模板撰写产品需求文档（PRD）… |
```

- **名称列**：保留英文路径/技能名，可点击到 `SKILL.md`。
- **说明列**：一行中文摘要，便于用户在 README 中检索。

## 本地技能维护

### 新增技能

1. 在根目录创建 `<skill-name>/SKILL.md`（`name` 与目录名一致，`version: 1.0.0`）。
2. 在 `registry.json` 添加条目：`name`（英文）、`description`（中文）、`tags`、`version`（与 SKILL.md 一致，初始 `1.0.0`）。
3. 在 `README.md` 对应分类表格中增加一行（名称英文、说明中文）。
4. 如需用户向说明，可补充 `<skill-name>/README.md`（中文）。

### 修改技能

- 改行为 → 更新 `SKILL.md` 正文（中文），并**按语义化版本规范 bump 版本号**（见下文）。
- 改触发描述 → 同步 `SKILL.md` frontmatter `description` 与 `registry.json`，两处必须逐字一致；同时检查 `README.md` 表格说明是否需要同步为更短的用户向摘要。若触发范围变化，同样需要 bump 版本号。
- 改 README 表格摘要 → 确保语义仍与技能触发描述一致；若只是用户向措辞优化且不改变触发范围，可不 bump。
- 仅改错别字、链接、排版且**不影响 Agent 行为** → 可不 bump，或仅 bump PATCH（维护者自行判断，建议在 commit message 中说明）。

### 版本号规范（SemVer）

技能更新后**必须**同步 bump 版本号，否则 `npx skills check` 与用户无法感知该技能已变更。版本号遵循 **[语义化版本 2.0.0](https://semver.org/lang/zh-CN/)**（`MAJOR.MINOR.PATCH`）：

| 变更类型 |  bump | 示例 |
|----------|-------|------|
| 修复 bug、纠正错误步骤/命令、不改变对外行为的小修正 | **PATCH** +1 | `1.2.3` → `1.2.4` |
| 新增能力、扩展流程、新 references/脚本、向后兼容的行为增强 | **MINOR** +1（PATCH 归零） | `1.2.3` → `1.3.0` |
| 删除或重命名关键步骤、改变默认行为、破坏已有调用约定 | **MAJOR** +1（MINOR/PATCH 归零） | `1.2.3` → `2.0.0` |

**首次发布**从 `1.0.0` 起（实验性技能可用 `0.y.z`，`0` 阶段 MINOR 视为可能不兼容变更）。

**必须同步更新的位置（两处保持一致）：**

1. **`registry.json`** — 对应技能条目的 `"version"`（`npx skills` 发现与更新检测的来源）
2. **`SKILL.md` frontmatter** — 同名字段 `version:`（若该技能已有此字段；新增技能建议一并写上）

```yaml
---
name: book-extract
description: 书籍素材提取：PDF 或拍照书页 → raw/books/（MinerU 或视觉大模型）。
version: 1.1.3
---
```

**变更流程：**

1. 完成技能内容修改
2. 根据上表判断 bump PATCH / MINOR / MAJOR
3. 同时更新 `registry.json` 与 `SKILL.md` 的 `version`
4. commit message 中注明技能名与新版本，如 `fix(book-extract): … bump to 1.1.3`

若一次 commit 改多个技能，**每个被改动的技能各自独立 bump**，不要共用版本号。

### SKILL.md frontmatter 示例（本地技能）

```yaml
---
name: book-extract
description: 书籍素材提取：PDF 或拍照书页 → raw/books/（MinerU 或视觉大模型）。
version: 1.1.3
---
```

`name` 英文；`description` 中文，含触发场景关键词；`version` 与 `registry.json` 一致。

维护 description 时，先问一句：**“用户怎么说时，Agent 应该想起这个技能？”** 如果答案不能从 description 中直接看出来，就继续补充触发词和场景。

## 第三方技能（submodule）

- 路径：`pm-skills/<plugin>/skills/<skill>/SKILL.md`；README 索引路径简写为 `pm-skills/<plugin>/<skill>`。
- 安装：`npx skills add phuryn/pm-skills --skill <skill-short-name> -y`（短名不含 `pm-skills/` 前缀）。
- 更新 submodule 后，检查 README 第三方技能表是否需增删行；描述从上游 `description` **翻译为中文**。
- **不要**在 submodule 内改文件来回填本仓库；上游变更应通过 submodule 指针更新引入。

## 维护者操作

```bash
# 添加第三方技能包
git submodule add <repo-url> <pack-name>

# 克隆含 submodule 的仓库
git clone --recurse-submodules <repo-url>

# 更新 submodule
git submodule update --init --recursive
git submodule update --remote <pack-name>
```

引入新 submodule 后：更新 README「维护」节（若流程有变）、README 技能列表、必要时 `.gitmodules` 已自动维护。

## 修改前自检

- [ ] 用户向文档是否为中文？
- [ ] 技能名称是否保持原始英文（目录、`name`、链接路径）？
- [ ] `SKILL.md` frontmatter 与 `registry.json` 的 description 是否逐字一致？
- [ ] description 是否写成 Agent 触发语义（任务域 + 用户意图 + 场景关键词 + 产出/行为），而不是参数说明或普通简介？
- [ ] README 技能表说明是否与 description 语义一致，且更适合用户快速阅读？
- [ ] **技能内容有实质变更时，`registry.json` 与 `SKILL.md` 的 `version` 是否已按 SemVer bump 且两处一致？**
- [ ] README 是否仍面向用户（无多余内部架构图/流水线）？
- [ ] 第三方技能是否只改 README 中文索引，未改 submodule 原文？
