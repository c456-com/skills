# karpathy-wiki

用 AI 在本地初始化并维护 **卡帕西式知识库**（Meta-Wiki 双层架构：根 + `domains/` 领域子库）。

技能目录：<https://github.com/c456-com/skills/tree/main/karpathy-wiki>

**无脚本** — 全部由 AI 对话询问、预览变更、确认后逐文件创建。

## 快速开始

复制以下话术到 Cursor、Claude Code、OpenCode 等 AI Agent 对话：

```
请从 https://github.com/c456-com/skills/tree/main/karpathy-wiki 读取 karpathy-wiki 技能，
帮我在当前目录初始化知识库。
执行前先问我需要哪些领域，展示即将发生的改变，我确认后再创建。
```

带参数的简版：

```
请从 https://github.com/c456-com/skills/tree/main/karpathy-wiki 读取 karpathy-wiki 技能，
帮我在当前目录初始化知识库，项目名 my-brain，先建领域 stock-trading。
执行前先展示即将发生的改变，我确认后再创建。
```

英文：

```
Read the karpathy-wiki skill from https://github.com/c456-com/skills/tree/main/karpathy-wiki,
initialize a knowledge base here. Ask me what domains I need, show a preview of changes,
and wait for my confirmation before creating anything.
```

## 你会看到什么

1. **Agent 读取技能** — 从 GitHub 拉取 `SKILL.md` 与 `references/` 模板
2. **智能询问** — 项目名、目标路径、领域名称与定位（缺什么问什么）
3. **扫描当前目录** — 判断 fresh 还是 merge 模式
4. **变更预览表** — 列出将新建 / 将跳过 / 不覆盖的项
5. **等你确认** — 回复「确认」后 AI 才逐目录、逐文件创建
6. **验收汇报** — 完成后给出 checklist

## 初始化后的目录结构

```
my-brain/
├── AGENTS.md                 # Meta-Wiki 规范
├── raw/                      # 跨领域原始素材（AI 只读）
├── wiki/                     # 全局知识 + 领域注册表
├── shared/wiki/              # 跨领域索引
├── domains/
│   └── stock-trading/        # 领域子库（同构 raw/wiki/output）
│       ├── AGENTS.md
│       ├── raw/
│       └── wiki/
├── output/
└── .tmp/
```

## 日常维护

初始化完成后，同一技能覆盖日常操作：

| 操作 | 示例话术 |
|------|----------|
| 摄入素材 | 「把 raw/articles/xxx.md ingest 进 domains/stock-trading」 |
| 问答 | 「根据 domains/stock-trading 知识库，解释 A 区是什么」 |
| 健康检查 | 「对 domains/stock-trading 跑 lint」 |
| 新增领域 | 「按 karpathy-wiki 技能新增领域 ruby-learning，先问我、再预览、确认后创建」 |

详见 [SKILL.md](SKILL.md)。

## 其它安装方式

| 方式 | 命令 / 链接 |
|------|-------------|
| Hermes | `hermes skills install c456-com/skills/karpathy-wiki` |
| 仅主技能 raw | `https://raw.githubusercontent.com/c456-com/skills/main/karpathy-wiki/SKILL.md` |

## 常见问题

**目录里已有文件怎么办？**
→ merge 模式：AI 只补缺目录和模板，不覆盖已有 `wiki/*.md` 正文。

**想加第二个领域？**
→ 「按 karpathy-wiki 技能，新增领域 ruby-learning，先展示预览，确认后执行。」

**需要 C456 同步？**
→ 另读同仓库 [c456-llm-wiki](../c456-llm-wiki/SKILL.md) 技能，补 `c456-sync/` 层。

**`books/` 和 `domains/` 有什么区别？**
→ 语义相同，都是领域容器。新库用 `domains/`；旧库用 `books/` 可在注册表注明路径，不必强制迁移。

## 文件说明

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | Agent 执行规范（对话式 Init + Ingest + Query + Lint） |
| [references/](references/) | AGENTS / index / log 模板，供 AI 渲染后写入 |
