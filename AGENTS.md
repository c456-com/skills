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
| 技能**描述** | 中文 | `README.md` 技能表、`registry.json` 的 `description`、本地技能 `SKILL.md` frontmatter 的 `description` |
| 正文文档 | 中文 | `README.md`、各技能目录下的 `README.md`、`references/` 等说明性文字 |
| 章节标题、表格列名 | 中文 | 如「名称」「说明」「安装」「维护」 |

**术语处理：**

- 广为人知的英文缩写可保留并在首次出现时括号注明，如 PRD、OKR、GTM、JTBD、ICP。
- 专有框架名可中英并列一次，如「机会-方案树（OST）」。
- 不要整段保留英文描述；从上游同步内容时，应翻译为中文后再写入本仓库文档。

**Submodule 例外：** 不修改 `pm-skills/` 内上游文件的英文原文；在本仓库 `README.md` 的第三方技能表中用**中文描述**索引即可。

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

1. 在根目录创建 `<skill-name>/SKILL.md`（`name` 与目录名一致）。
2. 在 `registry.json` 添加条目：`name`（英文）、`description`（中文）、`tags`、`version`。
3. 在 `README.md` 对应分类表格中增加一行（名称英文、说明中文）。
4. 如需用户向说明，可补充 `<skill-name>/README.md`（中文）。

### 修改技能

- 改行为 → 更新 `SKILL.md` 正文（中文）。
- 改一句话摘要 → 同步 `SKILL.md` frontmatter `description`、`registry.json`（若有）、`README.md` 表格，三处保持一致。
- 版本 bump → 更新 `registry.json` 中该技能的 `version`。

### SKILL.md frontmatter 示例（本地技能）

```yaml
---
name: book-extract
description: 书籍素材提取：PDF 或拍照书页 → raw/books/（MinerU 或视觉大模型）。
---
```

`name` 英文；`description` 中文，含触发场景关键词。

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
- [ ] 描述是否为中文，且 README / registry / SKILL frontmatter 已同步？
- [ ] README 是否仍面向用户（无多余内部架构图/流水线）？
- [ ] 第三方技能是否只改 README 中文索引，未改 submodule 原文？
