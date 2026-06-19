# c456 Skills

C456 系列技能库。安装与更新统一使用 **[Vercel `npx skills`](https://github.com/vercel-labs/skills)**（GitHub 为技能源）。

## 技能列表

| 名称 | 说明 |
|------|------|
| [karpathy-wiki](karpathy-wiki/SKILL.md) | Meta-Wiki 初始化 + Query / Lint；[使用说明](karpathy-wiki/README.md) |
| [book-extract](book-extract/SKILL.md) | PDF/拍照 → raw/books（MinerU 或视觉；[README](book-extract/README.md)） |
| [wiki-book-ingest](wiki-book-ingest/SKILL.md) | raw/books → wiki 书籍编译（[README](wiki-book-ingest/README.md)） |
| [c456-software-dev-sop](c456-software-dev-sop/SKILL.md) | 通用软件开发 SOP — 需求→理论调研→兼容性评估→编码→文档同步→验收 |
| [c456-cli](c456-cli/SKILL.md) | C456 CLI 操作命令 |
| [c456-llm-wiki](c456-llm-wiki/SKILL.md) | Karpathy LLM Wiki 知识库管理 |
| [c456-product-channel-article](c456-product-channel-article/SKILL.md) | 产品渠道长文撰写 |
| [c456-signal-product-vs](c456-signal-product-vs/SKILL.md) | 产品对比类 signal 写作 |
| [c456-signal-researcher](c456-signal-researcher/SKILL.md) | 新闻研究员风格 signal 写作 |
| [c456-sync-public-markdown](c456-sync-public-markdown/SKILL.md) | C456 公开 Markdown 同步规范 |

## 书籍录入流水线

```
karpathy-wiki → book-extract → wiki-book-ingest → karpathy-wiki
```

**karpathy-wiki** 在检测到书籍录入时会按 [karpathy-wiki/references/skill-install.md](karpathy-wiki/references/skill-install.md) **自动检查并安装**缺失的 `book-extract`、`wiki-book-ingest`，再从 `npx skills list` 返回的本地 `path` 加载（不用 `../` 相对路径）。

项目根 `.config/<skill-name>.json` 存放 API 配置（git 忽略 `.config/`）。

## 安装（`npx skills`）

在**知识库项目根**执行（会写入对应 Agent 的技能目录并生成 `skills-lock.json`）：

```bash
# 列出本仓库所有技能
npx skills add c456-com/skills -l

# 安装单个（CLI 会询问或自动识别当前 Agent，勿手写 -a）
npx skills add c456-com/skills --skill karpathy-wiki -y

# 书籍流水线
npx skills add c456-com/skills --skill book-extract -y
npx skills add c456-com/skills --skill wiki-book-ingest -y

# 一次装全部
npx skills add c456-com/skills --all -y
```

未加 `-a` 时：`npx skills` 根据环境交互选择 Agent（Cursor、Claude Code、Codex 等），或由执行安装的 AI 代为判断。仅当用户明确指定某 Agent 时才加 `-a <agent>`。

`skills-lock.json` 可提交到 Git，团队对齐同一版本。

## 更新（GitHub 更新后一键同步）

```bash
npx skills check              # 查看哪些技能有更新
npx skills update -y          # 更新全部已安装技能
npx skills update karpathy-wiki -y   # 只更新一个
```

从锁文件还原（类似 `npm ci`）：

```bash
npx skills experimental_install
```

不安装、仅对话里读 GitHub 原文亦可（见各技能 README 的 raw 链接）。
