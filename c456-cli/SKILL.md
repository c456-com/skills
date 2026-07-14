---
name: c456-cli
description: "C456 CLI / c456.com 操作：当用户要收录 intake、发布 playbook、管理 assets 媒体库、搜索/获取 C456 内容、截图上传或同步 self-hosted C456 数据时触发；用于 CLI 命令、CDP 截图和 API v1 工作流。"
version: 1.3.0
related_skills:
  - c456-sync
  - c456-publish
  - c456-write
---

# C456 CLI（c456-cli）

> **基础能力层技能**。本技能仅覆盖 CLI 命令操作本身。正文格式规范见 `c456-sync`，发布上线流程见 `c456-publish`。

**重要**：发布正文到 C456 前，应先加载 `c456-sync` 技能，按对外正文格式规范撰写 `--body-file`。发布流程见 `c456-publish` 技能。

## Agent 激活时自动检查并启动 CDP

涉及截图（`c456 screenshot`、配图更新、正文插图）前，**主动确保 Chrome CDP 已运行**：

1. 运行 `c456 browser status` 检查是否已有 CDP 连接
2. 若未运行，执行 `c456 browser start` 启动持久 Chrome 实例（默认端口 9222，profile `~/.cache/c456-cli/chrome-profile`，可复用登录态）
3. 记录该后台进程的 session_id，截图都复用同一连接（不需要每次重启）
4. 本次会话截图全部完成后，若不再需要浏览器，执行 `c456 browser stop` 清理

> 依赖系统 Chromium，由 `playwright-core` 自动发现。若系统未安装 Chrome/Chromium，`browser start` 会失败。

在终端通过 **`c456`** 调用 C456 的 **HTTP API v1**，供 Agent 将内容写入/查询 C456，而无需在对话中手写原始 REST 细节。

## 安装 CLI

未安装时可用 **`npx c456-cli …`** 或 **`bunx c456-cli …`**；已全局安装则直接 **`c456`**。

## 鉴权与站点

| 方式 | 说明 |
| --- | --- |
| **API Key** | `c456 config set-key <token>`（默认写入自 cwd 解析的 **`.c456-cli/config.json`**；全局用户配置加 **`-g`**）或 **`C456_API_KEY`** |
| **站点根 URL** | 默认 `https://c456.com`；自托管用 **`c456 config set-url <url>`**（同上 **`-g`**）、**`C456_URL`**，或单次 **`c456 -B <url> …`**。有效配置为 **全局 + 项目合并**（项目覆盖）；工作区由自 cwd 向上的 **`.c456-cli`** 或 **`C456_WORKSPACE`** 决定 |

**短选项冲突**：子命令里的 **`-k` 表示收录类型（kind）**，**不要**用 `-k` 传 API Key。Key 仅通过 `config` / `C456_API_KEY`。

**`-B` 与 `-u`**：根级 **`-B` / `--base-url`** 表示 **C456 站点根地址**；`intake` 等子命令里的 **`-u` 常表示「目标资源 URL」**（如 tool/channel 的链接），不要混用。

## Agent 执行方式

1. 需要真实读写 C456 时，在沙箱/终端中运行 `c456` 子命令，并解析其标准输出（含部分命令附带的 `--- JSON ---` 段）。
2. 非交互场景为 `intake delete` 等加 **`-f` / `--force`**，避免等待终端确认（删除前仍应确认用户意图）。
3. 勿在日志或回复中回显完整 API Key。
4. **严禁编造参数**：只能使用 `c456 <command> --help`（或本仓库源码/文档）明确存在的选项；不确定时先运行 `--help` 再行动。
5. **严禁重复创建**：若 `tool new` / `signal new` / `channel new` / `intake new` / `playbook new` 输出了 `ID:` 或 `--- JSON ---`（含 `id`），视为已成功创建，后续只能 `show <id>` / `update <id>`，不得再次 `new` 重试（避免重复发布两条）。CLI 应同时返回完整的公开 URL（如 `https://c456.com/signals/<id>`），以便直接验证和引用。各类型 URL 模式：signal → `/signals/`、tool → `/tools/`、channel → `/channels/`、playbook → `/playbooks/`。
6. **内容一律用文件传入**：创建/更新正文等长文本时，不要在命令行直接写内容（避免引号/换行/转义错误）。必须把内容写到**当前工作目录**的 `.tmp/` 下临时文件，再用 `--body-file` / `--summary-file` 传入。
7. **自媒体账号默认收录为渠道**：用户要收录 **YouTube / 抖音 / 小红书 / B 站 / 微博** 等**自媒体账号主页或频道**时，**默认使用 `c456 channel new`**（不要用 `c456 tool new`），并配合 `-u <主页或频道 URL>`；需要服务端按 URL 自动填资料段时再加 `--auto-resolve-url`。仅做「不落库的 URL 资料预览/抓取」时用 `c456 fetch profile -p social_account -u "url"`。
8. **渠道（及 tool）必须带至少一条「资料」**：`c456 channel new` 或 `c456 tool new` 时，服务端要求 **profile_data 里至少有一条资料段**（例如主页 **URL**、**媒体账号** 等对应 facet），常见做法是 `-u <url>` 并加 **`--auto-resolve-url`** 让服务端生成资料段；如需手写 **`--profile-data-json`**，**必须先阅读** [references/intake-profile-data-json.md](references/intake-profile-data-json.md)（含各 `profile_id`、必填字段与最小 JSON 示例）。**不能只写标题/正文而不提供 URL/资料段**，否则会 **422 校验失败**（提示含「至少添加一个资料段或图标」等）。
9. **素材库与列表图标**：上传、插入正文、设置 tool/channel 列表图标（`list_icon_url`）见 [references/media-library-and-icons.md](references/media-library-and-icons.md)；CLI：`c456 asset …`、`c456 intake update … --profile-data-json-file`。
10. **工具 / 渠道介绍里的产品截图**：优先 **`c456 browser start`**（持久 profile：`~/.cache/c456-cli/chrome-profile`，可保留登录态）→ 需要时在窗口内登录 → **`c456 screenshot <url> [-o .tmp/…]`** 复用 CDP；结束用 **`c456 browser stop`**。无长会话时可只跑 **`c456 screenshot <url>`**（可省略 **`-o`**，在当前目录按 URL 生成文件名）。然后 **`c456 asset upload`** → **`markdownSnippet`** 写入 **`--body-file`**。**产品官网 / 落地页首屏类截图一律只做视窗截图**：**不要**加 **`-f` / `--full-page`**（默认即为视口高度；整页长图上传后素材处理与阅读体验均易变差）。**仅当**收录时的**产品链接**为 **RubyGems / npm 等包注册表页**（如 **`-u`** 或资料中的包页 URL），并需要**基于该包页**为介绍配截图时：**`c456 screenshot` 的 URL 优先**用 **`c456 fetch profile -p package_registry -u "包页完整URL"`** 解析出的 **GitHub 仓库根页**（`https://github.com/owner/repo`），**不要**优先直接对包页截图。若产品链接已是 **GitHub / 官网 / 文档站**等，或用户**指定了其它截图目标 URL**，则**按该 URL 截图**。详见 [references/product-screenshots-for-intake.md](references/product-screenshots-for-intake.md)。
11. **封面截图与发布上线流程已迁至独立技能**：正文格式规范、配图策略 → 加载 **`c456-sync`**；净稿、CLI 发布、回填元数据、SEO 分发 → 加载 **`c456-publish`**。
12. **用户关键词 → 动作映射**：用户说的日常用语直接映射为以下 CLI 操作序列：

| 用户说 | 含义 | 执行的动作 |
|--------|------|-----------|
| 「收录 XXX」「上传到 c456」「发布到 c456」 | 在 C456 创建一条内容（草稿，仅创建者可见） | **`c456 <kind> new -u <URL> -t "标题" [--auto-resolve-url] --body-file .tmp/净稿.md`** |
| **「对外发布」 / 「公开发布」** | **将内容从草稿改为公开可见** | **`c456 <kind> update <id> --publish`**（申请公开，需审核）或 **`c456 <kind> update <id> --published`**（管理员直接发布） |
| 「配图用 URL」 / 「截图用这个链接」 | 用指定 URL 截图（替代官网首页） | `c456 screenshot <指定URL> -o .tmp/<name>.png` 而非 `c456 screenshot <官网URL>` |
| 「收录这个频道」 / 「收录这个账号」 | 渠道类型 | **`c456 channel new`**（规则 7） |

**⚠️ 区分「发布到 c456」和「对外发布」**：
- 「发布到 c456」= `c456 <kind> new` → 内容存到 C456，**只有创建者能看见**（草稿）
- 「对外发布」= `c456 <kind> update <id> --publish` → **公开可见**（所有人能看见）

**完整示例**：用户说「收录 https://www.shoplazza.cn/ 到 c456 并且对外发布，配图用 https://www.shoplazza.cn/why-choose-shoplazza」
→ ① 调研 shoplazza.cn（电商 SaaS，tool 类型）
→ ② 写 `c456-sync/tool/shoplazza.md` 正文
→ ③ `c456 screenshot https://www.shoplazza.cn/why-choose-shoplazza -o .tmp/shoplazza-hero.png`
→ ④ `c456 asset upload -f .tmp/shoplazza-hero.png`
→ ⑤ 拼接 body（第一行配图 + 正文）
→ ⑥ **`c456 tool new -u https://www.shoplazza.cn/ --auto-resolve-url -t "店匠 | 独立站建站" --body-file .tmp/shoplazza-净稿.md`**
→ ⑦ 记录返回的 ID
→ ⑧ **`c456 tool update <ID> --publish`**（对外发布）
→ ⑨ 回填本地元数据

## 命令速查

**配置**

- `c456 config set-key <token> [-g]` / `set-url <url> [-g]` / `show [-g]` / `reset [-g] [-f]`（`-g` = 仅全局 `~/.config/c456`；默认 = 项目 `.c456-cli`）

**技能 `skill`**

- `c456 skill install [[skillIds...]] [--with-wiki] [-C <cwd>] [-g] [-a <agent>] [--copy]`（仅 `npx skills add`；无参数且为 TTY 时多选菜单；传 `skillIds` 免交互；`--with-wiki` 时装 llm-wiki-domains、c456-llm-wiki 与 c456-cli）

**浏览器（系统 Chrome + CDP）**

- `c456 browser start [-p 端口]` · `stop` · `status`（持久 profile 默认 `~/.cache/c456-cli/chrome-profile`）
- `c456 screenshot <url> [-o <path>] [--full-page] [--viewport 1280x720] [--wait-after-load ms] [--no-reuse] [--keep-github-files-table]`（默认 **`--wait-after-load 3000`**；**github.com** 默认隐藏 README 上方文件表格；**产品官网介绍勿加 `--full-page`**）

**收录 `intake`**

- 新建（AI 自动识别）：`c456 intake new [-u <url>] [--hint signal|tool|channel|playbook] [-t 标题] [--body-file <path>]`
- 新建工具（手动指定）：`c456 tool new -u <url> -t <标题> [--auto-resolve-url] [--body-file <path>]`（profile_data 结构见 [references/intake-profile-data-json.md](references/intake-profile-data-json.md)）
- 新建信号（手动指定）：`c456 signal new -t "标题" [--description "摘要"] --body-file <path>`
- 新建渠道（手动指定）：`c456 channel new ...`（渠道同上支持 `--description`）
- 查看 / 更新 / 删除 / 列表：`c456 intake show <id>` · `c456 intake update <id> …` · `c456 intake delete <id> [-f]` · `c456 intake list [-k] [-q] [-p 页] [-n 每页]`

**搜索 `search`**

- `c456 search signals -q "..." [-k kind] [-l n]`
- `c456 search playbooks -q "..." [-l n]`

**打法 `playbook`**

- 新建：`c456 playbook new -t "标题" [--description "摘要"] --body-file <path> [--ref-intake id …] [--ref-playbook id …]`
- 更新：`c456 playbook update <id> [-t 新标题] [--description "摘要"] [--body-file <path>]`（也支持 `--publish` / `--published` / `--featured` / `--favorited`）

**讲解 `walkthrough`**

- 新建：`c456 walkthrough new …` · 更新：`c456 walkthrough update <id> --body-file <path> [--summary-file <path>]` · 另有 `show` / `list` / `delete`

**素材库 `asset`**

- `c456 asset upload -f <path>` · `list` · `show <id>` · `update <id> --filename <名>` · `delete <id>` · `refresh-markdown` · `fingerprint`

**资料 `fetch`**

- `c456 fetch profile -u <url> -p <profile_id>`（`profile_id` 必填）

`profile_id` 类型含义：
- `link_product`：产品/官网等普通链接页
- `package_registry`：软件包页（npm、RubyGems 等）
- `github_origin`：代码仓库（GitHub/GitLab/Gitee）
- `social_account`：社交账号主页/频道

## 子技能（references/）

| 子技能 | 用途 | 触发条件 |
|--------|------|---------|
| [intake-profile-data-json](references/intake-profile-data-json.md) | profile_data 字段定义与校验 | 手写 `--profile-data-json` |
| [intake-profile-data-quickref](references/intake-profile-data-quickref.md) | 三种最常见 profile_data JSON 模板 | 快速复制 |
| [media-library-and-icons](references/media-library-and-icons.md) | 素材库上传、正文插图、列表图标 | 配图与图标流程 |
| [product-screenshots-for-intake](references/product-screenshots-for-intake.md) | 产品截图最佳实践 | tool/channel 收录配图 |
| [douyin-channel-intake](references/douyin-channel-intake.md) | 抖音渠道收录特殊说明 | 抖音账号收录 |
| [content-syntax-kramdown](references/content-syntax-kramdown.md) | C456 富文本语法 | 生成/写入正文内容 |

## 分层技能体系

| 层级 | 技能 | 职责 |
|------|------|------|
| **基础能力** | `c456-cli`（本技能） | CLI 命令、CDP、鉴权、Agent 规则 |
| **基础能力** | `c456-skills-repo` | 技能仓库维护 |
| **数据同步** | `c456-sync` | 对外正文格式 + 配图策略 |
| **数据同步** | `c456-write` | 信号/产品对比/工具渠道文章写作 |
| **数据同步** | `c456-llm-wiki` | wiki ↔ C456 双向同步 |
| **数据发布** | `c456-publish` | 净稿 → CLI 发布 → 回填 → SEO 分发 |

## 收录最佳实践

- **自媒体 / 社交账号**：一律按渠道收录 → `c456 channel new`
- **渠道 / 工具**：新建时务必带上至少一种结构化资料（`-u` + `--auto-resolve-url`，或 `--profile-data-json`）
- **软件 / 产品 / 仓库**：一般用 `c456 tool new`
- **产品界面进介绍**：优先 `c456 browser` + `c456 screenshot` → `asset upload` → `body`；**官网截图仅视窗**，勿 `-f`
