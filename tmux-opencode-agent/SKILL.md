---
name: tmux-opencode-agent
description: "OpenCode Agent over tmux：当用户要把活派给 tmux 中的 OpenCode、判断它哪一轮说完（SSE 终态）、处置 Permission required 权限面板与 AskUserQuestion 提问面板、切换会话 tab、取消执行（Esc 两次）或挂监控探针时触发；用于可见 TUI 编排与可靠终态判定。"
version: 1.0.0
author: Hermes Agent
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

## 0.5 ⛔⛔⛔ TUI tab 模型：**同一工作目录的 opencode 合并成一个 TUI，用 tab 并排**（2026-09-26 操作者当面教）

> 操作者原话：「opencode 是 TUI 不是命令行，同一个工作目录你启动的所有 opencode 都会被合并
> 一起用 tab 显示、切换。因为现在 oc-review 和 oc-final 都在同一个 tab 所以你无法派活。」

**我此前一直用「进程」模型理解，这是错的**（而且今晚因此反复派错活）。事实：

```
同一工作目录启动的所有 opencode  ⇒  合并进同一个 TUI  ⇒  顶部一行 tab 栏并排
┌ issue-XXX ──────────────────────────────────────────────────────┐
│ [PR 318][执行 T3 failure][执行并汇报][⠙ PR 326 独立终审][+] │  ← 这一行就是 tab 栏
└─────────────────────────────────────────────────────────────────┘
```

### 三个必须记住的推论

1. **一个 tmux 窗 ≠ 一个会话。** 多个 tmux 窗可以连**同一个 TUI**、看**同一个 tab**。
   实测：两窗顶栏**像素级一致**、同一段 diff、同一个 `269.6K (26%)` ⇒ 同一 tab。
   ⛔ **进程数/pane 数不能当「几份独立上下文」的判据**（我在 09:0x 用它否掉了操作者的判断）。
2. **向「不认识的窗」send-keys 未必派到了你以为的地方**——消息会落进**该窗当前激活的那个 tab**。
   实测：我想往 oc-review 派第二单，结果它进了 oc-final 正在跑的 tab ⇒ **那单根本没派出去**，
   而我当时报告成「已派出、在排队」。**这是最危险的一类错：看上去一切正常。**
3. **判「某窗空闲」之前必须先切 tab**：该窗显示的 tab 可能正在跑，而你要派的活应该在**另一个空闲 tab**。

### 键位真源（从 OpenCode 二进制 keybind 表读出，**不要背错、换版要重读**）

```bash
strings -n 4 ~/.opencode/bin/opencode | grep -oE 'session_tab_[a-z_]+:e\("[^"]+"[^)]*\)'
```

| 动作 | 键 |
|------|-----|
| 切下一 tab | `ctrl+tab` 或 `alt+down` |
| 切上一 tab | `ctrl+shift+tab` 或 `alt+up` |
| 直选第 N 个 tab | `ctrl+1` … `ctrl+9` |
| 跳到有未读的 tab | `alt+shift+down` / `alt+shift+up` |
| 会话 / 项目列表 | `ctrl+o` |
| 重开刚关的 tab | `ctrl+shift+t` |
| 关当前 tab | `<leader>w` |
| **取消当前执行（掐轮）** | **`Esc`（按两次：第一次屏底出现 `esc again to interrupt`，第二次才真打断）** |

⛔⛔ **取消执行只有 `Esc`**（2026-09-28 操作者当面定）：**不是 `Ctrl+C`，不是 `/exit`，也不是退出 TUI**。
根因：**opencode v2 的执行在后台服务端跑，TUI 只是视图** —— `C-c` / 关窗口 **不会取消后台轮次**，它会继续跑（甚至跑完才让你发现）。推论（停活 + 清场必读）：

- **要停一轮**：`Esc` → 核屏底出现 `esc again to interrupt` → 再 `Esc`。**只认屏底提示，不要数次数**（实测：第一次 Esc 后会提示再按一次，不是一次就停）。
- **杀窗口 ≠ 停止执行**：`tmux kill-session` 之后**必须**核服务端 `GET /api/session/active`，看该 session id 是否仍在返回里。
  - 仍在 ⇒ 后台还在跑（没被打断），按上面节拍补 `Esc`，或按需另处置；**不许**把「窗口没了」当「它停了」。
  - 已不在 ⇒ 才是真停。
- **别用 `C-c` 掐轮**：那只会把 TUI 退到 shell（实测我按 `C-c`×2 后回到 shell 提示符，轮次是先前那两次 `Esc` 打断的）。

### 派活前的硬闸（缺这一步就等于没派）

```bash
# ① 读顶栏，确认有几个 tab、当前是哪个（转圈 ⠙/⠧ = 该 tab 在跑）
tmux capture-pane -p -t <win> -S -60 | sed 's/\x1b\[[0-9;]*m/ /g' | head -3
# ② 目标 tab 在跑？⇒ 切到另一个空闲 tab（alt+down / ctrl+N）
tmux send-keys -t <win> M-Down
# ③ 切完用**内容指纹**确认真的换了 tab（不要只看标题）：
#    上下文用量  269.6K (26%) → 372.9K (36%)  ⇒ 换成功
tmux capture-pane -p -t <win> -S -3 | grep -oE '[0-9]+\.[0-9]+K \([0-9]+%\)'
```

⛔ **切 tab 会影响两个窗**（它们看同一个 TUI）——切完**两个窗都要重新核**。
⚠️ 别用「两个 pane 进程不同」推「上下文不同」；也别用「内容看起来一样」推「同一 tab」——**用上下文用量指纹最硬**。

### ⛔⛔ 归属硬闸：不是我的小弟，一个键都不许发

「我能控制这个窗」是**归属**问题，不是**技术可行性**问题。
⇒ 对**不是自己派的那个会话/窗口/tab**：`send-keys` 禁发（连 `alt+down` 这种「只是切个视图、
不改变任何东西」的也禁）、`kill` 禁发、切 tab 禁切、close 禁关。**一律只读观察。**
即使确认它「闲着」「看起来不忙」「切一下就还原」——闲着的别人的窗也不是我的操作空间。

**判归属靠服务端清单，不靠猜**（见下方脚本）：把该工作树上所有 active 会话列出，
`title` 与我派的任务名对得上的才是我的；**其余全部排除**，包括标题看着像在扫同一仓的。

```python
active = set(get("/api/session/active").get("data", {}).keys())
for s in get("/api/session").get("data", []):
    d = (s.get("location") or {}).get("directory") or ""
    if d != MY_WORKTREE: continue
    print(("MINE " if s["id"] in MY_SESSION_IDS else "FOREIGN"), s["id"], s.get("title"))
```

发现不是我的会话时**照实报出来**，同时**把核对方法一并给出**（列 id / title / 目录），
让操作者自己一眼能判；⛔ 不接管、不 kill、不切、不代做决定。

### ⛔ 要自己一张干净 tab：新开窗（同目录），而不是去切别人的

同目录再启一个 `opencode`，它会作为**新 tab 并进那个 TUI**（实测顶栏末尾多出 `+ New session`），
**全程不碰任何现有 tab / 窗口**——这是拿自己工位的正确方式。

```bash
tmux new-session -d -s <新窗名> -n agent -c <本单工作目录>
tmux send-keys -t <新窗名> "opencode"; sleep 2; tmux send-keys -t <新窗名> Enter; sleep 15
```

⛔ **派活前必核模型**：新实例用 TUI 当时的默认模型，**可能不是本单要求的那个**。
看屏底 `Build · <模型名>`（或 `shift+tab agents` 面板）对上再发指令，**不对上先换模型**。
⇒ 「工位对了」不等于「配置对了」，两者都要核。
⛔ **TUI 启动没有 `-m`（实测）**：`opencode --help` 里模型参数**只属 `run` 子命令** ⇒ **「开之前把模型选好」做不到**，只能起完会话核屏、在 TUI 内换（`/models`，或 `shift+tab` agents 面板）。
⇒ 所以「起会话」与「发指令」之间**必须**插一步核屏；想省这一步就会带着错模型跑完一整轮，白烧一轮产出。

### ⛔ `/models` 选择器三个实测坑（2026-09-26）

1. **搜索框跨次保留文本**：第一次输入 `space-bunny-free` 关掉面板后，再开 `/models` 时面板里仍是上次的词，
   新输入会**粘在后面**（实测得到 `space-bunny-free/models` ⇒ `No results found`）。
   ⇒ **重开选择器后先清空搜索框**（连按 `BSpace` 约 30 次），确认框空再输过滤词（用**短词**如 `bunny`）。
2. **高亮只认底色**：多行同名模型（`Space Bunny Free (Favorite)·OpenCode Go` / `Space Bunny Alpha·OpenRouter` /
   `Space Bunny Free·OpenCode Zen`）文本上分不出选中的是哪条——用 `capture-pane -p -e` 读 `bg`（选中行为
   `48;2;250;178;131`）**确认高亮落在要的那条再按 Enter**。三家里只有 `…·OpenCode Go` 那条是 0 成本线（屏底会显示 `$0.00`）。
3. ⛔ **面板关掉不等于输入框干净**：核一次输入框（占位符 `Ask anything…` 出现 = 空），别把过滤词当指令发出去。

### ⛔ 首条指令被当 shell 命令执行（实测，我会误读成「小弟乱来」）

现象：发出去的正文在屏上被渲染成 `$ <我的正文>` + `zsh:1: command not found: …` + `Command exited with code 127`。
⇒ **那是 TUI 处于 shell（bash）模式**，不是小弟跑偏。
**处置**：按 `Escape` 退出 shell 模式（**可能要按两次**，且**不能靠数次数，要靠屏底提示核**），确认输入框干净后重发同一条；发完**核渲染块不带 `$` 前缀**再走开。
（实测：同一句话在退出 shell 模式后重发即正常进入 agent 轮次。）

⛔⛔⛔ **判模式只看「屏最后一行非空行」，且要核两次**（2026-09-27 二次实测，两次把指令跑成 shell 命令后总结）：

⚠️ **2026-09-29 补充：上一条「最后一行非空」不够——会取错行。** 实测同屏有两处提示，位置会变：
- shell 模式时，**输入框内的模式行会渲染成 `Shell`**，且屏底出现 `… <path> <branch>   esc exit shell mode`；
- 普通模式那两处分别是 `Build · <model> …` 与 `… <path> <branch>  <用量> · $<费用>  ctrl+p commands`。
⇒ **可靠判据 = 一眼看输入框的「模式行」是 `Shell` 还是 `Build …`**（截图/`-e` 抓取时看那行原文），别只按行号或"最后一行"猜。
⇒ 处置：`Escape` 退出（文本**还在输入框里**，退完**直接 Enter 即可**，不用重打）；提交后**必须验证真进了轮次**——判据是 **token 用量数字变大**（如 229.1K → 230.8K）+ 出现轮次耗时行（`Build · … · 5.9s · 38.8 tok/s`）。
⚠️ 我今晚为此连发 4 条被当命令跑掉（症状：屏上 `zsh:1: parse error near ')'` / `Command exited with code 1`，token 数一动不动）——**每次发指令前都核模式行，发完都核 token 增量**。

### 🔴 真根因（2026-09-29 二次实测，3 条消息被吞后定位）

**消息正文里的 `!` 会被 TUI 当「shell 模式开关」**：整段文本用 `send-keys -l` 打进去，敲到 `!` 那一刻模式就翻成 `Shell`（实测 `… → 对，按仓规就地开评审（审 PR !447 …）`：`!` 一到，模式行立刻从 `Build` 变 `Shell`），于是**这条消息永远进不了模型**——Enter 是被 shell 消费的。
- ⛔ **正文禁用 `!` 与行首 `#`**（`#` 会被渲染成 `$ <正文>` 当 shell 命令）。要指代 PR / issue 就写「PR 编号 123」「issue 编号 456」，别用 `!123` / `#456`。
- ⇒ **模式会在两次发送之间自己变**（小弟自己跑过 shell 命令就会留在 shell 模式）⇒ **每次发之前都重新核模式行**，不能拿上一次的结果当准。
- ⇒ **「Escape 退完直接 Enter」不足以救**：文本里含 `!` 时，退模式后 Enter 仍可能被当命令吞掉（实测 box 清空、token 不动）。处置顺序应是：`Escape`（退模式）→ `C-u`（清空输入框）→ **改掉正文里的 `!`/`#` 后重打** → 核模式行是 `Build` → Enter → 核 token 增量。
- ⇒ **token 数不动 = 没送达**（不是「已排队」）：必须重写重发，别假设小弟收到了。
- ⛔ **发送侧硬自检（我自己的正文）：正文里绝对不许出现 `!`** —— 包括要教给小弟的命令里的 `'!gh auth …'`。
  一个 `!` 就把整条消息变成 shell 模式，Enter 后被执行：屏上出现 `zsh:1: command not found: <你正文开头>` + `Command exited with code 127`，
  **消息根本没送到 agent**。要给的命令改写成文字描述（「用 gh 的 git 凭据助手」），或把 `!` 拆开说明。
  发送前一律 `assert '!' not in MSG`。
- ✅ **权威判法（比 token 计数可靠）**：直接读服务端会话消息，搜你这条的特征串——
  `curl -s -u opencode:<pw> "http://127.0.0.1:49374/api/session/<sid>/message" | grep -c '<特征串>'`
  （返回的是 `{id,time,type,agent,model,content[],tokens…}` 数组，**不是** `{info,parts}` 形状，别按后者解析）。
  实测：轮次**刚起**时 token 计数还没刷新 ⇒ **token 不动是假阴性**，别据此重发（重发会造成重复指令）。
  ⇒ 顺序：核模式行（Build）→ Enter → 若 token 未变，**用上面这条查一次消息**再决定是否重发。

```bash
# ✅ 主判据：抓输入框那几行，看「模式行」整行文本
tmux capture-pane -p -t <sess> | sed 's/\x1b\[[0-9;]*m//g' | grep -E '^\s*┃\s+(Shell|Build)' | tail -1
#   含 "Shell"                  ⇒ 还在 shell 模式（按 Escape 退出；文本还在框里，退完直接 Enter）
#   含 "Build · <模型> …"      ⇒ 普通模式，可以发
#   辅判据（次要）：屏底出现 "esc exit shell mode" 只作佐证
```
⛔ **别用「最后一行非空行」取**（旧版写法，已废）：同屏有多行提示且**顺序会变**，
实测因此取错行、把 shell 模式误判成普通模式（一轮白发）。

- ⛔ **不要用「整屏 grep -c 'esc exit shell mode'」判**：滚动历史里会留着上一次失败的 footer，计数 >0 是**假阳性**（实测因此误判、又把复审正文当命令跑了）。
- ⛔ **两个时点都要核**：① 发字前；② **送字之后入 Enter 之前**——实测模式会在输入时翻转。
- 实测：shell 命令 `exit 127` 后 TUI **自己回到普通模式**（footer 变回 `ctrl+p commands`），所以不一定需要连按 Escape；**只认 footer，不要数 Escape 次数**。
- 再次实测：被跑成命令后，文本**已从输入框消失**（被 shell 吃掉），必须**重发**，不能直接 Enter。
- 实测：第一次 `Escape` 后**仍是 shell 模式**（我误以为已退出，重发的正文差点又被跑成命令）；
  再按一次才退。**“按一次就行”是错的——只认屏底提示。**
- ⛔ **两个都带 `$` 的块要分清**：`capture-pane -S -8` 里历史块（已跑成命令的证据）与输入框**都会出现 `$`**；
  输入框是**最底部那个 `┃` 框、紧贴模型栏上方**。判“文本到底进没进输入框”要看那个位置，不看全文 grep 计数。
- 实测的首条被跑掉后，文本其实**还在输入框里**（单元格里就是我的正文，无 `$`）——退出 shell 模式后**直接 `Enter` 提交即可**，不必重打。

⚠️ **会复发（实测同会话第二次）**：不只在首条——同会话里后来的消息也会再次被当 shell 命令执行（实测：一轮交工后的「复审请求」那条又中）。
⇒ **每次发指令都要核**，且要分清两个长得像 `┃` 的块：**输入框**（屏最底部、紧贴模型栏上方）带不带 `$`；
**历史块**（已经发出去的）也可能带 `$`（那就是已被跑成命令的证据），别把它当成输入框状态。
⛔ 别把它归因成「模型乱执行」、也别归因成「小弟跑偏」。

## 1. 起会话（可见 TUI）

⛔ **开之前先确认「今天用哪个执行者」**：默认分工会被操作者当天口径覆盖（实测：「今天我们用 cursor 小弟开发代码」）。
⛔ **别照默认直接开 opencode 会话**——开错执行者 = 白开 + `tmux kill-session` 清场 + 重开，
还得额外核一次清场结果（工作树没被它动过）。判据：**当天口径 > 任何默认分工**；拿不准就问一句，比开错便宜。

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

## 1.2 ⛔ 单会话制（操作者 2026-09-29 定）：只开一个 tmux 会话供他观察调度

操作者原话：「为了方便我观察执行过程，你只需开一个 tmux session，一个 issue 结束了，你只需退出 opencode 即可，
这样我可以持续在 tmux 窗口内观察你的调度状态。」

⇒ 硬规矩：

1. **全程只保一个会话**，起个稳定通用名（现行 `oc`）——⛔ 不要一单一个窗口
   （旧做法 `oc-361`/`oc-442`/`oc-417` 各开一个 = 操作者要切好几个窗才能看全，已废）。
2. **一单结束 ⇒ 退 opencode 回 shell，不关会话**：他就在那个 shell 里持续看到我 `cd` 下一棵树、起下一单、删现场。
   ⛔ 不许 `tmux kill-session` 收尾（那是把观察面也收掉了）。
3. **同一会话换单**：`/exit`（或 `C-c`）退 TUI → `cd <新工作树>` → 再 `opencode`。
   ⚠️ `cd` 一定要在起 opencode **之前**做，TUI 的 cwd = 起它那一刻的 cwd。
4. **换单/改名后探针必须重挂**：`--tmux-session <名字>` 变了，屏副路（`SCREEN-QUESTION` 主判据）会失效。
   顺序：`kill` 旧探针 → `ps -p` 核已停（⛔ 一个 target 只许一个探针）→ 用新会话名重挂 → 核 `ANCHOR-OK`。
5. **registry.tsv 跟着单行化**：只登记当前这一单（+ 非我派的只读观察项）。
   ⛔ **换单必须同时把行里的 opencode 会话 id（锚点）改掉**，不能只删旧行/只改备注：
   守夜兜底是按 registry 里的 sid 巡检的，锚点不改 ⇒ 它会按**旧 sid** 反复 `nohup` 补挂探针
   ⇒ 同一个 tmux 窗上出现盯旧锚点的孤儿探针（假信号与重复通知的来源）。
   顺序：改行 → `ps -eo pid,command | grep '[w]atch.py' | grep <旧sid>` 应 **0** 命中 → 再挂新探针。
6. ⛔ **被 park 的单（等操作者决策）不要占窗口**：它的状态在 issue / PR / 看板里，空窗口只会让他看花眼。
   放行时再在同一会话里 `cd` 回去起 opencode，用原简报接着干。
7. ⛔ **换单时目标工作树已存在 ⇒ 先判它是不是「遗留空树」，别急着新建或当别人的成果**。
   三条同时成立就是遗留（可复用）：`git status --short` 干净、
   `git rev-list --count <branch> ^origin/main` 为 0（分支 tip 是 main 祖先）、
   `git ls-remote --heads origin <branch>` 无输出（没推过远端）。
   复用前先 `git fetch` + `git merge --ff-only origin/main` 把它推到当前 main 再派活
   （旧树端口/库配置仍在，省一次建树 + `bun install`）。
   三条任一不成立（有自身提交 / 已推远端）⇒ 当**别人或旧尝试的在飞成果**处理：⛔ 不覆盖、不重置，先只读核实并报出来。

## 1.5 会话身份验真（挂探针前的硬闸，⛔ 不可跳过）

`session_id` 是探针唯一的过滤条件。**服务端不认识的 id，探针会安静地永不命中**——
它不报错、不退出，而 `ps` 照样显示它活着 ⇒ 我把「探针在跑」读成「在监」，空转数小时零告警。
⇒ **锚点只能取自服务端清单，不能取自我自己上次的记录。**

⛔ **挂探针前两步验真**（完整诊断与目录交叉核见 `references/session-identity.md`）：

```bash
curl -s -u "opencode:$PW" "$URL/api/session"        | grep -c "<session_id>"   # 0 = 锚点作废
curl -s -u "opencode:$PW" "$URL/api/session/active" | grep -c "<session_id>"   # 预期在跑却不在 = 跑的不是它
```

### ⛔ 进程活 / 任务在跑 / 探针在监，三者互不顶替

| 信号 | 只证明 |
|------|-------|
| `ps` 有探针进程 | 脚本活着（**可能在盯一个空 id**） |
| 屏底 `esc interrupt` | **某个** opencode 忙着，**不是**「我的任务在跑」 |
| 探针报了终态/面板 | 那条 id 上真有事件流过来 |

⇒ **「我的任务在跑」的唯一判据是「我那条指令里的标记串出现在该 pane 历史里」**：
派活时在指令里塞一个独特标记，事后 `tmux capture-pane -p -S -3000 | grep -c '<标记>'`。
`grep -oE '<brief 文件名>'` 逐窗计数是同一件事的轻量版（每个 pane 应恰好命中自己那份）。
⚠️ 屏内容雷同**最常见的真因是「我把同一份指令发给了两个窗」**——先核这个，别急着归因成界面共用。

### ⛔ 同工作目录开多个 opencode：pane_pid 只证明进程独立，不证明会话独立

对方可能报「同目录多个实例会并进同一个界面的多 tab」。**先分开两个问题：几个进程？几个会话？**
两者都会影响归因，而**只有第二个决定「屏上这屏是谁的」**。

```bash
tmux display-message -p -t <sess>:0 '#{pane_pid}'    # 几个 pane_pid 不同 = 几个独立进程
curl -s -u "opencode:$PW" "$URL/api/session/active" | grep -c 'ses_'   # 几个 active 会话
```

- `pane_pid` **互不相同** ⇒ 各自独立的 opencode **进程**。⛔ **但这不等于独立会话**——
  多个 TUI 前端可以连同一个服务端会话（实测：两个 pane 进程不同，服务端只有 1 个 active 会话，
  两窗屏内容一致且都在跑同一件活）。
- `pane_pid` **相同** ⇒ 连进程都是同一个，屏上任何东西都不能归因到单个任务。
- ⇒ **判「这几窗是一份还是几份」只比 active 会话数**，不靠 pane 数、也不靠进程数。
  屏内容雷同时**先怀疑共享会话**，再回查指令是否发重了（见 §1.5 上面的标记串判据）。

## 1.6 ⛔ 派「会改文件」的活之前：先数这棵树上还有谁在动

只读活（评审 / 巡检 / 截图取证）撞上别人无所谓；**写代码的活撞上别人 = 两边同时改一棵树**，
表现为随机冲突、脏工作树、归因不清——比看不见的撞车更难查。
⇒ 派活前先列出**所有**落在该工作树上的 active 会话，**包括不是我派的**：

```python
for s in get("/api/session").get("data", []):
    d = (s.get("location") or {}).get("directory") or ""
    if d == "<本单工作树>" and s["id"] in active:
        print(s["id"], "|", s.get("title"))
```

| 屏上 / 清单里 | 结论 | 动作 |
|---|---|---|
| 只有我这一单 | 安全 | 正常发 |
| 有**我派但还没交工**的单在跑 | 排队即可 | 新单子会进 follow-ups 队列、等前一轮结束——**这是正确状态，不要打断** |
| 有**不是我派的**会话在跑 | ⛔ **停** | **报出来问操作者那是谁**再决定 |

⛔ 第三档最容易漏：那些会话的标题一眼就能看出不是自己派的任务，但**它就在同一棵树上、一样会改文件**。
既不接管、也不 kill、也不当没看见——**报出来问**，因为我不知道它要什么，擅自处置可能毁掉别人的在飞产出。
（派活前把工作树 `git status --short` 清空作为基线，见 `delegated-work-verification`。）

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

## 2.5 ⛔⛔ 挂探针前必须先验锚点：抄来的 id 会让你盯 8 小时空气（2026-09-26 实测）

**实测**：我给三个探针喂了「从记录里抄的 / 根本不存在」的 `session_id`。
探针照样打印 `PROBE-START`、进程一直活，我用 `ps` 反复确认「在盯」——
实际它在旁听一个**空 ID**，一盯 5~8 小时。**`ps` 只能证明进程活，证明不了锚点对。**

```bash
# ⛔ 挂之前先核 id 真实存在（真源 = 服务端，不是我的笔记）
curl -s -u "opencode:$PW" "$URL/api/session" | python3 -c "
import sys,json
for s in json.load(sys.stdin)['data']:
    d=(s.get('location') or {}).get('directory') or ''
    if 'my-worktree' in d: print(s['id'], '|', s['title'][:30], '|', d[-30:])
"
```

⇒ **`scripts/watch.py` 已内置启动闸**（2026-09-26 新增，三路回归已过）：

| 输入 | 输出 | 意义 |
|------|------|------|
| id 不存在 | `ANCHOR-FAIL` + 退出 | 抟上错 id，**宁可不盯不可盯错** |
| `--expect-dir` 与实际不符 | `ANCHOR-FAIL` + 退出 | 防同项目多 worktree 串台 |
| 两者都对 | `ANCHOR-OK` + 继续 | 附带打印真目录 |

```bash
# 现行用法：必带 --expect-dir
python3 scripts/watch.py <real_session_id> 86400 \
  --tmux-session <sess> --expect-dir <绝对工作目录>
```

### ⛔ 三个必须用对字段/口径的地方（我今晚全踩了一遍）

1. **目录字段是 `location.directory`，不是 `directory`。**
   我读顶层 `directory` 拿到全空，得出「这些会话不属于本项目」的**错结论**，
   差点把「探针盯错」误报成「整个环境不对」。⇒ 核目录一律 `s['location']['directory']`。
2. **「派了活」与「跑的是我派的活」是两件事。**
   屏上有 `esc interrupt` 只证明**某个** opencode 在跑。⇒ 判「在跑我的活」必须核：
   会话 `title` 是我派的任务名 **且** `location.directory` 是我指的工作目录。
   今晚我就是拿「进程活」冒充了「任务在跑」。
3. **多个 TUI 进程可以共享同一个服务端会话（2026-09-26 实测，操作者当面纠正）。**
   操作者原话：「同工作目录启动多个 opencode 他们会在一个窗口里面的多 tab 下面，
   所以你开到两个 tmux 窗口其实是一个界面。」
   实测：两个 tmux 窗各有**独立 opencode 进程**（pane_pid 33642 / 96448），
   但服务端 `/api/session/active` **只有一个**目标会话在跑
   ⇒ **进程数 ≠ 1 不代表「多份独立上下文」**。多个 TUI 前端可以连同一个会话。
   ⚠️ 我当时用「进程数不是 1」否掉了操作者的判断，**这是错的**：
   屏上两个窗内容一致不是因为「我发错了指令」，而是**它们本来就在看同一个会话**。
   ⇒ 推论：**看到多个窗内容雷同时，先怀疑共享会话，而不是先怀疑自己发错。**
   ⇒ 判「这几窗是一份还是几份」的唯一可靠办法：比 `/api/session/active` 里的会话数，
   **不要靠 pane 数量、也不要靠进程数**。

### ⛔ `BACKFILL-DONE` 重放旧终态会盖住真信号（2026-09-26 实测，已修）

**实测**：探针锚在一个**8 小时前已收工**的 session 上，每 3600s 重连就把**同一条**
`BACKFILL-DONE` 重放一次——实测日志里连转 6 次同一个 `end_ts`。
真信号被噪音盖住，我据此误以为「在盯」，实际盯的是旧终态。
⇒ **`BACKFILL-DONE` 连续出现多次不是「有新进展」，是同一个旧终态在重放。**
⇒ 已修：`scripts/watch.py` 跨重连记忆 `message_id`（`REPORTED_BACKFILL`），**只报一次**，之后静默。
回归：锚在已收工 session 上跑 3 轮重连 ⇒ `BACKFILL-DONE` 出现 **1** 次（修复前 = 3）。

**⚠️ 去重只针回看终态，不碰真信号**：正在 `active` 的 session 仍每轮正常打
`BACKFILL-UNAVAILABLE session 当前仍 active`，SSE 终态事件也不受影响（已回归）。

**⛔ 附带一条判据**：`BACKFILL-DONE` 报完若屏上又有 `esc interrupt`，
那是**新一轮开始**（正常的下一单），不是「旧终态又来了」；
此时应核屏底是不是 `esc interrupt`，是就继续等，**不是**当重复噪音。

## 3. 轮次结束判据（三个终态，任一即结束）

| 事件 | 含义 |
|------|------|
| `session.execution.succeeded` | 正常完成 |
| `session.execution.interrupted` | 被打断（发新消息会顶掉待批准请求） |
| `session.step.failed` / `session.tool.failed` | ⚠️ **不是轮次结束**（见下） |

**判据是「本 session 出现过 `session.execution.succeeded` 或 `session.execution.interrupted`」，
不是只看 `succeeded`**——只等 succeeded 会漏被打断的轮次。

⛔⛔ **`session.tool.failed` / `session.step.failed` 不得当轮次结束**（2026-09-25 实测误报）：
它们只表示「**某一次**工具调用 / 某一个 step 失败」，长任务里出现一次完全正常，
agent 会换路继续（实测：Read 读二进制失败 → 它改用 shell 提纯 → 继续读，仍然在跑）。
**真误报现场**：`watch.py` 命中 `session.tool.failed` 就打印 `STAGE-DONE` 并退出，
而那一轮实际还在跑（上下文 92.3K / 9%，仍在读日志）⇒ 编排方拿到「结束」假信号就退监控，
下一次请示门/权限面板就没人盯了。⇒ `scripts/watch.py` 的 `TERMINAL_EVENTS` 只含两个
`execution.*` 事件；failed 类事件若要报，只能作**提示**（`TOOL-FAILED`），不得触发退出。

⛔ **`session.execution.succeeded` ≠ 工具成功**：实测跑不存在的命令（exit 127）**照样发 succeeded**，
它只表示「这一轮执行完成」。`session.tool.success` 同理只表示「调用完成」，不代表业务成功。

⛔⛔ **主轮 `succeeded` ≠ 整轮交工（实测两次假终态，必须当硬闸）**：agent 派了子代理时，
主轮的 `session.execution.succeeded` 只表示「主 agent 那一段执行完成」，
**它派出的子会话可能还在跑**。两次实测：一次 SSE 报主 session `STAGE-DONE`，
屏上同时是「评审仍在进行：…尚未完成」+ `↓ 2 subagents · 1 shell`；另一次重挂探针时
`backfill` 读到的就是上一段的 `idle/succeeded`，**启动瞬间就自退**，而子代理仍在跑。
⇒ **判主轮真结束必须额外核「`parentID == 本 session` 的子会话全部不再 active」**：
```python
active = api_get(url, "/api/session/active").get("data")
# ⚠️ 真源形状实测：data 可以是 {sessionID: {"type": ...}} 字典，也可以是 session 对象数组；
#    按 list 处理会静默取不到 id（实测我第一版就写错了，检查静默失效、没拦住）
ids = list(active.keys()) if isinstance(active, dict) else [s.get("id") for s in active if isinstance(s, dict)]
children = [(sid, api_get(url, f"/api/session/{sid}").get("data", {}).get("parentID") == SESSION_ID) for sid in ids if sid != SESSION_ID]
```
`scripts/watch.py` 已内置（`child_sessions_still_active()`）：有 active 子会话时打印
`TERMINAL-PENDING` 并**继续盯**，不判结束；核不出结果时打印 `TERMINAL-UNVERIFIED` 同样不判结束。
**另：屏上 agent 自己的「仍在进行 / Need wait background notification」也是未完成信号**，以它为准。
**⛔ 改完探针必须用真场景回归**：拿一个确实有 active 子会话的 session 跑一次，
断言输出是 `BACKFILL-UNAVAILABLE … 子会话 active` 而**不是** `BACKFILL-DONE`。
⛔ **`session export` 的 `info.outcome` 不能当判据**：实测**运行中它就已是 `succeeded`**（那是上一轮的结果），
用它判本轮会 100% 误判。

⛔ **`session.execution.failed` 不等于「这轮白干」（2026-09-28 实测，两个会话各中一次）**：
它只表示「这一轮以错误收场」，最常见根因是 **provider 侧 LLM 调用失败**（现场原文
`Error: Upstream request failed: Invalid credential`），而**工作往往早已落盘**。
⇒ 收到 `failed` 先核事实再判，别当失败处置：
① `git log --oneline` / `git status --porcelain`（本地提交在不在、是否仍 staged）；
② `git ls-remote --heads origin <branch>`（推没推上去，编码的是 agent 自报不符）；
③ 产物文件（报告 / 门禁日志）是否已写、`wc -l` 是否到预期节。
三样都证明「该做的做了、只是收尾对话被掐」⇒ 发一条「接着做、别重来」的消息让它续跑。
⛔ **别因为一句 `Invalid credential` 就切账号**：先用 v2 自带命令核**生效**账号
（`opencode auth list` 列账号；生效项读 sqlite `opencode.db` 的 `credential.active`）。
实测常见形态是「生效账号可用，表里另有一条**未生效**的旧 `API key` 条目是 `invalid`」——
**不切**，只报。
⛔ **账号切换 / 额度监控一律用 opencode v2 自带能力，不要自建工具、台账或 cron**（操作者已明确否掉自建维护件）。
凭据真源、鉴权头口径、额度判定、隔离复现法见 `references/opencode-v2-credentials.md`。

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
   ⛔ **判「已经打断了」不能只 grep `esc interrupt`**：第一阶段文案是 `esc again to interrupt`，
   它**不含** `esc interrupt` 子串（count=0）⇒ 单查这一条会把「押了一次、还没真打断」读成「已停」。
   两个文案都要查（`grep -E "esc interrupt|esc again to interrupt"`，得 0 才是真停）。
   没停也不会丢消息（新消息进 follow-up 队列等待），**但不得在汇报里写成「我已掐掉当前轮」**。

### 忙碌时 title 会变（修正「恒为 OpenCode」）

空闲态恒为 `OpenCode`，但**忙碌时会变成 `OC | <任务名>`**（实测 `OC | Running repeated OC- output…`）。
⇒ 短窗口采样时它**可用作辅助佐证**；但结束态会回到 `OpenCode`，
所以**不能只靠 title 判结束**，仍以 SSE 终态事件为准。

### 消费后的队列消息不会在屏上重复

实测：忙碌时发的 `OCQ2-MARKER` 转后台后被消费执行，屏上出现它的 Thought 块，
但**原始输入行只出现 1 次**（不重复渲染）——
⇒ 别用「屏上几次」数队列，用 `session.inbox.enqueued` / `delivered` 事件数。

## 3.5 ⛔ 探针不在的窗口期：权限阻塞处置后重挂，**必须先核终态**

**今天实测踩到的真坑（2026-09-25 20:24）**：探针报 `PERMISSION-BLOCKED` **就退出**（设计如此，让 CTO 去处置面板）
⇒ 处置期间若那一轮被**打断**（`interrupted`，比如 CTO 批权限时误按 Enter 落进输入框），
**没有任何探针在看** ⇒ 小弟停在屏上十几分钟，CTO 完全不知情。

**⛔ 硬闸：重挂探针 ≠ 挂上就完事。** 处置完权限面板重挂探针后，**先核一次屏底终态**：

```bash
tmux capture-pane -p -t <sess>:0 -S -20 | sed 's/\x1b\[[0-9;]*m/ /g' | tr -s ' ' \
  | grep -E "interrupted|succeeded|esc interrupt|Add a follow-up" | tail -3
```

| 屏底命中 | 含义 | 该做什么 |
|---------|------|---------|
| `interrupted` | **那一轮被打断**（最常见的假完工） | ⛔ 别当它还在跑：先看有没有半成品（`git status`），再续派或收工 |
| `esc interrupt` | **正在跑** | 正常，继续盯 |
| `succeeded` 且无 `esc interrupt` | 已交工 | 去核它的产出 |
| `Add a follow-up` 且无 `esc interrupt` | 空闲等指令 | 正常 |

⚠️ `BACKFILL-UNAVAILABLE session 当前仍 active` **不代表没事**——它只说“当前轮还没落成 idle”，
**不说明这一轮中途没被打断过**。⇒ 回看不可用时，**核屏是唯一可靠手段**。

⚠️ `session.execution.interrupted` **已在** `TERMINAL_EVENTS` 里（探针会报 `STAGE-DONE`）——
所以“中断了却没人知道”**不是缺事件**，而是**那个时刻没有探针在看**。修的是流程，不是加事件。

### ⛔ 小弟拿 `sleep N` 干等长门禁 = 白烧的墙钟（装配简报时就写死）

**实测（会话导出记录）**：一轮评审里工具时间的 **67–89%** 是一串 `sleep 240/270/285`，
等的都是同一道全量门禁；每一条除了 sleep 几乎只带一条 `tail <日志>`。
门禁本身不可省，**等法完全可省**——同一轮里那些时间本可用来读码、核证据、写报告。

**写进简报的硬要求（四条）**：

1. **门禁一开场就后台起**（拿到 diff / checkout 完立即起），**随后与它并行**做后面的活。
   ⛔ 禁「起后台 → 立即 sleep 等 → 再看」这个循环。
2. **收口前只取一次结果**（退出码 / 汇总行 / `tail`），取到即用；⛔ 禁固定间隔 `sleep N` 轮询。
3. **同一道长门禁一轮内只跑一次**；中间轮次只跑**触碰包 + 依赖它的包**，全量留到「准备判通过」前那一次。
   若这样做，必须写明「这是覆盖面让步，最终全量仍要跑一次」，⛔ 不让小弟自己决定缩面。
4. **“等”必须可观测**：要卡就卡在**退出码/汇总行**上，不卡在时间上。

**同一条纪律适用于我自己**：等我自己的门禁 / 构建 / 下载时不要 `sleep` 干等——
去做下一件事，回来再核（这与 §6.5 「用监控通知，不要轮询」同源）。

**度量口径**：要证明它真的在干等，读会话导出（见 `agent-session-time-forensics` 的
`references/opencode-record-layout.md`），按**单条工具耗时的降序 top-5** 看——
`sleep` 会直接堆在榜首；只看占比会被稀释掉。

## 4. 权限请示面板（Cursor 的对应物）

面板形态：

```
  △ Permission required
    ← Access external directory ~/somewhere
    Patterns
    - ~/somewhere/*

     Allow once   Always allow   Reject
     ctrl+f fullscreen  ⇆ select  enter confirm
```

**默认权限是 `{"action":"*","effect":"allow"}`** ⇒ 写文件、普通 shell **不弹面板**。
只有这些会弹（从 agent 权限规则读，别猜）：

- `external_directory`（访问工作树外的目录）
- `read` `*.env` / `*.env.*`（除 `*.env.example`）

⇒ **要测/演示权限面板，用跨目录访问，别用「创建文件」**（那个默认直接放行）。

### ⛔⛔ 写任务单时，产物路径一律落工作树内被 gitignore 的目录（如 `tmp/<task>/`）

**别让 opencode 读写工作树外的路径**（`/tmp/*.txt`、用户家目录别处、另一棵工作树）——
每个这样的路径都会触发 `external_directory` 面板，agent 在那里**静默等待**，
编排方若没挂探针就完全不知情。

「放 `/tmp` 因为它会被重启清空」这个直觉是反的：`/tmp` 恰好是树外最容易被拦的地方。
正确落法是工作树内的 gitignore 目录（`tmp/`、`*.log`）——既不入库、又不越界、还不被重启清空，
三条好处一次满足。

同理，**已写出树外的文件**：`cp` 进工作树再让它读，不要重跑一遍昂贵命令去重新生成。

### 按键语义（实测）

| 键 | 行为 |
|----|------|
| `←` / `→` | 在三项间**循环**切换，两端环绕。实测方向：**`Reject → Allow once → Always allow → Reject`**，即 **`→` 是「向 Always allow 走」** |
| `Enter` | 确认选中项 |

⛔ **移光标后必须先复核选中项再按 Enter，绝不能盲按**（`←` 会落到不可复议的 `Reject`），
**判「哪项被选中」的完整配方见本节末尾**——`capture-pane -p` 三项文本完全一样，
必须用 `-e` 读转义序列，且**字色与底色都要看**。

### ⛔ 面板卡住时：分诊看「申请的范围」，不是看「技术项还是授权项」

> ⛔ **本节曾教错，已改。** 旧版写「本单范围内的必要动作 ⇒ 选最宽但可回滚的选项（`Always allow`）」，
> 实际执行时我把「整个家目录 `~/*`」判成可回滚就按了 `Always allow` —— 这是**判据本身错**：
> 范围本身就是闸门，选项宽窄是次要的。操作者原话：「`~/*` 这种权限我整个目录是绝对不允许的。
> 这种情况下，你就应该拒绝，然后问他究竟要访问什么，把他要访问的范围缩小，然后再开给他。」

**分诊三步（顺序不能换）**：

1. **读 Patterns 行，拿到它要的确切范围。** 不读就按 = 盲批。
2. **范围判定**（三档）：

| 申请的范围 | 处置 |
|-----------|------|
| **家目录级 `~/*`、用户目录级、`/Users/<me>/*`** | ⛔ **一律 `Reject`，永不复议。** 然后让它把需求缩成**精确文件清单**（逐个绝对路径），逐项授权 |
| **本单契约里写明的目录**（cwd = 该目录时） | 属技术项，我拍。最宽可回滚选项即可 |
| **契约外但确属本单必需** | 先核「能不能换个路子不碰它」（CLI / 服务 API / cwd 内落文件）；换不掉再**逐文件**授权，不给目录通配 |

3. **按下之前自检一句**：我批的到底是「一个文件 / 一个工作目录」，还是「用户整个家」？后者 ⇒ 收回手。

**⛔ 拒绝之后必须做的事**：`Reject` 只解决这一次，它不会自己收敛范围。
要么在输入框发一条**要求它列出精确文件清单**的指令并停下，要么直接改派。
否则它会换个工具再撞同一堵墙（实测：`glob` 被拒后同范围的 `shell find` 照样跑通 ⇒
**权限面板不是访问的唯一闸门**，范围必须写进契约）。

**⛔ 根治比逐次授权便宜得多：派活时把会话 cwd 直接设成目标目录**
（`tmux new-session -d -s <t> -n agent -c <目标目录>`）。工作域天然封闭，
它连树外路径都想不到要申请，权限面板根本不会出现。实测：同一份任务单，
cwd 在目标目录内时全程零权限面板；cwd 在业务仓时它会去读工具链目录，逐次撞面板。

**`Always allow` 只对当时那条 Patterns 落库** —— 换成另一个范围（哪怕是它的父目录）会**重新弹**。
所以「我刚批了 Always allow」不等于「这类访问都放行了」，别据此跳过读 Patterns。

**⛔ 但 `cwd` 是建会话时的属性，改不了 —— 把已开好的会话改指另一棵树 = 必撞面板。**
`-c` 只在 `tmux new-session` 生效，已存在的会话无权换工作目录；而授权范围是**按建会话时的 cwd 落库**的。
⇒ 复用老会话派「基线已经换掉」的活时（例如合并完成后，把验收目标从特性 worktree 换成主树），
**第一条命令就会弹 `Access external directory <新树>/*`**——这是必然的，不是配置坏了、不是探针故障。
先核屏确认是这一条再处置，别把它当异常反复重挂。

处置顺序：
1. **报决策者批**（按 §4 三档分诊，Patterns 行读清范围）：目标工作树 / 主树这类「本单契约内的工作目录」属技术项，我拍；
   `~/*` 一律 `Reject`。
2. **长任务选 `Always allow` 而非 `Allow once`**——这类活会反复读写同一棵树，批一次会在下一次访问再弹一遍。
3. ⚠️ 报批时把口径讲清：`Always allow` = **整棵子树的读写**（本机范围，不影响仓内安全），不是「这一个文件」。
4. **更省事的是直接新开会话**（`tmux new-session -c <新树>`）。基线已换时旧上下文多半已过期，
   新会话不继承上下文反而是净赚——别为了「保住上下文」硬复用，那才是反复撞面板的根因。

⛔ **面板一出现在屏上就当场处置，处置顺序是硬闸不是参考。**
处置顺序第 1 条写的是「**报决策者批**」——易被读成「什么都要问人」。**不是**：
分诊表里「本单契约内的工作目录」那档写的是「**我拍**」。
⇒ 判据是 **Patterns 行的范围**：命中该档 ⇒ 自己按；只有 `~/*` 那档才惊动人。
⛔ **判据不是「技术上我能不能代劳」**——按「能不能代劳」判会把本该我拍的事无限上抛。

**⛔ 三项的循环方向：`→` 是「向 Always allow 走」**（`Reject→Allow once→Always allow`），
`←` 反向。从 `Allow once` 按 `←` 会落到 **`Reject`**——那是不���复议的一档。
**移光标后必须复核选中项再按 Enter**，用下方字色+底色判据核。

**⛔ 判「哪项被选中」的完整配方：字色 + 底色**

⛔⛔ 解析时 fg 与 bg 必须用两个变量分开跟，不能共用一个

我连续两次栽在同一处：用**单个**变量同时接 `38;`（字色）与 `48;`（底色）两类序列，
两者互相覆盖 ⇒ 判据永远不成立、函数返回空串。
⇒ fg（字色）与 bg（底色）各用一个变量，只在遇到对应前缀时更新：

```python
import re, subprocess
out = subprocess.run(["tmux","capture-pane","-p","-e","-t",SESS,"-S","-6"],
                     capture_output=True, text=True).stdout
for line in out.splitlines():
    if "Allow once" not in line: continue
    fg = bg = ""                       # ⚠️ 两个变量，不是一个
    for seg in re.split(r'(\x1b\[[0-9;]*m)', line):
        if seg.startswith("\x1b["):
            c = re.match(r'\x1b\[([0-9;]*m)', seg).group(1)
            if   c.startswith("38;2;"): fg = c
            elif c.startswith("48;2;"): bg = c
            continue
        if seg.strip() in ("Allow once", "Always allow", "Reject"):
            sel = (fg == "38;2;10;10;10" and bg == "48;2;250;178;131")
            print(seg.strip(), "  ← 选中" if sel else "")
    break
```

**⛔ 解析器返回空 ≠ 面板没了**：空只说明「我的判据没命中」（配色变了、面板换位、格式变了）。
**处置纪律：解析空时不得盲按。** 必须降级为**打印原始转义序列**人工判读：

```bash
tmux capture-pane -p -e -t <sess> -S -6 | grep "Allow once" | cat -v
```

（`cat -v` 把 `^[` 显式化，一眼能看出哪段带 `48;2;250;178;131` 底色。）
我实测正是靠这个降级路径判出高亮其实在 `Always allow`，避免了盲按。

（本节只保留上面那一个配方；本文件内搜索「当前选中」以它为准。）

**拒答后它自己换路继续**（实测：Reject 后 agent 说「Previous tool call declined」然后换个工具继续），
不会卡死等在这儿 —— 这点比 Cursor 的请示门省心。但**换路可能撞到同一堵墙**，见上。

⛔ **权限状态只能从 SSE 的 `permission.asked` / `permission.replied` 拿**：
`GET /api/permission/request` 在面板明明在等时返回 `data:[]`，**REST 端点不可靠**。

| 事件 | data 关键字段 |
|------|--------------|
| `permission.asked` | `{id, sessionID, action, resources, save, source}` |
| `permission.replied` | `{sessionID, requestID, reply}`（reply = `allow-once` / `always` / `reject` 实测值） |

**卡死判据**：`permission.asked` 已发、长时间无对应 `permission.replied` ⇒ 它在等裁决。

## 4.5 提问面板（AskUserQuestion）：**不在事件流里**，只能靠屏

OpenCode 的提问面板是 agent 用它自己的提问工具弹的，**不发 `permission.asked`** ⇒
SSE 事件侧**完全看不见**，小弟就那么静默等人，你能干等半小时。

⛔ **但它不是「只能靠屏」**（旧版这里写错，已改）：那个提问就是一次普通的工具调用
`name == "question"`，**明摆在会话消息 API（`/api/session/<id>/message`）里**，
入参含 `questions[].header` 与 `.options` —— **题面与选项都能直接读到，不依赖屏文案，也不受 TUI 滚屏影响**。
⇒ 要回看「它当时到底问了什么、我选了什么」，走 API 拿原文；屏上那份会被滚掉。
（取法与解析路径见**另一个技能** `agent-session-time-forensics` 的 references 里那篇
OpenCode 会话记录布局；⚠️ 那份引用不在本技能目录下。）

**实时告警仍以屏副路为主判据**（`scripts/screen_watch.py` 每 15s 读屏，命中
`enter submit` + `esc dismiss` 打 `SCREEN-QUESTION`，这条必须进 `watch_patterns`，见 §6.5）——
屏是**推**过来的、秒级；轮询 message API 是**拉**、有延迟且要自己判 pending。
两者互补：屏管「叫醒我」，API 管「叫什么、我怎么答的」。

```
  ┃  1. <选项一>（推荐）
  ┃  2. <选项二>
  ┃  3. Type your own answer
  ┃  ↑↓ select  enter submit  esc dismiss
```

⛔ **必须逐项选中并提交，不许 `esc` 退出**——退出而不选，它可能把预选项当默认执行。

**处置四步（缺一步都可能让它按错方向干完一整轮）**：

1. **读完整题面**：`tmux capture-pane -p -t <sess> -S -120`。视口只有尾部，题面会被滚掉；没读全就别按键。
2. **裁决先落盘**（写进它 `cwd` 那棵树的 `.briefs/`），再动面板。面板选择只带得走**选项描述里那点信息**，
   我裁决里的额外边界（不许 commit / 范围上限 / 汇报要标注什么）它看不到；而面板交互无留痕
   （配色会变、选中态可能没有视觉区分）⇒ **只存在于按键里的裁决等于没写**。
3. **面板上选中并提交**（默认落在第 1 项；要选别的先 `↓` 到位再 `Enter`）。提交后**核屏底恢复 `esc interrupt`**
   —— 没恢复就是没提交成功。⚠️ 选中态可能**没有视觉区分**（三项字色/底色全一样），别指望靠配色判；
   就靠「提交后它是否继续跑」。
   🔴🔴 **但「我显式选中了」本身不可信 —— 必须用散文复核（2026-09-30 夜两次实测）**：
   两次都是「面板问要不要授权免签 commit，我用 `↑` 明确移到第 1 项 + `Enter` 提交」，
   它**执行成了第 2 项**（第 2 次是「先不提交，等签名恢复」⇒ 白等一轮）。
   ⇒ **面板选择一律配一条散文兜底**：`Escape` 关面板后发一条
   「CTO 裁决：选第 N 项，<动作>，**明确排除**第 X、Y 项，**不要**<那个错误项描述的行为>」，
   再核 `capture-pane` 看到 `esc interrupt`。
   ⇒ **排除项必须写成行为描述**（如「不要等我审阅 diff」「不要等签名恢复」），
   不能只写编号 —— agent 是拿语义匹配的。
   ⇒ 收工类面板（是否开评审 / 是否合并 / 是否开新会话）**直接用散文答**，别碰面板。
4. **立刻发指针补边界**：「裁决已落盘 `.briefs/<file>` 末尾（含 X / Y），完成当前项后读它并落实」。

⛔ **别指望探针叫你**：屏副路那 15s 轮询是**后补的**；补上之前这类面板出现过两次，**两次都是我手工核屏才发现**。
⇒ 派活期间主动核屏，尤其在「该有进展却迟迟没动静」的时候。

> **好请示长什么样**：这类面板背后的请示往往质量很高——它**先自证「这不是基线自带的问题」**
> （跑一次基线 / `git stash` 对照，确认同一条命令在改动前是绿的），再给出**带范围的互斥选项**。
> 遇到这种请示**当场拍、别让它等**；反过来，只说「报错了」不给基线对照的请示，退回要证据。
> 我自己下「已核实 / 无影响」结论时同理，先跑基线对照再开口。

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

**⛔ 探针的寿命纪律与 SSE 的可靠性是两个问题，不要混判：** 屏幕监控类探针按设定寿命
到点自退并显式提示重挂（运行纪律，跑完一轮就该重新武装），是**有意的设计**而非缺陷；
而「寿命之内 SSE 断了就再不出声」是**实现缺陷**。两者都关乎「探针还活着吗」，
但一个靠重挂解决、一个靠改代码解决——**别因为规定了寿命就放行断流失效，也别因为断流有洞就去改寿命**。

| 维度 | Cursor | OpenCode |
|------|--------|----------|
| 结束信号 | hook（须先于启动配好，忘 chmod 静默失效） | **SSE（零配置）** |
| pane title | `✅ Ready` / `⏳ Working` 可判活 | 空闲恒为 `OpenCode`；**忙碌时变 `OC \| <任务名>`** ⇒ 只能作辅助佐证 |
| 忙碌指示 | `ctrl+c to stop` | `esc interrupt` |
| 请示门 | `Question N of M` 多问面板，`←/→` 翻页 | `Permission required` 单选三项，`←/→` 循环 |
| 拒答后果 | 容易停住等你 | **自己换路继续** |
| 会话身份 | `create-chat` 预分配 | `session list` 直接列（`ses_...`） |
| 排障入口 | hook 日志 | `session export <id>`（⚠️ 其 `outcome` 不可当判据） |

### 6.5 监控探针（scripts/watch.py）

> ⛔ **⛔ 派活前必须先挂 watch.py —— 这是硬纪律，不是可选项。**
> 实测踩坑（2026-09-25）：派完 opencode 只发指令、**没挂探针**，
> 它中途停在 `Permission required` 面板（读工作树外目录）静默等待，
> **我完全不知情**，直到偶然查屏才发现——已经过了很久。
> ⇒ 与 Cursor 侧同一条教训：**请示门 / 权限面板是事件流的盲区**，
>   SSE 只在「事件到了」时说话，**没人订阅就等于没监**。
> ⇒ **规矩**：`terminal(background=true, notify_on_complete=true)` 挂
>   `scripts/watch.py <session_id> <timeout_s> --tmux-session <sess>`，
>   **紧跟在派活之后、且在结束回合之前**；探针输出含 `PERMISSION-ASKED` /
>   `STAGE-DONE` / `WATCH-TIMEOUT`，任一都值得立即处置。
>   汇报里显式写「探针已挂（session_id=…）」，便于事后核对「当时到底有没有在盯」。
>
> **⛔ 但「先挂探针」在【新起会话】上做不到 —— 首单顺序是「发指令 → 取 id → 验真 → 挂」。**
> TUI 刚起来时服务端**还没有这个会话**（按 `location.directory` 过滤 `/api/session` 为空），
> `session_id` 由**第一条消息**创建 ⇒ 派首单之前**无 id 可锚**，硬等就是空转。固定顺序：
> ① 四步协议发指令，核到屏底 `esc interrupt`（= 真开始跑）；② **立刻**从服务端清单取 id
> （按 `location.directory == 本单工作树` 过滤，⛔ 不取自己笔记里的 id）；③ `active` 命中即锚点有效；
> ④ 挂探针并核到 `ANCHOR-OK`。**派发与挂探针之间只隔几秒**，⛔ 不许「等它跑一会儿再挂」。
> **会话已存在**（复用会话派下一单）时才回到上面那条：**先挂探针再发指令**。
>
> 两条同批实测：**新会话的 `title` 就是我那条指令的正文**（可当归属指纹；忙碌时 `pane_title` = `OC | <同一句>`，
> 空闲时回 `OpenCode`）；`/api/session/active` 返回 `{"data":{}}` 表示**当前没有任何 active 会话**
> （= 小弟空闲待命，不是在跑），⛔ 空字典不是「形状不对」、不是异常，别据此怀疑服务端。
>
> **⛔⛔ 探针遇到「要人处置」的事件时，必须让探针自己结束。**
> 权限面板是事件流的盲区——它一出现就说明对方在静默等人批准，而**探针继续挂着毫无价值**：
> 编排方的进程面板上 `last: PERMISSION-ASKED` 那一行永远不变，
> 看着像「我知道了」其实**没有任何人被叫醒**（探针不退出 ⇒ 没有完成通知 ⇒ 无人处置）。
> ⇒ 设计这类探针的硬规则：**「要人处置」= 进程退出 = 通知到达**。
> `scripts/watch.py` 的 `permission.asked` 分支应打印 `PERMISSION-BLOCKED` 后 `sys.exit(0)`，
> 并把 `source` 字段（哪条工具调用发起的请求）打进输出，否则看完不知道它在要什么。
> Cursor 侧的 `Question N of M` 面板同此理。
>
> ⛔ **「一轮做完」不是「不用盯了」；探针寿命必须绑「小弟存在」**（2026-09-25 操作者当面纠正，已改代码）
> 问法：是不是只有小弟收工了才可不挂？——**不是。只要 tmux 窗口还在，监控就得在**，
> 哪怕它停在 `✅ Ready` 待命、哪怕两轮任务之间空着。原实现有三个同源缺陷：
> ① SSE 终态 `sys.exit(0)`；② `backfill` 命中历史终态也退；③ SSE 断流/到点就结束。
> **实测代价**：这三种空窗里发生过「多选面板预选项被当默认执行、13 张现行截图被误移」，
> 当时无任何告警——因为没人看着。现行语义（`scripts/watch.py`）：
> | 事件 | 行为 |
> |------|------|
> | `STAGE-DONE` | **只报不退出**，继续等下一轮 |
> | `BACKFILL-DONE` | 同上（那是上一轮收工，不是本单结束） |
> | SSE 断流 / `--max-time` 到点 | 自动重连 + 回看，**不退出** |
> | `PERMISSION-BLOCKED` | **只报不退出**（处置完我继续盯；旧版退出是错的） |
> | tmux 窗口/会话被解散（人工 `kill-session`） | 才退出 |
> | `WATCH_MAX_SECONDS`（默认 86400） | 显式上限，防跑飞 |
>
> ⛔⛔ **反过来不成立：tmux 窗口自己消失时，探针不会跟着退。**
> TUI 会**自行退出并连带关窗**（实测同一段工作里三个不同任务的窗在不同时点先后没了，都非我手 kill），
> 而带 `WATCH_MAX_SECONDS` 的探针**照样活着**（`ps` 在、`--tmux-session` 指向一个已不存在的窗口）。
> ⇒ 这会留下最坏的一种假信号：**看着在监控，其实窗口早没了、屏侧告警全是空转**。
> **纪律**：上图那条表不能当“会自动收尾”读——
> ① 每次收工/换工时**主动核** `tmux ls`，把死窗口对应的探针 `kill` 掉（`ps` 复核退出）；
> ② **判「小弟被解散」不能只看 tmux 窗消失**，先核服务端会话是否还在（会话可以在服务端存活），
> 要接着干就重新挂窗；
> ③ 反之，**「探针还活着」不能当「小弟还在跑」的证据**——两个信号必须分别核。
>
> **⛔ 判活不能用「无输出」**：探针只打印不输出心跳，长时间静默是正常的，
> 不等于它死了。核存活用 `ps`，不靠盯屏幕。

> **⛔ `watch_patterns` 撞上限会「静默降级」投递通道 —— 这是重挂的判据，不是探针死了。**
> 报活型探针（每 N 分钟自报存活那种）用 `watch_patterns` 起，撞到投递次数上限后通道会退化成
> 「仅进程退出才通知」：**探针照跑、屏照看，中间信号我一条都收不到**。看到「watch patterns disabled /
> 达到投递上限」这类通知时，先 `ps` 核探针与对应 tmux 窗口是否都还在 → 都还在就是通道问题。
> 处置是**降低信号频率 + 靠探针内去重压条数**（让整轮信号数落在上限内），**不是**换成
> `notify_on_complete`——对永不退出的探针那样换等于**继续失明**。⛔ 重挂前先读下面这条「一个 target 只留一个探针」。

> **⛔⛔ 一个 target 只能有一个探针：重挂前先数，重复的立刻收掉。**
> 重挂与多轮派活最容易留下的垃圾就是**两个探针盯同一个会话 / 窗口**——每个信号投递两遍，
> 而我常把第二遍误读成「又发生了一次」，据此做出重复动作。
>
> ```bash
> # 每个 target 应恰好 1 命中
> ps -eo pid,command | grep -E "[w]atch.py|[s]creen-mon.py" \
>   | grep -oE "(ses_[A-Za-z0-9]+|<tmux-sess>:[0-9]+\.[0-9]+)" | sort | uniq -c | sort -rn
> ```
>
> 计数 >1 ⇒ `kill -9` 掉**较旧那个**（`etime` 大的），保留带 notify 通道的新探针。
> ⚠️ **收完必须 `ps -p <pid>` 复核**：`kill -9` 的退出回放通知（`exited (exit code -9)` + 它的全部历史输出）
> 会在**一整轮之后**才到达，很容易被误读成「探针自己崩了」而去查探针的 bug。
> 回放里若是一串规整的自报行（`RENEW` 之类），那就是我自己的 `kill`，不是故障。
>
> **⛔ 重挂之后必须再数一次，而且计数要用 `ps -eo pid,ppid` 判归属。**
> 实测形态：`ps` 核到旧探针已停 → 重挂新探针 → 紧接着 `ps` 又看到**同锚点两条**。
> 真因不是重挂重了，而是**守夜兜底在我 kill 掉的瞬间看到「这个 sid 没探针」**，立刻补挂了一条脱离式。
> 判据：`ppid=1` 的是**守夜兜底的脱离式**（只落日志，Hermes 收不到信号），
> `ppid=<Hermes 会话父进程>` 的才是**带投递通道的那条** ⇒ 保留后者，`kill` 前者，再复核。
> ⚠️ **别用 `grep -c '<sid>'` 判唯一性**：我自己的 shell 包装命令行里就含那个字符串，
> 会把「只有一条」数成两条、也会把「零条」数成一条（自匹配假阳性）。
> 正确写法是列出 `ps -eo pid,ppid,etime,command` 逐行看，或 `ps -p <pid>` 直核那一个 pid。
>
> **⛔⛔ 探针退出 ≠ 可以不挂下一个（2026-09-25 实测漏挂）**：本单交工、探针报完
> `STAGE-DONE` 自退后，我派了**两轮**下一单（任务 C、任务 B）都**没重挂探针**，
> 只靠人工 `capture-pane` 盯着；期间出了「预选面板被当默认执行、13 张现行截图被误移」
> 这类事故，**期间无人被叫醒**。⇒ **纪律：会话活着 + 要派下一单 ⇒ 先挂探针再发指令。**
> **判据**：只要屏上还是 `esc interrupt` 或会话未收工，探针就必须在；「上一单做完了」
> **不是**不挂下一单的理由——同一 session 会连做多单（实测一晚做了 A → A2 → C → B 四轮）。
> **收工只在真正结束时**（无待派单 + 屏上 `esc interrupt` 消失 + 工作树干净）。
>  **⛔ 换单的两步不许拆开做**（实测踩坑）：kill 旧探针后去做别的事（查 issue、改看板、查另一单），
>  派下一单时**又把探针忘了**——那段时间小弟在飞、我完全不知情，而汇报里还写着「在跑」。
>  ⇒ **把「kill 旧探针 + 派下一单 + 挂新探针」当一个不可分割的动作**：
>  同一轮工具调用里完成派单与挂探针（派单在**复用已有会话**时可先挂后发；
>  **新起会话**则是「发指令 → 取 id → 验真 → 挂」，见下，两者之间只隔几秒）。
>  自检一句：**我现在手上有没有一根活着的探针？** 没有 ⇒ 不许发下一单的指令。
>  ⛔ 也不许「先派活、稍后补挂」——实测那次补挂时小弟已经交工，等于整轮无人看管。
>
> **另外两条同源纪律（派活当场就要满足，不是事后补）：**
> - **⛔ 决策权在我手里的事直接做，不反问。** 总问不是「这件事重不重要」，
>   而是「**决策权在谁手里**」：不影响不可逆状态 + 判据已在文档/技能里写明 + 属执行层动作
>   ⇒ 三条全中就直接做，只回一句「已做 X，状态 Y」。
>   **小弟问我要不要开新会话 / 要不要继续 / 要不要授权 ⇒ 那是小弟在问我，不是问操作者，我当场拍。**
>   把小弟问我的问题原样升级给操作者 = 空转型失职。
- **⛔ 派活后汇报默认 1–3 句**（做了什么 + 现在状态 + 需要他动作时一句话）。
  不复述他已知的、不列无用备选、不问已决定的事。细节等他问。
- **⛔ 汇报里的“派活受阻”要三态分清，别混成一句“处理中”**：
  **材料已备齐** / **动作未发出**（卡在哪个动作）/ **等谁放行**——三样都写出来。
  漏掉「未发出」这一态，小弟会以为已经在跑；漏掉「等谁放行」，操作者不知道该按哪个键。
- **⛔ 浏览器驱动的活（演示 / 交互测试 / 重拍证据）也归小弟，我只派单 + 独立复验。**
   操作者当面纠正过：「你停下来，把浏览器演示和测试的工作交给 opencode 小弟。」我此前一直自己
   开着窗口点、试尺寸、改路径——那是执行作业，不是判断作业，且占掉我大量回合。
   **拆法**：小弟负责「起服务 → 登录 → 点路径 → 截图 → 落盘」；我负责「写清路径与判据 →
   派单 → 另开一次独立 `vision_analyze` 核图 → 裁决」。⛔ **我核图必须自己开图**，
   不采信它的「已核」自评（见 `delegated-work-verification`「证据物本身要看」）。
   同理，**为省一轮而自己动手的诱惑**（"就调一下窗口大小 / 就点一下看看"）一律先问：
   这是我该做的判断吗？多数不是——判据与目标给小弟，操作让它做。
- **⛔ 派单前核「两份 open issue 是否覆盖同一缺陷」——看不见的撞车比在飞撞车更贵。**
   `worktree list` / `tmux` 只能看见**已经开工的**，看不见**已登记但没开工的 issue**。
   实测：两个 open issue 写同一个缺陷、正文互不引用、**给的两个修法还不同**；
   若都开工会在同一个文件上返工两次。⇒ 派活前跑
   ```bash
   gh issue view <A> --json body --jq .body | grep -inE "<核心概念>|<关键符号>"
   gh issue view <B> --json body --jq .body | grep -inE "<核心概念>|<关键符号>"
   ```
   **重叠就把「以哪个 issue 为唯一施工入口」连同两个修法的差异一起报决策者**，
   ⛔ 不自己挑一个开干——选法是架构裁决，不是执行动作。

> ##### 换单时的三条操作纪律（实测一夜七单反复踩）
>
> 1. **一条指令不带任何前导符号**（见上文 §6.5：首字符是普通汉字，正文无 `!` `#` `` ` `` `*` `$`）。
>    实测一晚失败三次：`!`（引 PR 号）、`$`（我以为的安全写法）、`/`（我以为的 slash 命令）。
> 2. **换单 = kill 旧探针 + 派单 + 挂新探针，一个不可拆的动作**。拆开做的那次，小弟在飞、我无感，
>    汇报里还写着「在跑」。自检：**我手上有没有一根活着的探针？** 没有 ⇒ 不许发下一单指令。
> 3. **新起会话的顺序是「发指令 → 取 id → 验真 → 挂」**（会话 id 由首条消息创建，派前无 id 可锚）；
>    **复用已有会话**才是「先挂后发」。
> 4. **在飞树里我自己改了文件 ⇒ head 会变 ⇒ 门禁要按新 head 重跑**。实测单行修复合入后，
>    先跑的那次全量作废（指纹以 head 为准）。顺序：先提交修复，再起门禁。


```bash
# 必须由 Hermes 托管；subprocess.Popen 起的进程 Hermes 不认，退出时不通知
terminal(command="python3 <skill>/scripts/watch.py <session_id> <timeout_s> --tmux-session <s>",
         background=true, notify_on_complete=true)
```

- ⛔ **投递通道必须与探针寿命匹配**（两种单用都是瞎的，本会话两种都栽过）：

| 探针寿命 | 必须用的通道 | 为什么 |
|---------|------------|--------|
| **会退出**（一次性核验、跑完即止） | `notify_on_complete=true` | 退出即通知，中途信号本来也不需要 |
| **永不退出**（寿命绑「小弟窗口还在」） | `watch_patterns=[低频高价值前缀]` **＋** `notify_on_complete` 兜底 | ⛔ **`notify_on_complete` 只在进程退出时通知**——永不退出的探针用它是**全程失明**：它照常打印 `STAGE-DONE` / `PERMISSION-BLOCKED`，但一个信号都投不到我这儿。实测交工后 2 分钟才靠手动核屏发现。 |

  ⚠️ 所以「`watch_patterns` 有 8 次上限 ⇒ 别用它」是**错的半句话**，正确表述是：
  **上限约束的是条数，不是能不能用。** 配 `watch_patterns` 时把前缀收窄到**低频高价值**那几条
  （现行七条：`STAGE-DONE` / `PERMISSION-BLOCKED` / `SCREEN-QUESTION` / `ANCHOR-FAIL` /
  `TERMINAL-PENDING` / `TERMINAL-UNVERIFIED` / `WATCH-EXIT`），
  同时保留 `notify_on_complete` 兜住探针异常退出。

  ⛔ **`SCREEN-QUESTION` 必须进 `watch_patterns`**：OpenCode 的提问面板（AskUserQuestion）
  **不走 `permission.asked` 事件** —— SSE 侧完全看不见，小弟就那么静默等人，你能干等半小时。
  屏副路（`scripts/screen_watch.py`，每 15s 读屏）按实测文案 `enter submit` + `esc dismiss`
  识别它并打印 `SCREEN-QUESTION`。**2026-09-28 实测缺这条踩了两次**（两次都是我手动核屏才发现）。
  另注：同一次也会在 SSE 侧到点打印 `QUESTION-PANEL`，但那要等一次 `--max-time` 断流，太慢 ——
  15s 的屏副路才是主判据。

  ⚠️ **但 `SCREEN-QUESTION` 会有假阳性**（2026-09-29 实测一次）：屏上瞬时渲染即可命中，
  面板可能早已消失、根本没进待答态。**别只凭它就去发键**（乱发等于替它答一个它没问的问题）。
  判真伪两步：① 屏底是否真有面板（`enter submit` + `esc dismiss` 且**处于等人状态**，
  不是在 `Thinking`/`Writing…`）；② **查服务端该 session 最近消息里有没有 AskUserQuestion 调用**
  （只读 sqlite，最准）：
  ```python
  con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)   # db=~/.local/share/opencode/opencode.db
  rows = con.execute("select data from session_message where session_id=? order by rowid desc limit 40", (sid,))
  # data 里出现 "AskUserQuestion" 才是真问了
  ```
  最近消息里搜不到 ⇒ 它在正常干活，不要动它。

  ⛔ **两条前提必须同时成立，否则额度照样烧光**（两者已在 `scripts/watch.py` 内置、均已回归）：
  ① **跨重连去重**——去重集合必须声明在重连循环**之外**。声明在循环内 ⇒ 每次断流重连都重报同一条
  终态，8 次额度几分钟烧光。
  ② **启动即验锚点**——锚点不存在直接 `ANCHOR-FAIL` 退出，见 §1.5 / §2.5。

  ⛔ **自检：起探针后第一件事是「我这条通道真能收到信号」**，不是确认进程活着（`ps` 活 ≠ 信号通）。
  信号该到却没到时按三段分诊，**别直接下结论「探针坏了」**：

  ```bash
  ps -p <probe_pid>                                  # ① 进程还活吗
  process(action="log", session_id=<probe_session>)  # ② 它的输出里有那条信号吗
  ```

  | ① | ② | 结论 |
  |---|---|---|
  | 活 | 有信号 | **投递通道坏了**（多半撞上限降级或只配了 `notify_on_complete`）→ 按上表重挂 |
  | 活 | 无信号 | 真的没交工 ⇒ 核屏底终态（§3.5），不是监控问题 |
  | 亡 | — | 探针真退 ⇒ 看它最后一行报什么（`WATCH-EXIT` 才是正常退场） |
- 探针按 `data.sessionID` 过滤，只认本会话；命中任一终态事件即打印 `STAGE-DONE` 并 `sys.exit(0)`。
- 输出 `TURN-START` / `STAGE-DONE`（带 start_ts、end_ts、duration）/ `PERMISSION-ASKED` /
  `PERMISSION-REPLIED` / `QUESTION-PANEL` / `WATCH-TIMEOUT`。

### ⛔ 权限通知可能已经过期：处置前先核屏，核不到就不处置

`PERMISSION-ASKED` / `PERMISSION-BLOCKED` 到达时，**它可能已经自行消解**（agent 换工具绕过、被后续消息顶掉、
面板被别的交互关掉）。实测：我处置晚了一轮，核屏时面板已不在（面板关键词 0 命中），
而 `GET /api/session/active` 显示会话仍 active——**通知是那一轮的，不是现在的**。

**处置前必做两步**：
```bash
# ① 面板还在吗？（三项任一命中 = 面板在屏上）
tmux capture-pane -p -t <sess>:0 -S -60 | sed 's/\x1b\[[0-9;]*m/ /g' \
  | grep -cE "Permission required|Allow once|Always allow|Reject"
# ② 它还在跑吗？（屏底忙碌行优先于通知本身）
tmux capture-pane -p -t <sess>:0 -S -3 | grep -E "esc interrupt"
```
- ①=0 ⇒ **面板已不在，不要按过期通知按键**（按 `←`/`Enter` 可能落到输入框里成为一条消息，
  实际是 `interrupted` 的常见成因）；先确认它当前在做什么再决定要不要发指令。
- ②命中 `esc interrupt` ⇒ 它正在跑，⛔ **不要发纠正指令打断**；发指令前先判断它是不是已经自己走对路了。

**⛔ 通知只说「那一刻发生了什么」，不等于「现在需要你」。** 所有探针通知到达后，
先核屏拿当前态，再决定动作——这条与 §3.5「重挂探针必须先核终态」同源。

### ⛔⛔ 派活指令被安全审批拦下（`BLOCKED: timed out without user response`）= 指令**没发出去**

`send-keys` 会失败在**发送这一步**：命令被安全审批拦下、超时未确认 ⇒ **整条 `send-keys` 未执行**。
⛔ **不许重试、不许绕道**（换 `tmux load-buffer`、换 pane、写个文件让小弟自己读、缩小指令再来一遍
都算「达成同一结果」，审批规则禁的是这个不是那一条命令）。

**处置三步（顺序不能换）**：

1. **用只读手段核真实状态**——⛔ 不要假设已派出。核 `pane_title` 是不是你刚设的新任务名、
   `capture-pane` 输入框里**有没有**那条文字、屏底有没有 `esc interrupt`。
   标题没变 + 输入框空 ⇒ 确认未发。
2. **如实报「材料齐、动作未发」并写清卡在哪个动作**，以及解除需要什么（决策者放行那次审批）。
   ⛔ 别说成「在处理」——那会让对方以为已经派出去了。
3. **⛔ 别空转等**：转做**不依赖派出**的只读活。实测被拦下后靠只读核验挖出了另一个 issue 的
   真实实现缺口、发现两份 open issue 覆盖同一缺陷（给法还不同）、以及一条**违反仓级铁律的性能缺陷**
   （无界全表加载），等放行时材料已齐，**等待时间没白费**。三条现成命令：

   ```bash
   # ① 在被触及的子系统里扫铁律违规（只读）
   grep -rn "<违规模式>" packages/<sub>/src --include=*.ts | grep -v test
   # ② 登记冲突：两份 open issue 是否覆盖同一缺陷
   gh issue view <A> --json body --jq .body | grep -inE "<核心概念>|<关键符号>"
   gh issue view <B> --json body --jq .body | grep -inE "<核心概念>|<关键符号>"
   # ③ 下一刀的前置：目标能力在仓里现成吗
   grep -rn "<新能力关键词>" packages apps --include=*.ts | grep -v test
   ```

   **⛔ 边界：被拦期间不得顺手改任何文件**（包括“就一行错别字”）——工作树状态是放行后验收要比对的基准，动了就搅浑了。

⇒ 监控纪律在这里照旧：被拦期间小弟窗口仍在、探针**仍必须挂着**（它可能正在跑上一单），
被拦的是**新指令**不是**已有监控**。

### ⛔⛔ `STAGE-DONE` 到达但屏上还在跑 = 假终态，**不要按它推进下一步**

实测第三类假终态：`STAGE-DONE`（779s）到达，但屏底仍是 `esc interrupt` + `↓ 1 shell`，
`/api/session/active` 有 3 个 active 会话——agent 在本轮内**接着**做下一件事
（读文件 → 起服务 → 截图），`session.execution.succeeded` 只盖住了主轮那一段。

⇒ **`STAGE-DONE` 只允许触发「我来看一眼」，绝不允许直接触发「推进流程」**。
推进前硬闸两条，缺一不可：
```bash
tmux capture-pane -p -t <sess>:0 -S -3 | grep -E "esc interrupt"     # 有 = 还在跑
curl … /api/session/active | (数 active 会话)                          # >1 = 有并行工作
```
任一命中 ⇒ 继续等；并且**别把「工作树看起来没变」当它没进展**（它可能正在写文件、
起服务、或只是还没落盘提交）。

**⛔ 这条对「通知驱动的自主长跑」尤其致命**：探针通知是**唯一**会把我叫醒的东西，
一旦我在通知到达时就推进流程，后面整串动作（验收 → 派下一单 → 合并）全部建在假终态上。
所以通知到达后的**第一个动作永远是核屏**，不是核产物、更不是推进——
通知负责「叫我」，屏负责「现在是什么态」，产物负责「它干了什么」，三者不可互相顶替。

**⛔ 假终态在长轮次里是高发而非例外**：实测同一会话一晚触发两次，
间隔仅一轮（779s 后又 232s），每次形态不同（一次有子会话、一次只是同轮内接着做下一件事）。
⇒ 不要因为「上一次是真交工」就放松复核；每次都跑那两条命令。

**⛔ 首因是「我排了多笔追加裁决」**：裁决落文件 + 一行短指针**排队**（⛔ 不要用 `Esc` 打断；`Esc` 只留给要停手重写的场合）之后，它做完当前轮 → 收下一条 → 再跑一轮
⇒ 探针**按轮各报一次** `STAGE-DONE`，第 N 次只代表「第 N 笔做完了」，**不代表整单收工**。
每收到一次都重跑上面那两条命令；三者齐了才算收工：**屏底回 Ready + 约定产物落盘 + `git log` 出现新提交**。
⛔ 不许把「探针说交工」直接转成对操作者的结论——核屏是唯一凭证（报错了比报慢了贵得多）。
（`↓ N shells` = 它在跑**并行后台 shell**，典型场景是同一道门禁在两条不同路径复跑；有它时尤其要等那几条 shell 的产物落盘。）

**⛔ 追加了动行为面的提交 ⇒ 之前的全量绿作废**：新增提交只要碰**门禁实现 / `scripts/**` / hook / CI 配置**，
就必须在**新 head** 上重跑全量，⛔ 不许拿旧 head 的绿当凭证（纯 `*.md` 追加可免）。

**多轮/假终态的成因与派生规则**（含排队裁决、`↓ N shells`、重算门禁账）见 `references/stage-done-false-terminal.md`。

屏幕采样是 SSE 的**兜底**，二者不能有依赖关系。最容易写出的形态是把采样放进流读取循环里，
或写成流退出分支的**后续**——**两种都会让兜底在流一断时一起失效**：

- 周期性采样**不可寄生在 `for line in <SSE 流>` 的循环体内**（以事件到达为时钟；实测该流每 ~5s 一行心跳，
  高频下看着完全正常，**一旦静默就彻底不跑**）。
- 流不可用时（连接失败 / 断流）应当**继续主循环并重连**，而不是 `break` 掉整个探针；
  把采样写成 `if line is None: break` 之后 ⇒ 第一次采样把计数加到 1、流随即退出，
  **永远等不到第二次确认**，真静默下只报超时。
- 设计评审就问一句：**「如果 SSE 永远不说话，这次采样还会跑吗？」**

**配「连续两次确认」这类去抖时，两次观察之间必须真的间隔 ≥ `SCREEN_CHECK_INTERVAL`**，
由**时钟**驱动（后台读线程 + 队列 `get(timeout=...)` + 主循环 `except Empty: continue`），
不可由**流到达条数**驱动。验收必须包含一组**「事件源完全断流」**的用例：
把端点指向不存在的端口即可（不改被测代码），断言它仍在 ~2×interval 内报出面板，而不是超时。
（探针自测方法与 harness 见技能 `background-daemon-ops` 自身的验证章节。）

### ⛔⛔ 分支上多出来的提交：先核 actor，再判「越权」

简报里写了「⛔ 不许 merge 上游基线」，我看到分支上多一个 merge 提交 + `git status` 有改动，
当场判执行者越界并写进了汇报。**核一条命令就能避免**：

```bash
git log -1 --format='%h %an %ae %ad%n%s' <merge-sha>
```

| actor | 结论 | 正确动作 |
|-------|------|---------|
| 执行者 | 越权 | 按简报禁令处理（并问它为什么需要） |
| **操作者本人** | **不是越权，是操作者亲手做的** | 收回那条判断，改口「这是你手动 merge 的，不计入它的问题」；并说清**简报里那条禁令只约束它、不约束你** |

⛔ **判「谁干的」不能看 commit 形状（merge 提交、作者名都可能被 `-c user.*` 改过）**，
但 `%an/%ae` 足够判绝大多数；同一人（我派它 + 手动操作都记同一个名字）时以**时间线 + 指令历史**对：
那次是谁主动下过 merge 指令。⇒ 拿不准就**问一句**，不要先定性再改口。

### ⛔⛔ 「为保持最新 merge 上游基线」会把已拿到的全量绿作废

实测一晚上多起两轮全量的真因：执行者发现落后上游就 merge，merge 改 HEAD ⇒
**门禁指纹（以 HEAD 为准）作废** ⇒ 不得不重跑；而它重跑完又发现又落后，于是再 merge ⇒ 循环。
⇒ 简报里写死：**⛔ 不许为「保持最新」merge 上游基线**；确有依赖/冲突需要 ⇒ **先停下来问我**。
（我采纳了「上游修复后 merge 是对的」的建议后，额外成本就是这一整轮重跑——值得，但要在简报里写明。）

### ⛔⛔ 合并前评审技能与「全量次数上限」会撞车——必须给优先级

仓内 PR 评审技能有一条硬规矩：「判通过前必须有一次**同 head** 的全量绿；head 变了就重跑」，
并带一条「无行为变更可免跑」的例外。实测执行者把上游 merge 带进一行纯 `.md` 台账追加后，
既没用免跑例外、也没理会我简报里的次数上限，直接起了新一轮全量。

⇒ 简报里给优先级（三行就够）：
1. 先跑仓内评审技能自带的**免跑分类命令**（`git diff --name-only <base>..<head> | grep -vE '(\.mdx?)$|^docs/'`），**无输出 = 命中例外 = 免跑**，不计入我的预算；
2. 不命中才重跑，并计入预算；
3. **会超过上限 ⇒ 停下来问我**，不许自行取舍。

**同一条**：追加**纯 `.md`** 提交不触发全量重跑（指纹是**行为面**不是提交数）——
这条也要写进简报，否则会为一行台账重跑全仓。

### ⛔⛔ `STAGE-DONE` 之后出现大批意外 staged 文件：先查 `MERGE_HEAD`，再谈「越权」

**实测（2026-09-25 晚）**：验收一单冲突解法时 `git status` 跳出 **162 个** staged 文件，
全是另一个子系统 PDF 流水线的东西——我那单只授权改 2 个文件。表象完全像「小弟越权大改」。
**真相**：它执行了 `git merge origin/main`，把上游领先的几十个提交合进来并解了冲突、
**已入 index、未 commit**（`HEAD` 未变、`MERGE_HEAD` 存在）。它屏上也自述了
「未新增提交 / MERGE_HEAD 存在 / 未 push / 未碰其他文件」。

**核验顺序（错一步就会误判成事故，甚至回退掉人家的成果）**：

```bash
git -C <worktree> rev-parse -q --verify MERGE_HEAD   # 有输出 = 合并已解决未 commit
git -C <worktree> log --oneline -1                    # HEAD 未变 ⇒ 确实还没 commit
git -C <worktree> rev-list --count HEAD..origin/main  # 落后多少
```

| 判据 | 结论 |
|------|------|
| `MERGE_HEAD` 有输出 **且** HEAD 未变 | 合并中途态 ⇒ 那些文件是**上游带进来的**，不是它自撰的。核范围用 `git diff --cached --name-only` 对照**它被授权的清单** |
| `MERGE_HEAD` 无输出、HEAD 未变 | 才是它真自撰的改动 ⇒ 按越权判 |

**⛔ 核来源必须对远端引用，不要只查本地分支**：本地 `main` 可能陈旧于 `origin/main`，
拿它 `git cat-file -e` 查不到文件时会误判「来路不明」⇒ 正确写法是对 `origin/main` 查。

**⛔ 探针报 `STAGE-DONE` 只说明「这一轮执行完了」，不说明「工作树处于我预期的状态」。**
合并中途态就是典型：终态干净、但工作树有 160+ 项待处理。⇒ 核 `STAGE-DONE` 之后**必须**加一步
`git status --short | wc -l` + `rev-parse --verify MERGE_HEAD`，再决定「接下一单」还是「先收合并」。

**⇒ 对小弟的追加指令**：合并类操作收尾时，要求它明确交代
「是否 commit / 是否 push / MERGE_HEAD 是否还在 / 哪些文件是合进来的 vs 自己改的」。

### ⛔⛔ 派活前把「上游会漂移」算进去：授权清单与合入内容会互相污染

同一棵树在解冲突时若 `origin/main` 已领先几十个提交，**合入内容与本单授权范围必然重叠不清**。
⇒ 派合并/解冲突这类活时，简报里除授权清单外还要写明：
「以 `origin/main` 为合入源；只解冲突标记的文件；合入带来的其它文件**不许手改**；
收尾交代 `MERGE_HEAD` 状态与是否 commit」。
这样它自述的范围才可核，我验收时也不会把它带进来的上游改动当成它跑偏。

### ⛔⛔ 探针报 `STAGE-DONE` ≠ 它交了工（被测方自评不入门禁）

探针的职责只是**喊我来看**，不是替我验收。`STAGE-DONE` 到达后，**先核屏再核产物**：

```bash
tmux capture-pane -p -t <sess>:0 -S -3000 > /tmp/pane.txt   # -S 拉大回看长度，-40 只够看到尾部
grep -nE "interrupted|succeeded|仍在进行|Need wait" /tmp/pane.txt | tail
ls -lt .briefs/ | head                     # 产物落盘了吗
git -C <worktree> status --short          # 只读派活时应当是空的
```

| 屏上 / 盘上 | 含义 | 动作 |
|------|------|---------|
| 有「仍在进行 / Need wait … notification」+ `↓ N subagents` | 它自己都说没完 | **别当交工**，继续盯 |
| 有子代理计数但无该声明 | 仍有并行工作在跑 | 核 `/api/session/active` 的 `parentID` |
| 零产物落盘、结论只在屏上 | ⛔ **口头结论在门禁里等于没交** | 发指令要求把结论写成仓内 gitignore 目录里的文件（`.briefs/`），并贴屏上一份 |
| **`git status` 冒出大批我没派过的文件** | 上百个 `M`/`A`，多在别的子系统 | ⛔ **先当「中途合并未 commit」而非「它越权」**：`git rev-parse -q --verify MERGE_HEAD`（或 `REBASE_HEAD`/`CHERRY_PICK_HEAD`）有输出 ⇒ 合并已解决、已入 index、未 commit，那批是**被合进来的上游内容**。见下 |
| 屏底只有汇报尾部、中间被滚掉 | 视口截断 | 用 `-S -3000` 回看；拿不到就让它重写落盘 |

**派评审/验收类活时就把「结论必须落盘 + 贴屏一份」写进简报**，不要等交回来才发现没落盘——TUI 视口会把长汇报截掉，而那正是分级理由与证据所在的位置。

### ⛔ 验收命令我没先自跑过 = 我自己造的不可执行判据

给执行者的每条验收命令**必须是我自己先跑过、确认能在合理时间内跑完的**。实测：我给了一条自己没验的全仓测试命令，执行者如实报「超时未完成、全量门禁未闭合」——**它没撒谎，是我的判据不可执行**，但门禁照样闭不了。
⇒ 派活前先自跑；跑不完就明写「此命令可能超时，超时报『未闭合』而不是『失败』」，并给一条已验证的替代命令。

**⛔ 判据里凡有 grep / 点名检查，取词必须来自「实现真源」，不能来自计划里的建议名或我记得的措辞。**
实测自造的假 FAIL 两条：① 拿计划提案里的函数名去 grep，实现用的是另一个等价名 ⇒ 判据红、交付无辜；
② 拿一整句措辞去 grep，实现把同一意思写成了别的词序 ⇒ 同样假红。
⇒ 两条硬规矩：
1. **先 grep 定实际标识符，再写进判据**（`grep -rn '<概念>' <包>/src` 拿到真名），判据里引用的是**真名**；
2. **措辞类判据用词根/正则，不要整句**（`grep -E '<关键词1>|<关键词2>'`），并允许同义表述。
⇒ 复验脚本报红时**先怀疑判据自己**（大多数首轮 FAIL 是判据写错，不是交付错），
改正判据后要**重跑整本**再报数——⛔ 不许只报「改正后的那几条 PASS」了事。

#### ⛔ 判据里的**工具链**要先核「它在本仓真实存在」——不存在就不许让执行者现装

自跑之前还要多问一层：**被验的那个能力，本仓有现成设施吗？** 核三处——① 根 / 包的
`package.json` scripts；② turbo / 任务配置里有没有那个 task；③ 该工具在不在**本仓依赖**里、
配置文件在不在目标包内（`tsconfig.json` 之类）。

**实测**：一份规格把「类型检查」写进了验收判据，而仓里**根本没有 typecheck 设施**
（任务配置里 tasks 只有 `test`、`typescript` 不在依赖、目标包连 `tsconfig.json` 都没有）
⇒ 执行者只能 `bunx typescript@5.8.3 tsc` **现拉一个仓外工具**，**卡死 24 分钟**才被中止，
占掉那一段 68% 的墙钟（该段有效工作只有 11 分钟）。同一份计划里两条 flags 还自相矛盾
（`--module nodenext` 与 `--moduleResolution bundler` 不共存），根因也是没人先跑一遍。

⇒ **三条规则**：
1. **门禁只能由仓里现成的命令构成**——权威口径就是仓内那一条；凡写「跑 X 检查」，
   先问 X 在本仓是不是一条现成命令，不是 ⇒ 换掉它。
2. **确需新设施 ⇒ 先立一条前置任务把设施建起来**，不要把它塞进长活的验收栏让执行者顺手装。
   现装 = 长超时 + 拉外网 + 版本漂移，而且是一次性的垃圾时间。
3. **自检一句**：**这条命令，我在这棵树上自己跑过吗？跑通了吗？跑了多久？**
   三问答不出来 ⇒ 先自己跑一遍，再写进简报。
4. **要新建的设施，先自己量一次量级再定口径。** 仓里没有 ✕ 检查 ⇒ **先量**：既有问题有多少、
   集中在哪几个单元。量级决定判据形态——**上千条既有问题 ⇒ 设施只可能是「机器基线 + 增量判红」，
   绝不可能是「0 错才算过」**；不量就写判据 = 又造一条不可达成的判据。
   量级探针放**临时文件、跑完即删**并核 `git status` 干净（树里不留痕）。
   ⚠️ 一次性探针（**单份配置套全仓**）会**大量假阳性**（别名、构建/工具族不同的包全被算进来）——
   **只用来估量级与分布，⛔ 不许当缺陷清单**；真值靠逐单元口径。

## 6.5 ⛔ 长指令一律落文件 + 短指针（2026-09-28 实测两次踩坑）

**规则（操作者 2026-09-28 当面定）：给 opencode 小弟发话，首字符不能是 `$` / `!` / `/`——否则整行被当命令行执行，模型一个字都收不到。**

⛔ **强化（实测三种前缀全灭）：首字符带任何符号（`$` `!` `/` `` ` `` `>` `*`）一律不发；正文里也清掉 `!` `#` `` ` `` `**` 与 glob。**
三种前缀都真踩过：正文开头的 `!`（引 PR 号）、`$`（我以为的「安全写法」）、`/`（我以为的 slash 命令）——渲染出来一律是 `$ <正文>` + `zsh: …` + `Command exited with code 1/127`，**一条都没进模型**。
`#` 是同一类雷且**位置无关**：正文任何位置出现 `#123`，zsh 解析到就报 `unknown file attribute: #` 并把整条吃掉。
⇒ **唯一可靠配方：纯自然语言中文指令，首字符是普通汉字，正文不出现 `!` `#` `` ` `` `*` `$`**（要指代 PR/issue 就写「PR 编号 123」「issue 编号 456」）。实测纯中文指令连发三次全部进模型，带前缀的全灭。
⇒ **「核模式行」降为第二道保险，不是放行许可**：我有一轮核到 `Build` 仍被吃掉——模式会在两次 send 之间自己翻，而我漏核了第二次（只核了「有没有在跑」）。**顺序：先把正文写成不可能触发的形状，再核模式行。**

⚠️ **但「首字符是 `$`/`!` 才出事」这个归因不完整（2026-09-29 实测）**：被执行的正文里确实出现过 `!NNN`，
但同日晚被执行的几条**以中文开头、含 `#`**，真正原因是 **TUI 处于 shell 模式**（输入框模式行显示 `Shell`）。
⇒ **shell 模式下任何文本都会被当命令跑，与首字符无关**；主判据永远是**模式行**（见上面 shell 模式那一节），
发前核一次、发后核 token 增量。
⛔ **已证实（2026-09-29 三次实测）：`!` 就是 shell 模式开关，与首字符无关**——从 `Build` 模式起打一段含 `!447` 的正文，**敲到 `!` 那一刻模式行当场变 `Shell`**（实测原文：`… 开评审（审 PR !447 …）`，`!` 一到，模式行由 `Build` 变 `Shell`），于是这条消息**永远进不了模型**：Enter 被 shell 消费、输入框清空、**token 数不动**。
⇒ **正文里禁用 `!`**；要指代 PR / issue 写「PR 编号 447」「issue 编号 368」。
⇒ 但**字符不是门禁**：判据永远是**发字前 + 入 Enter 前**各核一次**模式行**是 `Build` 还是 `Shell`（模式会在两次发送之间自己变——小弟跑过 shell 命令就留在 shell 模式）；`#` 同理（行首会被渲染成 `$ <正文>`）。
⇒ **发完核 token 增量**：数字不动 = 没送达，必须重发（不是「已排队」）。

**现象**：500+ 字的裁决直接 `send-keys` 进输入框，屏幕上看着像「已提交」，实际被 zsh 执行（报 `no matches found` 或退出码 127/1），白等一轮；`**` 还会触发 zsh glob。

**规矩**：
1. 超过一两句话的指令 → 先写文件（如 `.briefs/<task>-ruling.md`），再 `send-keys` 一句指针：`裁决写在 .briefs/xxx.md，读它照做。`
2. 指令全文避开 `!` `$` `**` 与换行。
3. **送达必须核，不许假设**：导出 `GET /api/experimental/session/<sid>/export`，看最后一条非 assistant 条目的 `type` ——
   - `type=user` ⇒ 真送达模型；
   - `type=shell` + `exit 127/1` ⇒ 被当 shell 命令跑了，没送达，改短或落文件重发。

### 6.6 换模型：别在 /models 面板里较劲，用服务端 API 切（2026-09-28 实测）

`/models` 面板在 tmux 里把文本送进去很不可靠（实测：BSpace 清空搜索词后面板自己关了、文字落进了 prompt 框、模型没切）。**可靠的改法**：

1. 先发一条无意义短消息（如「回一句就绪，先不要做任何事。」）把会话建出来；
2. 取会话 id（`GET /api/session`，按 `time.updated` 排序取最新）；
3. `POST /api/session/<sid>/model`，body：`{"model":{"id":"<modelID>","providerID":"<providerID>"}}`，期望 `204`；
4. 核屏底 `Build · <模型名>` 与 `GET /api/session/<sid>/model` 两边都对上。

⛔ **切模型必须在轮次之间（屏底无 `esc interrupt`）**：实测在小弟正跑着时切（会话刚建、还没派活的除外），当前轮直接 `Error: Provider request failed with HTTP 400`（新 provider 对旧模型写的历史不兼容），一轮白跑（它交工时哪怕改动未提交，先核工作树再重派）。正确节拍：**起会话 → 确认空闲 → 立即切模型 → 再派活**；已污染历史的会话若持续 400，另开新会话（状态都在磁盘上，靠 brief 接着干）。

**服务地址与凭据（先取对，别猜）**：`URL=$(opencode service status | tr -d '[:space:]')`（实测 `http://127.0.0.1:49374`）、`-u "opencode:$PW"`，`PW` 取自 `~/.config/opencode/service.json` 的 `password`（只在 shell 变量里传递、不打印）。
⛔ **别猜端口**：猜 `4096` 只会拿到空响应 + JSON 解析失败，白烧好几轮（2026-09-28 实测）；拿不准就用 `lsof -nP -iTCP -sTCP:LISTEN | grep opencode` 核。

可用的模型清单：`GET /api/model`（带 providerID）。

**现行默认模型（操作者 2026-09-28 定）：开 opencode 任务一律用 `opencode-go` / `deepseek-v4.1-flash`**——
免费模型（`space-bunny-free` 等）太慢，不再作默认。**评审线也用这一条**（操作者明确要求统一）。
⇒ 后果要如实记账：作者与评审同一模型 ⇒ 评审结论**按「同模型自评」标注**，**不得谎称独立门禁**；
要真独立门禁才换异模型（如 `opencode-go` / `gpt-6-luna`、`mimo-v2.6-pro`），换模型前先问一句。

⛔ **默认模型改不了 API**：`POST /api/model/default` 实测返回 `404`（该端点只有读）。
⇒ **但可以改 opencode 的全局配置（2026-09-28 实测，已就位）**：`~/.config/opencode/opencode.json` 里加
`"model": "opencode-go/deepseek-v4.1-flash"`（先备份原文件），重启 TUI 后屏底即 `Build · DeepSeek V4.1 Flash OpenCode Go`
—— 新会话**默认就是对的**，不必再每次手工切。改配置后**必须用屏底核实**，别只看文件写对了。

保留节拍（配置未生效 / 要临时换模型时）：**起会话 → 发一句建出会话 → 确认屏底无 `esc interrupt` → `POST /api/session/<sid>/model` 切到本单模型 → 再派活**。
（会话 id 在**发出首条消息之后**才出现在 `GET /api/session` 里；按 `location.directory` 过滤、取 `time.created` 最新的一条。）
（新会话建出来时的 `title` 就是我那句建会话的话，别把它当任务名。）

## 7. 探针任务怎么写 + 收尾必查

**探针有模式命中上限（默认 8 次）**：吃到上限后**静默退化成「仅进程退出时通知」**——轮次结束不再报，看起来「在跑」实则瞎了。发现办法：收到「Watch patterns disabled … lifetime cap」提示。处置：**杀掉旧进程，用同 anchor 起一个新进程**（新进程 = 新配额），并用 `process_manage poll` 核头几行有 `ANCHOR-OK`；`BACKFILL-DONE` 出现表示它已把上一轮回看掉、正在盯下一轮。长跑阶段主动数剩余配额，别等退化。

- 在 **scratch 目录**跑探针（业务工作树里会让它去动真文件）。
- 长任务用固定列表（`for i in 1 2 3 …`），别用 `$(seq …)`（折行污染，见 `tmux-cursor-agent` §2.2）。
- **⛔ SSE 长连接会漏杀**：`terminal(background=true)` 报「进程已退出」**不等于 curl 真退了**——
  实测探针跑完报退出，`ps` 里那个流进程仍在跑。
  ⇒ 收尾一律 `ps` 按 pid 核；`kill -9` 后再 `ps -p <pid>` 确认。别用 `pgrep -f curl`（会匹到自己）。
- SSE 探针正常退出码是 curl 的 `28`（`--max-time` 到点），**不是故障**；
  被 `kill -9` 则是 `137`，也不是故障。两种都别当错误报。
- **⛔ 清场顺序（opencode v2 后台执行，2026-09-28 定）**：① `Esc`×2 掐轮（屏底 `esc again to interrupt` 为凭）
  → ② `tmux kill-session` → ③ 核服务端 `GET /api/session/active` 该 id **已不在**（这才是真停）。
  **杀窗口 ≠ 停止执行**；`C-c` 不是掐轮键（只把 TUI 退回 shell）。杀完再 `ps aux | grep <树名>` 核残留（**别把 Hermes 自己的 transient bash 包装进程当成残留**）。

## 2.9 ⛔ 探针会无声消失：常驻监控必须「脱离式 + 守夜兜底」（2026-09-29 实测）

三个真账（同一天全踩）+ 一条投递时序（见下第 4 条）：

1. **Hermes 后台句柄会被回收 ⇒ 探针子进程跟着死**。`terminal(background=true, watch_patterns=…)` 起的探针，事后 `process_manage(action='log')` 报 `not_found`、`ps` 里也没了 —— 台面上看着"挂着"，其实是空的。**别再假设「我挂过就一定还在」**；汇报前先 `pgrep -fl 'watch\.py ses_'` 复核。
2. **macOS 没有 `setsid`**（`setsid: command not found`）→ 脱离式重挂只能用 `nohup … &`。写进脚本里没问题；直接在 Hermes 工具命令里写 nohup 会被工具拒（"uses shell-level background wrappers"）。
3. `set -u` 下多字节字符紧跟变量名会被当成变量名的一部分：`$sess（` ⇒ `sess\xef: unbound variable`。**变量后接中文括号一律写 `${sess}（`**。
4. **通知会滞后于现实：已 kill 的探针仍在投递它生前缓存的 `STAGE-DONE`**。收口一单后（kill 会话 + pkill 探针 + 删 registry 行）仍陆续收到该会话的数条 `STAGE-DONE`，`end_ts` 全部落在**更早的时刻**（缓冲回放，句柄已退出）。
   ⇒ 收到通知先做两件事再动手：① 比对事件里的 `end_ts` 是否落在**当前这次派活之后**（旧事件只记账、⛔ 不触发任何动作）；② `ps`/`tmux ls` 核该会话与探针是否还在。
   ⇒ **「通知到达」≠「现在发生了什么」**——通知负责叫我，屏/ps 负责现在的态（与 §3.5「处置前先核屏」同源）。已收口的单收到它的终态通知时，正确动作是**什么都不做**。

现行做法（照抄即可，件在持久目录，不放 scratch——scratch 24h 会被清）：

- **两条腿，缺一不可**：
  - **投递腿 = Hermes 跟踪起**：`terminal(background=true, watch_patterns=[…])` 起探针 —— 只有这样事件才会**回到会话里**（收到 STAGE-DONE/SCREEN-QUESTION/SESSION-FAILED 通知）。
  - **存活腿 = 守夜兜底**：`~/.hermes/profiles/<profile>/scripts/probe-watchdog.sh` + 注册表 `registry.tsv`（列 = `tmux会话名 <TAB> opencode会话id <TAB> expect-dir <TAB> 备注`；tmux 名写 `-` 表示「无窗口，只兜底探针存活」）。cron `probe-watchdog`（10m · no_agent）发现该 sid 没有 watch.py 进程就 `nohup` 重挂一个**脱离式**的 + 发 macOS 通知。
- ⛔ **只挂脱离式（nohup/setsid）= 假监控**：进程活着但输出只落日志文件，Hermes 侧永远收不到事件 —— 2026-09-29 操作者当场抓出这个错（"你没有挂上监控"）。**脱离式只能当兜底，不能当主通道。**
- 注册表与窗口同生共死：窗口关了 ⇒ 删该行 + kill 掉孤儿探针（寿命绑窗口，不绑一轮任务）。
- 汇报「监控在」之前，先跑一次 `bash ~/.hermes/profiles/<profile>/scripts/probe-watchdog.sh --verbose` + `pgrep -fl 'watch\.py ses_'`，用输出说话，别等操作者提醒。

## 2.10 question 面板（AskUserQuestion）怎么答（2026-09-29 实测配方）

小弟**真的**在请示时，屏底是选项列表：

```
┃  Questions
┃  <它的问题>
┃  1. A. …… （推荐）
┃  2. B. ……
┃  3. C. ……
┃  4. Type your own answer
┃  ↑↓ select  enter submit  esc dismiss
```

**先判真伪**（`SCREEN-QUESTION` 会假阳性）：① 屏底是不是真在等人（不是 `Thinking` / `Writing…`）；② 只读查该会话最近消息有没有 `AskUserQuestion`。两条都成立才是真请示。

**选中项怎么核**（不要凭感觉按 Down）：
- **question 面板**：被选中那一行独有 `\x1b[48;2;10;10;10m`（**深底**）+ 前色 `38;2;250;178;131`；其他行没有。
- **permission 面板**是**反的**：选中行底色 `48;2;250;178;131`（**橙底**）+ 字色 `38;2;10;10;10`。两套别搞混。
- 核法：`tmux capture-pane -p -e -t <sess> > /tmp/p.txt`，再按上面的色码 grep 定位行号，确认落在你要的那一项上。

**⛔ 不许 `esc dismiss`**：退出=不选，TUI 会把**首项（常是它的「推荐」）**当默认执行 —— 等于替操作者拍了板（曾实测致 13 张现行证据被误移）。要么正确选一项，要么走「Type your own answer」。

**走自定义文本（要下裁定/给长指令时）**：
```bash
# 1) 显式下移到 "Type your own answer"（末项），并核高亮色（见上）
tmux send-keys -t <sess> Down   # 重复到末项
# 2) 提交该项 → 提示行由 "↑↓ select  enter submit  esc dismiss" 变为 "enter submit  esc close"
tmux send-keys -t <sess> Enter
# 3) 贴长文本：⛔ 别用 send-keys -l 直接打长中文（会被 TUI 折行/截断），走 buffer
tmux load-buffer -b ans /tmp/ans.txt && tmux paste-buffer -b ans -t <sess>
# 4) 单独一次 Enter 提交（与贴文本分两次调用，否则 Enter 会被吞）
tmux send-keys -t <sess> Enter
# 5) 复核：屏底转 Thinking/Working，且输入框已空
```
裁定文本一次写清（目标 + 必须成立什么 + 边界 + 下一步），因为面板答一次就关，追加要多花一轮。

## 相关

- `tmux-cursor-agent` — Cursor 版运行时手册；共享「折行污染」「Busy/Ready 决定落点」等通用坑
- `cto-delegation-protocol` — 派活判据与验收门禁
- `cursor-hook-monitor` — Cursor hook 监控技能包（OpenCode 不需要，SSE 覆盖）
