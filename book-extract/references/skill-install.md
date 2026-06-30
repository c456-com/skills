# 技能安装约定（c456-com/skills）

与 [`llm-wiki-domains/references/skill-install.md`](https://github.com/c456-com/skills/blob/main/llm-wiki-domains/references/skill-install.md) **内容一致**；本文件随 `book-extract` 安装，供单独加载本技能时使用。

## 原则

- **禁止**用 `../其它技能/SKILL.md` 等仓库内相对路径加载技能（只安装单个技能时该路径不存在）。
- **必须**通过 **`npx skills`** 安装到本机，再从安装目录读 `SKILL.md`、`references/`、`scripts/`。
- **禁止**用 WebFetch 只拉 GitHub 上的单个 `SKILL.md` 代替安装（拿不到 `scripts/` 等完整目录）。

## 技能源

| 项 | 值 |
|----|-----|
| 安装源 | `c456-com/skills` |
| GitHub | <https://github.com/c456-com/skills> |

安装命令**不要**手写 `-a cursor`；由 `npx skills` 识别当前 Agent。

## 检测是否已安装

在**知识库项目根**执行：

```bash
npx skills list --json
```

在 JSON 数组中查找 `"name": "<skill-name>"`，记下 `"path"`（技能根目录）。

若无项目级记录，再查全局：

```bash
npx skills list -g --json
```

也可读项目根 `skills-lock.json` 的 `skills` 对象是否含该技能名。

兜底 Glob（按 Agent 实际目录，择一存在即可）：

- `.agents/skills/<skill-name>/SKILL.md`
- `.cursor/skills/<skill-name>/SKILL.md`

## 安装（缺则主动执行）

```bash
cd <知识库项目根>
npx skills add c456-com/skills --skill <skill-name> -y
```

安装后重新 `npx skills list --json` 确认 `path`，并向用户简要汇报（新装 / 已存在）。

## 更新（已安装、本次要用时）

**原则**：

| 情况 | 是否 update |
|------|-------------|
| 本轮刚 `npx skills add` 新装的 | **跳过**（已是远端最新） |
| 检测到**早已安装**、本次流水线要用 | **先更新再读** `SKILL.md` |
| 用户明确说不要更新 / 离线 | 跳过，用本地已装版本并告知 |

**只更新本次涉及的技能**，不要无差别跑 `npx skills check` 或 `npx skills update -y`（会刷新全部已装技能，含无关的 c456-cli 等）。

```bash
# 示例：书籍录入流水线
npx skills update llm-wiki-domains book-extract wiki-book-ingest -y

# 示例：仅 Init
npx skills update llm-wiki-domains -y
```

更新后重新 `npx skills list --json` 取 `path`，再 Read `SKILL.md`。

**Phase 0 完整顺序**（检测 → 安装 → 更新 → 加载）：

1. `npx skills list --json` — 哪些已装、哪些缺失
2. 缺失 → `npx skills add c456-com/skills --skill <name> -y`
3. **早已存在**（非步骤 2 新装）→ `npx skills update <name>... -y`
4. 从 `path` 加载 `SKILL.md` / `references/` / `scripts/`

## 书籍录入流水线 — 须安装的技能

用户要录入 **PDF、拍照书页、书籍编译进 wiki** 时，进入业务步骤**之前**检测下表；**缺哪个装哪个**：

| 技能 | 用途 |
|------|------|
| `llm-wiki-domains` | 领域 Init、Query、Lint、Git 收尾 |
| `book-extract` | PDF/拍照 → `raw/books/` |
| `wiki-book-ingest` | `raw/books/` → `wiki/` |

可一次补齐：

```bash
npx skills add c456-com/skills --skill llm-wiki-domains -y
npx skills add c456-com/skills --skill book-extract -y
npx skills add c456-com/skills --skill wiki-book-ingest -y
```

## 加载已安装技能

1. `npx skills list --json` → 取目标技能的 `path`
2. Read `{path}/SKILL.md`
3. 模板：`{path}/references/`；可执行脚本：`{path}/scripts/`

## 配置示例与脚本路径

从**已安装**技能目录复制（勿用 `../../其它技能/...`）：

```bash
BOOK_EXTRACT_PATH="<book-extract 的 path>"
cp "$BOOK_EXTRACT_PATH/references/book-extract.example.json" .config/book-extract.json

python3 "$BOOK_EXTRACT_PATH/scripts/vision_openai_compatible.py" \
  --project-root . --images-dir .tmp/book-extract/<book-name>/pages --output-dir domains/.../pages --resume
```

`wiki-book-ingest` 的 example 同理：`{wiki_book_ingest_path}/references/wiki-book-ingest.example.json`。
