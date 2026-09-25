---
name: cursor-hook-monitor
description: "Cursor Agent hook 监控 / cursor-agent hook monitor：当用户要精准判断 tmux 中 cursor-agent 哪一轮对话结束、发现屏幕轮询漏报或误报空闲、给已在跑的 cursor-agent 补装 hook 接管、并行多个 cursor-agent 按会话归因，或复盘对话时间线时触发；用于安装 hook 事件流（stop/afterAgentResponse）、用时间窗丢弃假空闲、输出 STAGE-DONE/QUESTION-PANEL 信号，作为 tmux-cursor-agent 屏幕轮询的补充。"
version: 1.0.0
author: Hermes Agent (hermes-cto)
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [cursor, cursor-agent, hook, monitoring, tmux, orchestration, xiaohui]
    category: xiaohui
    related_skills: [tmux-cursor-agent, cto-delegation-protocol]
---

# Cursor Agent 对话结束监控（hook 补充信号）

## When to Use

- 派任务给 tmux 里的 cursor-agent，**且要精准知道它哪一轮说完**（而非靠盯屏幕）
- 发现现有屏幕轮询**漏报或误报**对话结束（长任务中途误报空闲、请示门卡死没被察觉）
- 需要**事后复盘**整场对话的时间线（每轮起止、时长、工具调用）
- 一个项目**并行多个 cursor-agent**，需要按会话分开归因
- 接手一个**已在跑但没监控**的 cursor-agent，想给它补上能力

## 定位：补充，不是替换

`tmux-cursor-agent` 技能的屏幕轮询（pane title + 屏底状态行 + git HEAD）是主信号，
本技能的 hook 事件流是**第二路独立信号**。两路物理独立、互相补位：

| 失效模式 | 谁能看见 |
|---------|---------|
| 对话已结束但屏幕无可见变化（零提交的报告/评论类交付） | hook |
| 请示门 `Question N of M` 静默卡死 | 屏幕轮询（hook 在此**正确地不触发**） |
| 主代理已回 Ready 但子代理还在跑 | 屏幕轮询 |
| hook 忘 chmod / 未配置 → 静默失效 | 屏幕轮询 |

**hook 不覆盖"卡住"和"还在跑"**——实测请示门开着 25 秒，stop 一次都不触发。
所以屏幕轮询不能撤。

## 前置：版本与能力

实测环境：cursor-agent `2026.09.23-86fc751`，macOS。

CLI 正常交互模式（TUI，非 `--print`）下这些 hook **确实触发**：
`sessionStart` · `beforeSubmitPrompt` · `afterAgentResponse` · `stop` · `afterFileEdit`

旧报告（论坛 2026.01 / 2026.08）称 CLI 只发 shell 事件、不发 `stop`——**已过时**。
若换版本后 hook 不触发，先用 `scripts/probe.py` 复验，不要直接下结论。

## 接管已在跑的 agent（补装 hook）

已启动的进程**不会重载 hook 配置**——事后补写 `.cursor/hooks.json` 对它永远无效。
但退出再恢复是**新进程**，新进程会读新配置。所以接管路径成立：

```bash
python3 <skill>/scripts/adopt.py <worktree_path> <tmux_session> [--conv-id <id>]
```

它做四件事：拿 conv_id → `/exit` → 装 hook + chmod → 用同一 ID 恢复。

实测结论（cursor-agent 2026.09.23-86fc751）：

- 恢复后**上下文完整带回**：标题、工具记录、文件编辑痕迹都在
- 恢复后的新进程 **hook 正常触发**（实测 9.34s 一轮完整捕获）
- pane 里**看不到** conversation_id，不能靠肉眼找
- `cursor-agent ls` 需要真 TTY，脚本里不可用（报 Ink raw mode 错）
  ⇒ 用 cwd 反查 `~/.cursor/chats/*/*/meta.json` 的 `cwd` 字段

**接管前必须确认 agent 已在 `✅ Ready`**，不能中途接管（脚本会拒绝并报错）。
中途退出会打断正在跑的工具调用。

⚠️ 接管会重建进程，`CURSOR_MONITOR_LOG_DIR` 以接管时传入的值为准；
改脚本默认值不影响已接管的会话，重接管即可换路径。

接管后**先发一轮秒回任务冒烟**，确认事件流真的产生行，再挂 watch 探针。

## 日志落位

默认落 `$TMPDIR/cursor-hook-monitor/logs`（Hermes scratch），**不落技能目录**——
落技能目录会污染技能、随技能分发跑到别的机器上，且技能目录常为只读。
可用 `CURSOR_MONITOR_LOG_DIR` 覆盖。start.py / adopt.py / watch.py 三者需用同一路径。

## 用法（三步）

### 1. 启动（拿到会话身份 + 装好 hook）

```bash
python3 <skill>/scripts/start.py <worktree_path> <tmux_session> [初始prompt]
```

它按顺序做四件事，**顺序不能改**：
1. `cursor-agent create-chat` 预分配 conversation_id → 提前知道会话身份
2. hook 装进该工作树 `.cursor/hooks.json`（+ `chmod +x`）
3. 用 `CURSOR_MONITOR_TAG=<conv_id> --resume=<conv_id>` 启动 TUI
   ⇒ tag / 会话身份 / 事件文件三者同一个 ID
4. 冒烟确认 TUI 进入输入框

输出 `CONV=` / `SESSION=` / `EVENTS=` 三行供后续使用。

### 2. 挂监控（**必须由 Hermes 托管**）

```bash
terminal(command="python3 <skill>/scripts/watch.py <CONV> <timeout_s> --tmux-session <SESSION>",
         background=true, notify_on_complete=true)
```

**绝不能用 `subprocess.Popen` 起探针**——Hermes 不托管那个进程，
它退出时不产生通知，Hermes 永远叫不醒（实测踩过）。

用 `notify_on_complete` 而非 `watch_patterns`：后者有 8 次投递上限
（`WATCH_LIFETIME_MAX_HITS`）+ 15s 冷却 3 次熔断 + 全局 15/10s 限流，
多 agent 并行必然踩到，之后静默退化成"进程退出才通知"。

### 3. 判读

探针只读 `<log_dir>/<conversation_id>.jsonc`，按优先级输出三类信号之一后退出：

| 输出 | 含义 | 处置 |
|------|------|------|
| `STAGE-DONE` | 本轮结束，附 start_ts / end_ts / duration | 独立验证 → 下一阶段或收口 |
| `QUESTION-PANEL` | 卡在请示门等裁决 | 立即裁决（见下） |
| `IDLE-FALLBACK` | 无 stop 事件且持续空闲 30s | hook 疑似未触发，降级回纯轮询 |
| `WATCH-TIMEOUT` | 到期未见 stop | 核当前状态，必要时重挂探针 |

## 时间窗：怎么丢弃轮询假空闲

事件流里每行带 `round_start_at`（本轮 beforeSubmitPrompt 的 ts）与 `round_open`：

- `round_open=true`  → 这一轮还在跑，**屏幕轮询的空闲判据一律丢弃**
- `round_open=false` → 窗口已关，轮询结果才有意义

效果：**一轮只唤醒 Hermes 一次**。长任务 30 秒内轮询看到多次空闲，全被时间窗吸收，
不产生额外 token。

## 五条硬约束（都是实测踩出来的，违反即静默失效）

1. **hook 必须在 TUI 启动前落盘。** 长驻进程不重载 hook 配置，事后补配对该会话永远无效。
2. **hook 脚本必须 `chmod +x`。** 漏了 Cursor 不会报错，agent 照跑、屏幕一切正常，
   但日志一行不写——最阴的失效。`start.py` 已内置 chmod，装完仍建议发一轮秒回任务冒烟验证。
3. **hook 进程内只追加即退。** 它阻塞 agent 轮次，禁止跑测试/git/网络。
4. **解析失败必须 fail-open。** 报错但绝不阻塞 agent。
5. **绝不能用前台调用跑探针。** 前台 600 秒上限会改道；`execute_code` 里的前台
   `terminal()` 拿不到完成通知。

## 判据不能只看"最后一行"

`stop` 与 `afterAgentResponse` **到达顺序不固定，且可能同一秒内到达**（两个方向都实测到）。
若按"最后一行是不是 stop"判断，采样落在两者之间就会漏判本轮已结束，
再叠加兜底分支就会在长任务中途误报空闲。

正确判据：**本轮是否出现过 stop**（扫全部行、按 `generation_id` 去重）。
`watch.py` 已按此实现。

## 请示门处置

hook 在此场景正确地不触发，只有屏幕能看见。捕获到后面板底部提示行是
`↑/↓ option · ←/→ question · Space select · Enter next/submit · Esc to skip`。

标准动作：
1. `tmux capture-pane -p -t <session>:0 -S -400` 翻出完整题面（`-S -40` 常只够最后一问）
2. 用 `Left/Right` 翻看每一问，**不要只答第一问**
3. **首选** `Esc` 退出面板 → 输入框发一行指针，而不是在面板里逐题点选
   （面板里 `Enter` 提交经常不生效，反复试键会耗时间并可能重置已勾选项）

## 多 agent 同项目

每个会话用独立 conversation_id 作 tag（`start.py` 自动如此），
事件流天然按 `<conversation_id>.jsonc` 分开，不串味。

实测：同目录两个 agent 交错执行，一个 30s 长任务、一个秒回，
各自事件流独立，`conversation_id` 互不相同，零交叉。

## 事后观测

`<conversation_id>.jsonc` 保留整场对话的事件时间线，可直接复盘：

```
11:55:58  beforeSubmitPrompt
11:56:28  stop              ← 轮起点 11:55:58
11:56:28  afterAgentResponse ← 轮起点 11:55:58
11:57:49  beforeSubmitPrompt  ← 轮起点 11:57:49
11:58:19  afterAgentResponse  ← 轮起点 11:57:49
11:58:19  stop               ← 轮起点 11:57:49
```

用 `scripts/timeline.py <log_dir> <conversation_id>` 渲染成可读时间线。

## 相关

- `tmux-cursor-agent` — 屏幕轮询、四步发送协议、队列/steer 语义（本技能是它的补充）
- `cto-delegation-protocol` — 派活判据与验收门禁
