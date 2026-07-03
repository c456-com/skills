# c456 Skills

C456 系列技能库。安装与更新统一使用 **[Vercel `npx skills`](https://github.com/vercel-labs/skills)**（GitHub 为技能源）。

## 技能列表

### 🧰 通用技能

非 C456 绑定的通用技能，可复用于任意项目。

| 名称 | 说明 |
|------|------|
| [llm-wiki-domains](llm-wiki-domains/SKILL.md) | 多领域知识库导航 — 每个领域独立 llm-wiki 实例，根索引 + 领域注册表 |
| [book-extract](book-extract/SKILL.md) | PDF/拍照 → raw/books（MinerU 或视觉；[README](book-extract/README.md)） |
| [wiki-book-ingest](wiki-book-ingest/SKILL.md) | raw/books → wiki 书籍编译（[README](wiki-book-ingest/README.md)） |
| [tmux-cursor-agent](tmux-cursor-agent/SKILL.md) | 通过 tmux 控制与监控 Cursor AI Agent — 状态检测、消息协议、监控 daemon，支持 pane 级别监控 |
| [cursor-agent-orchestration](cursor-agent-orchestration/SKILL.md) | 编排多个 Cursor Agent 在 tmux 中的团队协作 — 多 session 工作模式、启动序列、预检清单、状态恢复 |
| [doc-driven-multi-agent](doc-driven-multi-agent/SKILL.md) | 文档驱动多代理协作协议 — 角色 SOP、handoff 三要素、门禁 G0–G4、越界拒绝 |
| [c456-software-dev-sop](c456-software-dev-sop/SKILL.md) | 通用软件开发 SOP — 需求→理论调研→兼容性评估→编码→文档同步→验收 |
| [c456-ai-summit](c456-ai-summit/SKILL.md) | Host AI 圆桌峰会 — 多角色 cursor-agent 在 tmux 中协同讨论，动态布局切换、日志体系、agency-agents 集成 |

### 🏢 C456 通用技能

与 C456 业务绑定的技能。

| 名称 | 说明 |
|------|------|
| [c456-cli](c456-cli/SKILL.md) | C456 CLI 操作命令 |
| [c456-llm-wiki](c456-llm-wiki/SKILL.md) | 在 llm-wiki-domains 基础上集成 C456 双向同步 |
| [c456-product-channel-article](c456-product-channel-article/SKILL.md) | 产品渠道长文撰写 |
| [c456-signal-product-vs](c456-signal-product-vs/SKILL.md) | 产品对比类 signal 写作 |
| [c456-signal-researcher](c456-signal-researcher/SKILL.md) | 新闻研究员风格 signal 写作 |
| [c456-sync-public-markdown](c456-sync-public-markdown/SKILL.md) | C456 公开 Markdown 同步规范 |

### 📦 第三方技能（submodule）

其他开源技能或技能包直接以 git submodule 形式引入到仓库根目录，与本地技能平级：

```bash
# 引用单个技能
git submodule add <repo-url> <skill-name>

# 引用技能包（多个技能）
git submodule add <repo-url> <pack-name>
```

引入后可在 `registry.json` 注册个别技能以支持 `npx skills` 发现。

| 名称 | 说明 | 来源 |
|------|------|------|
| [pm-skills](pm-skills/) | 68 个 PM 技能 + 42 个链式工作流，覆盖 discovery、strategy、execution、GTM、growth 等 9 个插件 | [phuryn/pm-skills](https://github.com/phuryn/pm-skills) |

```
pm-skills/                  # submodule — Claude 插件包
  pm-execution/
    skills/
      create-prd/SKILL.md
      brainstorm-okrs/SKILL.md
      ...
llm-wiki-domains/           # 本地技能
c456-cli/                   # 本地技能
...
```

## 书籍录入流水线

```
llm-wiki-domains → book-extract → wiki-book-ingest
                        ↓
                  配置同步到 c456-llm-wiki（可选）
```

**llm-wiki-domains** 在检测到书籍录入时确保 `book-extract`、`wiki-book-ingest` 已安装。

项目根 `.config/<skill-name>.json` 存放 API 配置（git 忽略 `.config/`）。

## 依赖图

```
llm-wiki (Hermes 内置)         ← 单知识库核心引擎
    ↑
llm-wiki-domains               ← 多领域导航（本仓库）
    ↑
c456-llm-wiki                  ← C456 双向同步（本仓库）
```

- `book-extract` + `wiki-book-ingest` 与 `llm-wiki-domains` 配合使用
- `c456-llm-wiki` 依赖 `llm-wiki-domains` 提供多领域结构

## 安装（`npx skills`）

在**知识库项目根**执行（会写入对应 Agent 的技能目录并生成 `skills-lock.json`）：

```bash
# 列出本仓库所有技能
npx skills add c456-com/skills -l

# 安装单个（CLI 会询问或自动识别当前 Agent，勿手写 -a）
npx skills add c456-com/skills --skill llm-wiki-domains -y

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
npx skills update llm-wiki-domains -y   # 只更新一个
```

从锁文件还原（类似 `npm ci`）：

```bash
npx skills experimental_install
```

不安装、仅对话里读 GitHub 原文亦可（见各技能 README 的 raw 链接）。
