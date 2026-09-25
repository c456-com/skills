---
name: tmux-opencode-agent
description: "OpenCode over tmux / OpenCode TUI 驱动与监控：当用户要在 tmux 中启动、驱动或监控 OpenCode，判断某一轮是否结束、处理 Permission required 权限请示面板、并行多个 OpenCode 按 session 归因，或换版本后复验事件能力时触发；用于旁听 SSE 事件流判终态（succeeded/interrupted/failed）、按 sessionID 分流、识别权限面板选中态与卡死。"
version: 1.0.0
author: Hermes Agent (hermes-cto)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [opencode, tmux, monitoring, orchestration, sse, permissions, xiaohui]
    category: xiaohui
    related_skills: [tmux-cursor-agent, cto-delegation-protocol]
---

# 驱动与监控 tmux 里的 OpenCode

> 与 `tmux-cursor-agent` 同类（tmux 里驱动常驻 TUI 小弟）但**机制不同**，不能照搬 Cursor 的判据。
> **必须用可见 TUI**：用户要能在 tmux 里 attach 看到界面；headless / ACP 不适用
> （要 headless 就直接用 `opencode acp`）。SSE 只是**旁听**，不接管 TUI、不改它的显示。

## When to Use

- 把活派给 tmux 里的 OpenCode，且要精准知道它哪一轮说完
- 要处理 OpenCode 的权限请示面板（`Permission required`）
- 一个项目并行多个 OpenCode，需要按会话分开归因
- 换机/换版本后要复验 OpenCode 的事件能力

## 1. 起会话（可见 TUI）

```bash
tmux new-session -d -s <task> -n agent -c <worktree>   # cwd 必须是目标工作树
tmux send-keys -t <task>:0 "opencode"                   # 不加 --auto 才有权限请示
sleep 2; tmux send-keys -t <task>:0 Enter
sleep 15   # 等到出现 "Ask anything…" 输入框
```

⛔ **`--auto` 会自动批准权限** ⇒ 权限面板永不出现。**要观察/管理交互就别加 `--auto`。**

**pane title 空闲态恒为 `OpenCode`，但忙碌时会变成 `OC | <任务名>`**（实测 `OC | Running repeated OC- output…`）
⇒ **可作辅助佐证，不能当权威判活/判结束信号**（Cursor 的 `✅ Ready` / `⏳ Working` 二值信号在这里不存在）。
判活用屏底忙碌行 `esc interrupt`（在跑）/ 无（结束）+ SSE 终态事件；详见 §3.5。

## 2. SSE 事件流（主判据，零配置）

OpenCode 有 background service，TUI 连的是常驻服务端 ⇒ **不需要像 Cursor 那样装 hook**，
旁听服务端事件流即可拿到硬终态。

```bash
# 取服务地址与凭据
URL=$(opencode service status | tr -d '[:space:]')          # http://127.0.0.1:<port>
PW=$(python3 -c "import json;print(json.load(open('$HOME/.config/opencode/service.json'))['password'])")

# 旁听（-N 不缓冲，实时逐行落盘）
curl -s -N -u "opencode:$PW" --max-time <秒> "$URL/api/event" >> <logfile>
```

⛔ **端点要 Basic 鉴权**（`www-authenticate: Basic realm="Secure Area"`），裸 curl 全 401。
用户名固定 `opencode`，密码在 `~/.config/opencode/service.json`。
⛔ **别用 `opencode api GET /api/event`**：它能带凭据但**输出被缓冲**，实时场景收不到事件。
⛔ **别直接 curl `/openapi.json` 拿 spec**：要鉴权；用 `opencode api GET /openapi.json` 拿。
拿到 spec 后 SSE 端点是 `GET /api/event`（`operationId: event.subscribe`），返回 `text/event-stream`。

事件行结构：`{id, created, type, location:{directory}, data:{sessionID, ...}}`
每约 5s 有一行 `: heartbeat`（忽略）。

## 3. 轮次结束判据（三个终态，任一即结束）

| 事件 | 含义 |
|------|------|
| `session.execution.succeeded` | 正常完成 |
| `session.execution.interrupted` | 被打断（发新消息会顶掉待批准请求） |
| `session.step.failed` / `session.tool.failed` | 失败 |

**判据是「本 session 出现过任一终态事件」，不是只看 `succeeded`** —— 只等 succeeded 会漏掉
被打断和失败的轮次。

⛔ **`session.execution.succeeded` ≠ 工具成功**：实测跑不存在的命令（exit 127）**照样发 succeeded**，
它只表示「这一轮执行完成」。`session.tool.success` 同理只表示「调用完成」，不代表业务成功。
⛔ **`session export` 的 `info.outcome` 不能当判据**：实测**运行中它就已是 `succeeded`**（那是上一轮的结果），
用它判本轮会 100% 误判。

**分流**：一条流里混着所有 session 的事件（实测过 4 个并存），按 `data.sessionID` 精确切分，零交叉。
多工作树再按 `location.directory` 分第二层。

## 3.5 五个交互问题的实测答案（与 Cursor 差异最大的一节）

「消息发出没 / 进队列没 / 撤回执行 / 纠正队列内容 / 撤销队列条目」——
**这五问在 OpenCode 上的答案与 Cursor 截然不同，大部分能力缺失。**

| 问题 | 判据 | 动作 |
|------|------|------|
| **消息发送成功没** | ① Enter 前 `capture-pane` 能在**输入框**找到文字 ② Enter 后屏底出现 `esc interrupt` | 两者都要；只看①可能只是没提交 |
| **消息进队列没** | **屏面上无队列 UI**——只能看 `Press ctrl+b to move running work to the background` 提示出现 | ⛔ **无法数条目**，别指望看清有几条 |
| **已发送，想换向/停止** | 发一条 `STOP-NOW: kill …` 式指令；或 `ctrl+b` 把当前工作转后台 | ⚠️ **无 steer**，消息只能等当前轮结束 |
| **队列里那条要改** | **做不到**——无队列列表、无编辑态 | 发新消息显式作废前一条 |
| **撤销队列条目** | **做不到**——`esc` 是打断当前执行，不是撤消息 | 同上 |

### ⛔ 三条能力缺失是实测结论，不是没找到

1. **无 steer 机制**（Cursor 的「空框 Enter 注入队首到当前轮」在 OpenCode 不存在）。
   要「立即改向」只能：打断当前执行（`esc` 连按两次，二次确认），或 `ctrl+b` 转后台。
2. **无队列列表**——忙碌时发消息只显示「Press ctrl+b…」提示，
   **看不到队列里有几条、也改不了其中任何一条**。
3. **`esc` 语义与 Cursor 完全不同**：Cursor 的 `esc` 撤队列条目；
   OpenCode 的 `esc` 第一次把提示改成 `esc again to interrupt`，第二次才打断当前执行。

### 忙碌时 title 会变（修正「恒为 OpenCode」）

空闲态恒为 `OpenCode`，但**忙碌时会变成 `OC | <任务名>`**（实测 `OC | Running repeated OC- output…`）。
⇒ 短窗口采样时它**可用作辅助佐证**；但结束态会回到 `OpenCode`，
所以**不能只靠 title 判结束**，仍以 SSE 终态事件为准。

### 消费后的队列消息不会在屏上重复

实测：忙碌时发的 `OCQ2-MARKER` 转后台后被消费执行，屏上出现它的 Thought 块，
但**原始输入行只出现 1 次**（不重复渲染）——
⇒ 别用「屏上几次」数队列，用 `session.inbox.enqueued` / `delivered` 事件数。

## 4. 权限请示面板（Cursor 的对应物）

面板形态：

```
  △ Permission required
    ← Access external directory ~/somewhere
    Patterns
    - /Users/xiaohui/somewhere/*

     Allow once   Always allow   Reject
     ctrl+f fullscreen  ⇆ select  enter confirm
```

**默认权限是 `{"action":"*","effect":"allow"}`** ⇒ 写文件、普通 shell **不弹面板**。
只有这些会弹（从 agent 权限规则读，别猜）：

- `external_directory`（访问工作树外的目录）
- `read` `*.env` / `*.env.*`（除 `*.env.example`）

⇒ **要测/演示权限面板，用跨目录访问，别用「创建文件」**（那个默认直接放行）。

### 按键语义（实测）

| 键 | 行为 |
|----|------|
| `←` / `→` | 在三项间**循环**切换（两端环绕：`Always allow → Allow once → Reject → Always allow`） |
| `Enter` | 确认选中项 |

⛔ **选中态是颜色高亮，纯文本快照看不出来** —— `capture-pane -p` 三项看起来完全一样。
必须用 `capture-pane -p -e` 读转义序列，选中项背景色是 `48;2;250;178;131`（橙）。
判「我现在选的是哪项」不能靠肉眼看文本。

**拒答后它自己换路继续**（实测：Reject 后 agent 说「Previous tool call declined」然后换个工具继续），
不会卡死等在这儿 —— 这点比 Cursor 的请示门省心。

⛔ **权限状态只能从 SSE 的 `permission.asked` / `permission.replied` 拿**：
`GET /api/permission/request` 在面板明明在等时返回 `data:[]`，**REST 端点不可靠**。

| 事件 | data 关键字段 |
|------|--------------|
| `permission.asked` | `{id, sessionID, action, resources, save, source}` |
| `permission.replied` | `{sessionID, requestID, reply}`（reply = `allow-once` / `always` / `reject` 实测值） |

**卡死判据**：`permission.asked` 已发、长时间无对应 `permission.replied` ⇒ 它在等裁决。

## 5. 事件能力实测表

实测触发（长驻 TUI，多轮）：`server.connected` · `session.execution.started` /
`succeeded` / `interrupted` · `session.step.started` / `ended` / `failed` /
`streamed` · `session.tool.input.started` / `ended` · `called` / `progress` /
`success` / `failed` · `session.reasoning.started` / `delta` / `ended` ·
`session.text.started` / `delta` / `ended` · `session.usage.updated` ·
`session.inbox.enqueued` / `delivered` · `permission.asked` / `replied` ·
`project.updated` · `provider.updated` / `model.updated` · `shell.exited` / `deleted`

⛔ **事件类型不在 OpenAPI spec 里枚举**（spec 只有 `V2EventEncoded: string`）⇒ 换版本要重新实测，
别照抄这张表当契约。

## 6. 与 Cursor 的差异（别互相照搬）

| 维度 | Cursor | OpenCode |
|------|--------|----------|
| 结束信号 | hook（须先于启动配好，忘 chmod 静默失效） | **SSE（零配置）** |
| pane title | `✅ Ready` / `⏳ Working` 可判活 | **恒为 `OpenCode`，不可用** |
| 忙碌指示 | `ctrl+c to stop` | `esc interrupt` |
| 请示门 | `Question N of M` 多问面板，`←/→` 翻页 | `Permission required` 单选三项，`←/→` 循环 |
| 拒答后果 | 容易停住等你 | **自己换路继续** |
| 会话身份 | `create-chat` 预分配 | `session list` 直接列（`ses_...`） |
| 排障入口 | hook 日志 | `session export <id>`（⚠️ 其 `outcome` 不可当判据） |

## 7. 探针任务怎么写

- 在 **scratch 目录**跑探针（业务工作树里会让它去动真文件）。
- 长任务用固定列表（`for i in 1 2 3 …`），别用 `$(seq …)`（折行污染，见 `tmux-cursor-agent` §2.2）。
- 收尾：kill tmux 会话 → **核 SSE curl 进程真的退了**（长连接容易漏杀，
  `terminal` 报退出但进程可能还在，用 `ps` 按 pid 核）。
- SSE 探针正常退出码是 curl 的 `28`（`--max-time` 到点），**不是故障**。

## 相关

- `tmux-cursor-agent` — Cursor 版运行时手册；共享「折行污染」「Busy/Ready 决定落点」等通用坑
- `cto-delegation-protocol` — 派活判据与验收门禁
- `cursor-hook-monitor` — Cursor hook 监控技能包（OpenCode 不需要，SSE 覆盖）
