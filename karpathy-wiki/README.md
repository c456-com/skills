# karpathy-wiki

用 AI 在本地初始化并维护 **卡帕西式知识库**（Meta-Wiki 双层架构：根 + `domains/` 领域子库）。

技能目录：<https://github.com/c456-com/skills/tree/main/karpathy-wiki>

**无脚本** — Init 由 AI 对话询问、预览变更、确认后逐文件创建。

## 快速开始（推荐：一句话安装 + 初始化）

复制到 Cursor、Claude Code、OpenCode 等 Agent 对话。**未安装时 Agent 应先执行 `npx skills add`，再按技能做 Init**（不要只 Fetch GitHub 单个 SKILL.md）：

```
请用 npx skills 安装 c456-com/skills 仓库里的 karpathy-wiki 技能（本地未安装时先安装；
Agent 类型由 npx skills 自动识别，不要写死 -a cursor）。
然后按该技能帮我在当前目录初始化知识库。
执行前先问我需要哪些领域，展示即将发生的改变，我确认后再创建。
```

带参数：

```
请用 npx skills 安装 c456-com/skills 的 karpathy-wiki（未安装则先安装），
帮我在当前目录初始化知识库，项目名 my-brain，先建领域 stock-trading。
执行前先展示即将发生的改变，我确认后再创建。
```

英文：

```
Install karpathy-wiki from c456-com/skills via npx skills if not already installed
(let npx skills detect the agent; do not hardcode -a cursor). Then initialize a knowledge base here.
Ask me what domains I need, show a preview of changes, and wait for my confirmation before creating anything.
```

## 已安装后（日常一句话）

技能已在本地时，无需重复安装：

```
按 karpathy-wiki 技能帮我在当前目录初始化知识库（或新增领域 xxx）。
先预览变更，我确认后再创建。
```

## 免安装（备选，不推荐）

无法跑 `npx` 时，可让 Agent **从 GitHub 拉取完整技能目录**（`SKILL.md` + `references/`），效果不如本地安装，且无法用 `npx skills update` 同步：

```
请从 https://github.com/c456-com/skills/tree/main/karpathy-wiki 读取完整技能（含 references/），
再初始化知识库。先预览变更，确认后创建。
```

## 你会看到什么

1. **安装（若需要）** — `npx skills add c456-com/skills --skill karpathy-wiki -y`
2. **加载技能** — 读本地已安装的 `SKILL.md` 与 `references/` 模板
3. **智能询问** — 项目名、目标路径、领域名称与定位
4. **扫描目录** — fresh 或 merge 模式
5. **变更预览表** — 新建 / 跳过 / 不覆盖
6. **等你确认** — 回复「确认」后才写入
7. **验收汇报** — checklist

## 初始化后的目录结构

```
my-brain/
├── AGENTS.md
├── raw/
├── wiki/
├── shared/wiki/
├── domains/
│   └── stock-trading/
│       ├── AGENTS.md
│       ├── raw/
│       └── wiki/
├── output/
├── .tmp/
└── .config/          # git 忽略，见书籍录入相关技能
```

## 安装与更新（手动）

Agent 未自动安装时，可在项目根自行执行：

```bash
npx skills add c456-com/skills --skill karpathy-wiki -y
npx skills check
npx skills update karpathy-wiki -y    # GitHub 更新后同步
npx skills add c456-com/skills --skill karpathy-wiki -g -y   # 全局安装
```

详见仓库根 [README.md](../README.md)。

## 日常维护

| 操作 | 示例话术 |
|------|----------|
| 摄入素材 | 「把 raw/articles/xxx.md ingest 进 domains/stock-trading」 |
| 问答 | 「根据 domains/stock-trading 知识库，解释 A 区是什么」 |
| 健康检查 | 「对 domains/stock-trading 跑 lint」 |
| 新增领域 | 「按 karpathy-wiki 新增领域 ruby-learning，先预览，确认后创建」 |
| 同步技能 | 「运行 npx skills update karpathy-wiki -y」 |

录入大阶段完成后，若项目在 Git 下，Agent 会**询问是否提交**；`raw/` 过大时会**询问是否排除原始素材**。见 [SKILL.md](SKILL.md)「Git 版本控制与提交建议」。

## 书籍录入流水线

| 步骤 | 技能 |
|------|------|
| 1. 初始化领域 | **karpathy-wiki** |
| 2. PDF/拍照 → raw | [`book-extract`](../book-extract/README.md) |
| 3. raw → wiki | [`wiki-book-ingest`](../wiki-book-ingest/README.md) |
| 4. 问答 / Lint | **karpathy-wiki** |

## 常见问题

**AI 只读了 GitHub 链接、没跑 npx skills？**
→ 用上面「快速开始（推荐）」话术，明确要求 **先 `npx skills add` 再 Init**。

**目录里已有文件怎么办？**
→ merge 模式：只补缺，不覆盖已有 `wiki/*.md`。

**需要 C456 同步？**
→ 另装 [c456-llm-wiki](../c456-llm-wiki/SKILL.md)。

**`books/` 和 `domains/`？**
→ 语义相同；新库用 `domains/`。

**大录入完成后要提交 Git 吗？**
→ 在 Git 仓库内时，Agent 会在 Init / 整本书 ingest 等**大阶段收尾**询问是否 commit；**不会未经你同意自动提交**。

**书页照片、PDF 太大不想进 Git？**
→ 可选只提交 `wiki/`，把 `domains/*/raw/images/` 等写入 `.gitignore`；Agent 会按体积提示并问你。见 `references/git-raw-policy.md`。

## 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 执行规范 |
| [references/](references/) | Init 模板 |
| [references/git-raw-policy.md](references/git-raw-policy.md) | 大体积 raw 是否进 Git |
