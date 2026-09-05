---
name: tmux-cursor-agent
category: autonomous-ai-agents
tags: [tmux, cursor, agent, monitoring, automation]
description: "Cursor Agent over tmux：当用户要控制、监控或给 tmux 中的 Cursor AI Agent 发消息，判断 EXECUTING/STOPPED、取消执行、轮询 daemon、处理 CURSOR-STOPPED 通知或 pane 级监控时触发；用于状态检测和四步消息协议。"
version: 0.5.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tmux, cursor, agent, monitoring, automation]
    related_skills: [ai-coding-agents, tmux-pane-workspace, doc-driven-multi-agent]
---

# tmux-cursor-agent

> 通过 tmux 控制和监控 Cursor AI agent — 检测状态、发送消息、取消执行。

> **术语别名：** 此用户将 tmux 称为「多窗口终端」(multi-window terminal)。当用户说「多窗口终端」「终端管理器」或「终端分屏」时，将其视为 tmux 的等效说法。此别名适用于全文："启动一个 多窗口终端 会话"、"从 多窗口终端 捕获面板内容"等。

> **Cache note:** Constant tmux sessions (always-on) actually provide the **best** cache utilization vs on-demand sessions. Cursor/Claude Code cache the system prompt and conversation history across turns within the same session. With constant tmux, each follow-up call only pays for new input+output (cached reads at $0.25/MTok vs full $1.25/MTok). On-demand `cursor run` sessions lose this cache advantage — each new call reloads the entire prompt. So for multi-round workflows, keeping sessions alive in tmux is not waste; it is the most efficient approach.

发布于：`c456-com/skills` — <https://github.com/c456-com/skills/tree/main/tmux-cursor-agent>
安装方式：`npx skills add c456-com/skills --skill tmux-cursor-agent -y`
本地克隆：`git clone git@github.com:c456-com/skills.git /path/to/skills`

## 快速参考

### 在 tmux 中启动 cursor-agent

```bash
tmux new-session -d -s cursor -n agent -c /path/to/project
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter
sleep 4
# 验证是否正在运行（pane_current_command 显示 "node" 而不是 "cursor-agent"）
tmux list-windows -t cursor -F '#{window_index}: #{window_name} - #{pane_current_command}'
# 预期：面板显示 "node"（Node.js 运行时），而不是 "zsh" 或 "bash"
```

### 首次设置：登录与工作区信任

首次启动（或清除认证后），cursor-agent 会提示进行基于浏览器的 OAuth 登录：

```bash
# 启动 agent → 它会显示一个登录链接
tmux send-keys -t cursor:0 "cursor-agent --model auto agent" Enter
sleep 8

# 检查是否需要登录
tmux capture-pane -t cursor:0 -p -S -5
# → 显示："Press any key to log in..." 或 loginDeepControl URL

# 按任意键触发浏览器登录
tmux send-keys -t cursor:0 Enter

# 在 macOS 上，浏览器会自动打开。在无头环境中：
# 复制登录 URL 并在另一台机器的浏览器中打开。
sleep 30  # 等待浏览器登录完成

# 登录后：出现 "⚠ Workspace Trust Required" 提示
# 按 'a' 信任工作区，然后等待就绪
tmux send-keys -t cursor:0 a
sleep 10

# 验证就绪：应显示 "→ Plan, search, build anything"
tmux capture-pane -t cursor:0 -p -S -3
```

**同一账户的多个实例共享凭据** — 一旦一个会话登录，其他会话会自动复用令牌。要使用不同的账户，请先清除缓存的令牌（位置因平台而异；检查 `~/.local/share/cursor-agent/`）。

### 检查状态

```bash
git clone https://github.com/c456-com/skills.git /tmp/tmux-cursor-agent
cd /tmp/tmux-cursor-agent/tmux-cursor-agent
python3 -m core.watch cursor 0 --debug
# → state=executing（agent 工作中）或 state=stopped（空闲）
```

或从本地克隆运行：

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.watch cursor 0 --debug
```

### 发送消息（四步协议）

使用四步协议向 cursor-agent 发送消息。**永远不要**将文本和 Enter 合并在一个命令中。

```bash
# 步骤 0：聚焦目标面板 — 发送消息前始终先放大
#    将面板全屏化以便阅读。保持放大状态以观察响应。
#    索引保持不变，其他面板暂时隐藏。
#    正确语法：先 select-pane，然后在同一命令链中放大。
#    不先 select-pane 直接 resize-pane -Z -t（当另一个面板之前被放大时）会静默失败。
tmux select-pane -t session:window.pane \; resize-pane -Z
# 步骤 1：发送前检查 — 任何消息前始终验证 agent 状态
tmux capture-pane -t cursor:0 -p -S -15

# 检查当前状态并判断是否可以发送：
#
# 1. 工作中（spinner / "Working" / "Running" / "Editing" / "Grepping" / "Reading"）：
#    → 不要打断。Agent 正在活跃处理中。等待它完成。
#      消息要么会堆积，要么会扰乱 agent 的上下文。
#
#      例外：如果用户明确要求立即发送（紧急纠正/补充），
#      使用双 Enter 强制提交跳过后续队列：
#        send-keys "text" → sleep 1 → send-keys Enter → sleep 0.5 → send-keys Enter
#      在 Working 状态下单个 Enter 会让文本进入后续队列而非活跃对话。
#
# 2. 等待中（"Waiting Nm for shell" / "Monitoring background task"）：
#    → 消息会进入后续队列（`┌─ follow-ups ───┐`）。
#      仍然可以发送，但需要额外按一次 Enter 才能从队列提交。
#      Agent 会在当前 shell 命令完成后处理它。
#
# 3. 空闲（"→ Add a follow-up" / "Auto" / 无 spinner）：
#    → 干净状态，可以发送。继续。
#
# 4. 输入残留（"→ YOUR_TEXT" 可见）：
#    → 先清除（见下方清理方法）。不要在过期文本上继续输入。
```

**输入框状态：**

| 底栏显示 | 含义 | 操作 |
|---------|------|------|
| `→ Add a follow-up`（或 Plan 占位符） | ✅ 干净，可发送 | 继续执行步骤 1 |
| `→ YOUR_TEXT`（你之前的文本还在） | ❌ 未提交的残留 | 先清除（见下方） |
| `┌─ follow-ups ───┐` + `○ … enter steer`（旧版本显示 `enter send now`） | ❌ 队列模式 | 在空输入中按一次 Enter 提升第 1 条；若框仍在且显示 +N more lines，继续按 Enter 直到框消失 |
| 多行文本不在对话历史中 | ❌ 残留 | 先清除 |

**清除残留（发送前）：**

```bash
# 推荐：按 Escape 清除输入
tmux send-keys -t cursor:0 Escape
sleep 1
tmux capture-pane -t cursor:0 -p -S -10   # 验证只剩下占位符

# 如果 Escape 失效：按 Enter 提交过期文本，
# 等待 agent 处理完毕，然后发送真正的消息。
# 不要在过期文本上继续输入新文本。
```

**不要使用 Ctrl+C 来清除输入。** Ctrl+C 会触发 "Press Ctrl+C again to exit" 状态，此时 Enter 的含义是"不要退出"而非"提交"。

> 有关所有消息传递陷阱的完整参考（agent 状态、输入框状态、后续队列、shell 字符），请参见 [`references/messaging-pitfalls.md`](references/messaging-pitfalls.md)。

```bash
# 步骤 1：输入消息内容（不要按 Enter！）
tmux send-keys -t cursor:0 "Your message here"
# 步骤 2：等待
sleep 2
# 步骤 3：按一次 Enter
tmux send-keys -t cursor:0 Enter
# 步骤 4：验证投递
sleep 3
tmux capture-pane -t cursor:0 -p -S -15
```

**验证投递（步骤 4）：**

| 你看到的 | 含义 | 下一步 |
|---------|------|--------|
| 文本出现在对话历史中 + Working/spinner | ✅ 已投递，执行中 | 完成 |
| 文本出现在对话历史中，尚无 spinner | ✅ 已投递，等待中 | 等待几秒 |
| 输入栏显示 `→ YOUR_TEXT` | ❌ 卡在输入框中 | sleep 2 + 按一次 Enter，重新验证 |
| `┌─ follow-ups ───┐` + `enter steer` 可见 | ❌ 在队列中，非活跃 | 在空输入中按一次 Enter 提升；若框仍显示 +N more lines 再按 Enter（重复直到框消失）；验证文本进入对话历史 |
| 文本在面板中完全不可见 | ❌ 未投递 | 检查 session:window，重试四步协议 |
| `Press Ctrl+C again to exit` | ❌ 误按 C-c | 按一次 Enter 恢复，然后重试 |

不要在未执行步骤 4 验证的情况下声明"消息已发送"。

```bash
# 无需取消放大 — 保持放大状态以观察 agent 的响应。
# 只有在需要查看或与另一个面板交互时才取消放大。
```

**⛔ 最常见的错误：** 忘记步骤 0（放大）。没有放大你无法清楚地阅读 agent 的输出。保持放大 — 其他面板暂时隐藏，但你现在正在对话的 agent 才是最重要的。只有在需要查看或与另一个面板交互时才取消放大。

#### 常见消息传递陷阱

| 陷阱 | 症状 | 修复方法 |
|------|------|----------|
| 文本 + Enter 在一个命令中 | Enter 被吞掉，文本卡在输入框中 | 始终分开执行（中间 sleep 2） |
| 在 agent **等待** shell 时发送 | 文本进入输入缓冲区，永远到不了 agent | Ctrl+C 取消 shell → Enter 恢复 → Escape 清除 → 重新发送 |
| 在 agent **运行**前台命令时发送 | 文本进入后续队列，不会立即处理 | 在空输入中按一次 Enter 将其提升为活跃消息 |
| Shell 特殊字符（`<xxx>`、`` ` ``、`$()`、`>`、`\|`） | Shell 解释为重定向/命令替换，agent 收到乱码或错误 | 用 `[xxx]` 替换 `<xxx>`，移除反引号，避免 `$()` |
| 静默提交（文本在历史中但 agent 保持空闲） | Compass 建议或侧栏拦截 | 再按一次 Enter（不输入新文本）以触发执行 |
| 快速连续发送多条消息 | 第 2+ 条消息变为后续消息，agent 永远看不到 | 将所有内容合并在一条消息中发送，不要拆分 |
| 发送 shell 命令（echo/cat）而非纯文本 | 在 cursor-agent 后面的 shell 中执行，永远到不了对话 | 仅使用纯文本（见 `references/messaging.md` 反模式部分） |

### 取消

```bash
tmux send-keys -t cursor:0 C-c      # 取消执行
tmux send-keys -t cursor:0 Escape   # 清除未提交的输入
```

### 优雅关闭

使用 `/exit` 优雅地关闭 cursor-agent（保留会话状态以便恢复）。不要终止进程或单独使用 C-c。

```bash
# 输入 /exit 并按 Enter（注意自动补全菜单）
tmux send-keys -t cursor:0 "/exit" Enter
sleep 3

# 如果 /exit 显示了自动补全菜单（常见），直接再按一次 Enter
# 确认选择的操作
tmux send-keys -t cursor:0 Enter
sleep 2

# 验证已回到 shell 提示符
tmux capture-pane -t cursor:0 -p -S -2
# → 应显示 shell 提示符（zsh/bash），而非 cursor-agent 界面
```

### 使用守护进程监控

注册会话并启动监控守护进程，以自动接收 CURSOR-STOPPED 通知。

守护进程支持两种面板定位模式：

| 模式 | 示例 | 使用场景 |
|------|------|----------|
| **窗口级**（默认） | `session 0` → `session:0` | 每个窗口一个 agent（团队工作模式） |
| **面板级** | `session 0 --pane 3` → `session:0.3` | 每个窗口多个 agent（会议模式） |

> **面板级布局脚本：** 关于动态多面板布局管理（cols/grid/focus/zoom），参见 `tmux-pane-workspace` 技能的 `scripts/layout.sh`。

#### 窗口级（默认，每个窗口一个 agent）

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.monitor add --group my-group cursor-dev 0 --label "Dev"
```

#### 面板级（一个窗口中多个 agent）

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.monitor add --group summit c456-summit 0 --pane 0 --label "PM"
python3 -m core.monitor add --group summit c456-summit 0 --pane 1 --label "Arch"
python3 -m core.monitor add --group summit c456-summit 0 --pane 2 --label "Dev"
python3 -m core.monitor add --group summit c456-summit 0 --pane 3 --label "Analyst"
```

> **⚠️ 关键：注册前必须验证角色标签。** 不要信任手动设置的面板标题或初始假设。Cursor-agent 在初始化后会动态更新面板标题，因此早期标签通常是错误的。在注册前，请向每个面板询问其身份：
> 1. 向每个面板发送 `你是谁？请用一句话介绍你的角色职责`（四步协议）
> 2. 等待回复，从每个面板的回答中读取实际角色
> 3. 然后用已验证的标签注册
>
> 同时先扫描所有面板 — 不要假设你知道数量：
> ```bash
> tmux list-panes -t session:0 -F '#{pane_index}: #{pane_title}'
> ```
> 窗口中的面板数量可能比你记忆中的多（例如 10 个而不是 6 个）。

#### 多窗口监控（同一组）

一个监控组可以跟踪跨多个窗口的面板。将来自不同窗口的面板注册到同一组中：

```bash
# 窗口 0 的面板
python3 -m core.monitor add --group summit c456-summit 0 --pane 0 --label "PM"
python3 -m core.monitor add --group summit c456-summit 0 --pane 1 --label "ARCH"

# 窗口 1 的面板（同一组）
python3 -m core.monitor add --group summit c456-summit 1 --pane 0 --label "FEASIBILITY-A"
python3 -m core.monitor add --group summit c456-summit 1 --pane 1 --label "FEASIBILITY-B"
```

守护进程针对面板级会发出 `CURSOR-STOPPED:group:session:window:pane:reason`，标识哪个窗口和面板发生了状态变化。

每个面板使用自己的状态文件独立跟踪（`cursor-watch-{session}-{window}-{pane}.state`）。
CURSOR-STOPPED 通知包含面板索引：
- 窗口级：`CURSOR-STOPPED:group:session:window:reason`
- 面板级：`CURSOR-STOPPED:group:session:window:pane:reason`

#### 手动面板状态检查

```bash
cd /path/to/c456-com/skills/tmux-cursor-agent
python3 -m core.watch c456-summit 0 --pane 0 --debug
# → state=executing 或 state=stopped
```

#### 启动守护进程

> **⚠️ 强制前置：执行以下任何命令前，必须先加载本技能**
>
> 你在记忆中保存的 daemon 命令是**错误或过时的**。只有技能文档中的模板包含正确的 `watch_patterns` 参数。
>
> ```python
> # 必须执行这一行，然后读下面三步法
> skill_view(name='tmux-cursor-agent')
> ```
>
> **为什么必须这么做：** 你自己记忆中的 daemon 命令总是缺 `watch_patterns`，导致 CURSOR-STOPPED 永远不会通知到对话。只有每次从这里复制才能保证参数完整。

> **⚠️ 三步执行法（每次必做，缺一不可）**

> | 步 | 命令 | 验证 |
> |----|------|------|
> | **0 加载技能** | `skill_view(name='tmux-cursor-agent')` | 读到当前这行 |
> | **① 杀旧** | `pkill -f "python3 -m core.monitor daemon" 2>/dev/null; sleep 2` | `ps aux \| grep core.monitor \| grep -v grep` → 输出 **空** |
> | **② 注册** | `python3 -m core.monitor add ...` | `python3 -m core.monitor list --group X` → 显示所有 pane |
> | **③ 启动** | `terminal(background=true, watch_patterns=["CURSOR-STOPPED:"], command="cd ~/Codes/c456-com/skills/tmux-cursor-agent && exec python3 -m core.monitor daemon --group GROUP")` | `process(action='poll')` → 显示 `CURSOR-MONITOR-START` |
>
> **⛔ 常见致死错误：**
> - 忘了 `watch_patterns` → daemon 静默运行，你永远收不到任何 CURSOR-STOPPED
> - 用了 `notify_on_complete=true` → daemon 永不完成，此参数对 daemon 无效
> - 不先杀旧进程 → 多个 daemon 打架，state 文件冲突，通知乱发
>
> **正确的模板（直接复制）：**
>
> ```bash
> # ① 杀旧
> pkill -f "python3 -m core.monitor daemon" 2>/dev/null; sleep 2
> ps aux | grep "core.monitor" | grep -v grep | wc -l   # 必须 = 0
>
> # ② 注册（跳过，已注册）
>
> # ③ 启动（关键：同时要 background=true + watch_patterns）
> terminal(
>   command="cd /path/to/skills/tmux-cursor-agent && exec python3 -m core.monitor daemon --group YOUR_GROUP",
>   background=true,
>   watch_patterns=["CURSOR-STOPPED:"]
> )
> ```

## 职责边界

**使用 tmux + cursor-agent 时，应专注于：**

| ✅ 职责范围内 | ❌ 职责范围外 |
|--------------|--------------|
| 在 tmux 中启动/停止 agent | Git worktree 管理 |
| 检测每个面板的 EXECUTING/STOPPED 状态 | 团队角色工作流（PM/Arch/Dev） |
| 窗口级和面板级监控 | 项目特定的代码策略 |
| 发送消息（四步协议） | CI/CD 流水线设置 |
| 取消执行/清除输入 | 多 agent 任务编排 |
| 监控守护进程的状态变化 | 任何应由 agent 自身完成的任务 |
| 捕获面板内容 | |
| 多面板布局设置（3×2、2×2、自定义） | |

## 面板标题状态检测

cursor-agent 会自动将 tmux 面板标题更新为带状态后缀的形式，提供一种无需捕获面板内容的轻量级状态检测方法。

### 设置自定义面板标题（通过 `/rename`）

为防止 cursor-agent 用英文角色名覆盖你的自定义面板标题：

1. 先设置 tmux 面板标题：
   ```bash
   tmux select-pane -t session:0.0 -T "PM 产品经理"
   ```

2. 通过 `/rename` 让 cursor-agent 认领该名称（四步协议）：
   ```bash
   tmux send-keys -t session:0.0 "/rename PM 产品经理"
   sleep 2
   tmux send-keys -t session:0.0 Enter
   ```

`/rename` 之后，cursor-agent 会将自定义名称作为自己的显示名称，只追加状态后缀（` - ✅ Ready` / ` - ⏳ Working`），保留你的标签：
- 空闲：`PM 产品经理 - ✅ Ready`
- 工作中：`PM 产品经理 - ⏳ Working`

**不要**仅依赖 `tmux select-pane -T` — cursor-agent 在下一次状态变化时会用手动设置的标题覆盖为默认英文角色名。

| 标题后缀 | 状态 | 含义 |
|---------|------|------|
| `PM 产品经理`（无后缀，自定义标签） | 空闲 | 面板标题是手动设置的 — 仍然正常工作 |
| `Pricing Analyst - ✅ Ready` | STOPPED | Agent 空闲，等待输入 |
| `Pricing Analyst - ⏳ Working ···` | EXECUTING | Agent 正在活跃处理 |

通过标题后缀检查状态（比 `capture-pane` 更快）：

```bash
title=$(tmux display-message -p -t session:0.4 '#{pane_title}')
echo "$title" | grep -qE "⏳|[⠘⠠⠙⠸⠴⠦]" && echo "EXECUTING" || echo "STOPPED"
```

**注意：** 手动设置的面板标题（如通过 `select-pane -T "PM 产品经理"`）可能会在 cursor-agent 状态变化时被覆盖。在 cursor-agent 启动后重新应用自定义标题，或使用标题后缀作为可靠的替代方案。

### 跨平台状态检测

面板标题后缀（` - ✅ Ready` / ` - ⏳ Working`）在 **macOS** 上可靠工作。在 **Linux** 上，cursor-agent 始终将标题保持为 `Cursor Agent`，与状态无关 — 需要回退到内容扫描：

```bash
content=$(tmux capture-pane -t session:0.pane -p -S -5)
echo "$content" | grep -qE "(Working|Reading|Thinking|Editing)" && echo "EXECUTING"
```

`layout.sh auto` 命令实现了双模式（标题优先，内容回退）。

### 面板标题的 tmux 设置

为使 cursor-agent 的标题更新生效：

```bash
tmux set -t session:window automatic-rename off   # 防止 tmux 覆盖标题
tmux set -g allow-rename on                        # 允许程序设置标题
tmux set -t session pane-border-status top         # 在面板边框中显示标题
tmux set -t session pane-border-format '#{pane_title}'  # 在边框中显示面板标题
```

## 陷阱

1. **错误的面板**：发送前始终检查 `pane_current_command` 是否为 Node 进程（显示 `node`）。窗口名称不可靠。
2. **Enter 被吞**：始终将文本与 Enter 分开（中间 sleep 2）。永远不要 `send-keys "text" Enter` 一次性执行。
3. **未验证**：发送后始终 `capture-pane` 确认消息在对话历史中，而非卡在输入栏。
4. **执行期间发送**：先检查状态。如果 agent 正在 EXECUTING，请等待。
5. **占位符 ≠ 空闲**：`→ Add a follow-up` 是一个空的输入框，不是任务完成信号。
6. **百分比 ≠ 进度**：`Auto · 84.8%` 是上下文窗口使用率，不是任务进度。
7. **选择菜单**：使用方向键 + 空格，永远不要直接发送数字。
8. **守护进程无面板**：启动守护进程后验证 `total > 0`，否则它什么都不会监控。
9. **`/exit` 自动补全**：输入 `/exit` 通常会显示自动补全菜单。始终发送两次 Enter：一次从菜单选择 `/exit`，一次确认。之后检查面板 — 如果仍在 cursor-agent UI 中，再发送一次 Enter。
10. **`pane_current_command` 显示 `node` 而非 `cursor-agent`**：cursor-agent 运行在 Node.js 上，所以 `pane_current_command` 会是 `node`，而非 `cursor-agent`。使用 `capture-pane` 内容验证 agent 实际正在运行。
11. **工作区信任阻止启动**：OAuth 登录后，cursor-agent 会显示一个需要按 `a` 键的信任对话框。没有它，agent 保持阻塞状态，不会接受任何输入。
12. **多会话认证共享**：在另一个 tmux 窗口中启动第二个 cursor-agent 会自动复用第一个会话的认证令牌。要强制使用不同账户，请先清除缓存的凭据。
13. **守护进程速率限制**：如果在 15 秒的监控间隔内触发多个事件，同一窗口的 CURSOR-STOPPED 通知可能会被抑制（Hermes 会丢弃重复项）。不要依赖捕获每个通知 — 使用 `process(action='poll')` 或手动 `capture-pane` 进行确认。
14. **先注册再启动守护进程**：始终在启动守护进程之前注册窗口（通过 `monitor add`）。守护进程只监控启动时已注册的窗口。
15. **cursor-agent 的 "Exited" 误报**：守护进程可能会报告仍在运行的 cursor-agent 会话的 `state=exited`。这是因为 cursor-agent 运行在 Node.js 上（进程名 `node`），临时 shell 命令可以短暂切换 `pane_current_command`。在假设 agent 崩溃之前，请用 `capture-pane` 进行验证。
16. **多面板监控**：在监控同一窗口内的多个面板时（会议布局），使用 `--pane` 参数：`monitor add --group g session window --pane N --label "Role"`。监控脚本通过 `session:window.pane`（如 `c456-summit:0.0`）访问面板。
17. **`--auto-layout` 守护进程参数**：向 `daemon` 传递 `--auto-layout` 以根据哪些面板在工作中自动切换 tmux 布局。需要项目中有 `layout.sh`。参见 `tmux-pane-workspace` 技能了解布局脚本设置。
18. **需要 `automatic-rename off`**：没有此设置，tmux 会用运行中的命令名覆盖 cursor-agent 的面板标题。在创建每个窗口后设置 `tmux set -t window automatic-rename off`。
19. **Shell 命令 vs agent 消息**：使用 shell 命令（echo/cat/heredoc）的 `tmux send-keys` 会在 cursor-agent 后面的 shell 中执行，永远到不了 agent 的对话。始终使用四步协议且**仅使用纯文本** — 不使用 shell 语法，不使用文件重定向。参见 `references/messaging.md` → 反模式部分了解示例和恢复方法。
20. **不要信任初始面板标签**：在为多 agent 窗口设置面板级监控时，cursor-agent 在初始化后会动态覆盖手动设置的面板标题。agent 启动前你看到的标题可能与它们加载后的实际角色不同。始终通过向每个面板询问 `你是谁？请用一句话介绍你的角色职责`（通过四步协议）来验证，从回复中读取其自识别的角色，然后使用已验证的标签注册。例如：最初标记为 "PM" 的面板在 cursor-agent 初始化后实际可能是 "Trend Researcher"。
22. **先扫描所有面板**：窗口中的面板数量可能比你最初的设置脚本创建的更多（例如 10 个而不是 6 个）。注册前始终运行 `tmux list-panes -t session:window -F '#{pane_index}: #{pane_title}'` 来发现每个面板。不要假设 0..N 覆盖了所有面板。
23. **守护进程进程堆积**：每次通过 `terminal(background=true)` 启动守护进程都会创建一个新进程。旧守护进程在后台会话通过 Hermes 终止后仍作为孤儿进程持续存在。反复重启后堆积 5+ 个守护进程是常见情况。重启前：(a) 杀死所有守护进程：`pkill -f "python3 -m core.monitor daemon"` (b) 验证清理：`ps aux | grep core.monitor | grep -v grep` (c) 然后才启动新守护进程。当通过 Hermes 后台进程管理器运行时，使用 `execute_code` 为每个旧进程显式 `kill -9 PID` 比使用 shell 级 `pkill` 更可靠。
24. **脏输入缓冲区阻塞四步协议**：失败的广播后（发送 shell 命令如 `cat`/`echo` 而非 agent 消息），面板的输入缓冲区可能包含过期的 shell 文本，阻止新消息到达 agent。`→ Add a follow-up` 空闲指示器可见，但 `send-keys` 按键被过期的 shell 状态消费而非 agent 的 stdin。恢复序列：`tmux send-keys -t session:0.pane Escape`（取消自动补全），`sleep 1`，`tmux send-keys -t session:0.pane C-c`（中断过期进程），`sleep 2`，`tmux send-keys -t session:0.pane C-u`（清除行），`tmux send-keys -t session:0.pane C-k`（清除到行尾），`sleep 1`，然后用 `capture-pane` 验证。只有当 `→ Add a follow-up` 不再显示过期内容时，才应重新尝试四步协议。

25. **没有 `watch_patterns` 的守护进程 = 无 CURSOR-STOPPED 通知**：如果守护进程通过 `terminal(background=true)` 启动但没有 `watch_patterns=["CURSOR-STOPPED:"]`，状态变化的输出会进入守护进程的 stdout，Hermes 会将其捕获为普通进程输出 — 它**永远不会**转发到对话中。你可以 `process(action='poll')` 查看当前状态，但永远无法知道面板何时从 executing→stopped 转变。始终将 `background=true` 与 `watch_patterns=["CURSOR-STOPPED:"]` 搭配使用。注意：`notify_on_complete=true` 在守护进程退出时触发一次（对长时间运行的守护进程无用）；`watch_patterns` 在每行匹配时触发。它们用途不同，不能互相替代。

26. **Agent 因管道缓冲区死锁卡在等待 shell**：当 cursor-agent 的 shell 命令使用 tee 和 tail 的管道时（如 `make ci-quick 2>&1 | tee log | tail -25`），可能会无限期显示 Waiting Ns for shell（0% CPU，无进展）。操作系统管道缓冲区（4KB-64KB）阻塞 tee 写入直到 tail 读取，而 tail 不读取直到有足够输入或管道关闭，形成循环死锁。恢复方法：(a) 用 ps aux 找到卡住的 PID，(b) 杀死它，(c) agent 恢复。重试时不使用管道（仅 `make ci-quick 2>&1`）或使用 stdbuf -oL。

27. **Hermes 会话重启后守护进程丢失**：当 Hermes 会话重启（连接丢失、/new 或进程重启）时，守护进程停止。tmux 会话和 cursor-agent 持续存在，但不会触发 CURSOR-STOPPED 通知，直到守护进程重新启动。恢复方法：(a) 验证组存在：`python3 -m core.monitor list --group YOUR_GROUP`，(b) 重新启动守护进程：`terminal(background=true, watch_patterns=[CURSOR-STOPPED:])`。组状态文件（`~/.hermes/logs/cursor-monitors/`）在 Hermes 重启后持续存在。

28. **TASK_COUNT 页脚 bug 历史 — 已在 v0.4.2 修复**：参见下方的陷阱 #32 了解 2026-07-04 应用的实际 watch.py 修复。曾存在两种失败模式：(A) 添加 TASK_COUNT_RE 以修复报告不足；(B) 它导致过度报告，过期的 "N task" 永远阻止 CURSOR-STOPPED 触发。两者都通过从 `is_executing()` 中移除 TASK_COUNT 解决 — 真实的活动信号已经在前面被捕获。完整细节见 [`references/task-count-bug-20260704.md`](references/task-count-bug-20260704.md)。

29. **易混淆的 Unicode 字符触发安全扫描阻止**：通过 `tmux send-keys` 发送消息时，避免使用视觉上类似 ASCII 但代码点不同的 Unicode 字符（数学字母数字、西里尔字母仿冒、希腊字母）。Hermes 安全扫描器会将这些标记为潜在的同形字攻击并阻止命令或提示批准。仅使用纯 ASCII — 不要使用 Unicode 破折号、智能引号或数学符号。这在包含代码路径或技术术语的多行消息中尤为重要。

30. **Worker 数量不得超过 CPU 核心的 80%**：运行并行数据任务（minute-1m、rollup、board-daily）时，将 worker 数量设置为 `cores * 0.8` 以上会浪费资源。超出 CPU 容量的 worker 全部在等待 I/O（API 速率限制、磁盘）而非计算。在 32 核机器上，最大有效 worker 数 = 25。更多 worker = 更多 API 节流，而非更快完成。

31. **Hermes 会话丢失后守护进程重启**：当 Hermes 重启时（连接丢失、/new），守护进程停止但 tmux 会话和 cursor-agent 持续存在。恢复方法：(a) 验证组存在：`python3 -m core.monitor list --group GROUP`，(b) 不要重新注册面板（状态在 `~/.hermes/logs/cursor-monitors/` 中持续存在），(c) 启动守护进程：`terminal(background=true, watch_patterns=["CURSOR-STOPPED:"], command="exec python3 -m core.monitor daemon --group GROUP")`。

32. **页脚 TASK_COUNT 抑制 CURSOR-STOPPED（已于 2026-07-04 修复）**：当 agent 的状态页脚显示 "1 task" / "N tasks"（过期的后台 shell 进程）时，旧的 `is_executing()` 代码基于 `TASK_COUNT_RE` 匹配页脚行返回 True，导致守护进程永远无法触发 CURSOR-STOPPED。Agent 可能完全空闲（`→ Add a follow-up`）但守护进程永远不会通知，因为它认为执行仍在进行。

**修复（watch.py `is_executing()`）：** 从 `is_executing()` 中移除了 TASK_COUNT 检查。底部页脚的任务计数是残留指标 — 它们不代表 agent 正在活跃处理。真实的活动信号（spinner/BRAILLE、Working/ACTIVITY、background tasks/BACKGROUND_RE、monitoring/MONITORING_RE）已经在函数前面被捕获。如果这些都不匹配，页脚上方的 activity_text 是干净的，agent 就是空闲的，无论页脚中是否有过期的 "N task"。

**验证：** 修复后，显示 `→ Add a follow-up` 且页脚中有 `1 task` 的 agent 将正确报告 `state=stopped reason=idle` 而不是永远显示 `state=executing`。这使得守护进程可以为有过期后台进程的空闲 agent 触发 CURSOR-STOPPED 通知。

33. **守护进程轮询间隔调优（`CURSOR_MONITOR_INTERVAL`）**：守护进程每 N 秒检查一次面板状态，由环境变量 `CURSOR_MONITOR_INTERVAL` 控制（默认：`15`）。更改时，先杀死旧守护进程并使用新值重启：

```bash
# 默认 15s（无需环境变量）
cd ~/.hermes/skills/autonomous-ai-agents/tmux-cursor-agent
exec python3 -m core.monitor daemon --group YOUR_GROUP

# 10s — 响应更快，2026-07-04 会话中用户偏好
CURSOR_MONITOR_INTERVAL=10 exec python3 -m core.monitor daemon --group YOUR_GROUP

# 5s — 激进模式，仅在响应速度至关重要时使用
CURSOR_MONITOR_INTERVAL=5 exec python3 -m core.monitor daemon --group YOUR_GROUP
```

其他可调环境变量：`CURSOR_MONITOR_STATUS_INTERVAL`（心跳日志，默认 600s）、`CURSOR_MONITOR_LINES`（面板捕获行数，默认 15）。低于 10s 会增加 CPU 占用但收益有限 — 大多数工作流在 10s 或 15s 下即可正常工作。

**修复后早期通知的说明：** TASK_COUNT 修复（陷阱 #32）后，提交后台 shell 命令（如 `make ci-quick`）的 agent 在 shell 运行时显示空闲 — 这是**正确行为**。Agent 没有在活跃处理；它在等待。在长时间 shell 命令期间频繁的 `CURSOR-STOPPED:idle` 是预期行为，不是回归。守护进程现在准确报告 agent 活动而非将后台进程计数与 agent 状态混淆。

34. **Follow-ups 队列识别特征（`enter steer` vs 文档 `enter send now`）**：follow-ups 框的**唯一可靠特征**是框头 `┌─ follow-ups ───┐` 与末行 `+N more lines · enter steer`（旧版本显示 `enter send now`）。不要在捕获中只搜 `enter send now` — 新版本不会匹配，消息会静默堆积。**每次发送后必须检查**：若捕获中出现 follow-ups 框，说明消息未投递，需要立即在空输入行按 Enter 提升（每条消息一次 Enter，重复按到框消失）。排查顺序：`capture-pane -S -40` → grep `follow-ups|enter steer|enter send now` → 有框则 Enter 提升 → 再 capture 确认消息已在对话历史中（框外）→ 才声明发送成功。

## 文档

仓库 `tmux-cursor-agent/docs/` 中的完整文档：

```
01-quickstart.md         快速入门指南
02-session-lifecycle.md  创建/验证/销毁会话
03-state-detection.md    EXECUTING/STOPPED 检测原理
04-messaging-protocol.md 四步协议详解
05-monitoring-daemon.md  守护进程配置
06-pitfalls.md           完整陷阱目录
```

### 技能参考文档

| 文件 | 内容 |
|------|------|
| [`references/calibration.md`](references/calibration.md) | Fixture 测试框架及如何添加/修改状态检测测试 |
| [`references/state-detection.md`](references/state-detection.md) | 状态检测模式与边缘情况 |
| [`references/messaging.md`](references/messaging.md) | 消息协议深入解析 |
| [`references/messaging-pitfalls.md`](references/messaging-pitfalls.md) | 完整的消息传递陷阱（状态、输入、队列） |
| [`references/daemon-poll-behavior.md`](references/daemon-poll-behavior.md) | 守护进程轮询行为与过早空闲检测 |
| [`references/task-count-bug-20260704.md`](references/task-count-bug-20260704.md) | TASK_COUNT 页脚 bug（修复、复现、验证） |
| [`references/publishing-pattern.md`](references/publishing-pattern.md) | 如何在 c456-com/skills 仓库中添加/重命名/移除技能 |
| [`references/daemon-poll-interval.md`](references/daemon-poll-interval.md) | 守护进程轮询间隔配置（CURSOR_MONITOR_INTERVAL 环境变量） |
| [`scripts/team_tasks.py`](scripts/team_tasks.py) | 持久化团队任务台账 — 创建/更新/列表/完成任务 |
END
__tr_native_ec=$?; pwd -P >| '/var/folders/kr/_pxypyrx0xvcqfqdwy1h83q80000gn/T/trae-agent-toolhost-501/jobs/job-38144be5058a452cbdbff7359c12a8ef/cwd.txt'; exit "$__tr_native_ec"
