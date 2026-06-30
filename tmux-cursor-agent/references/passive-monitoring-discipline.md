# 被动等待纪律 — daemon 运行期间禁止主动 tmux 轮询

> 生效范围：当她使用 `terminal(background=true, watch_patterns=["CURSOR-STOPPED:"])` 启动 daemon 来监控 cursor agent 时，**不要主动盯屏**。

## 为什么不能主动轮询

1. **watch_patterns 的设计就是唤醒你** — daemon 检测到 `CURSOR-STOPPED:` 后自动注入你的对话。你已经有了通知机制，不需要自己盯。
2. **sleep+tmux capture-pane 循环违背被动检测架构** — 如果你在循环等 agent 停，说明你不信任 daemon。如果 daemon 有问题，你应该修 daemon，而不是绕过它。
3. **浪费 token 和注意力** — 每轮 capture-pane = 上下文消耗。你本可以同时处理其他任务。

## 正确做法

| # | 操作 |
|---|------|
| 1 | 四步法发消息给 cursor agent（capture-pane 确认已发出） |
| 2 | **立即停手**。不要 sleep，不要 capture-pane 窗口 |
| 3 | 等候 CURSOR-STOPPED 通知注入你的对话 |
| 4 | 收到通知 → capture-pane 一次确认 → 跑验收 shell → 继续下一轮 |

## 自检信号

如果你脑子里在算「sleep 15 秒再查一次」「再 poll 一下 daemon 看看有没有 STOPPED」——这是错的。不应该主动查，应该被通知。daemon 每 N 秒（`CURSOR_MONITOR_INTERVAL`，默认 15）轮询一次，你只要等。

## 唯一例外

超过 3 分钟无唤醒 → 允许**一次** `process(action='poll', session_id="<daemon_session_id>")` 看 daemon stdout；或 `tail -f ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log` 确认 daemon 仍在 TICK/WATCH（与 poll 内容一致）。仍然禁止 tmux capture-pane 循环。

## 相关环境变量

| 变量 | 默认 | 用途 |
|------|------|------|
| `CURSOR_MONITOR_INTERVAL` | 15 | tick 间隔（秒），控制轮询窗口的频率 |
| `CURSOR_MONITOR_STATUS_INTERVAL` | 600 | STATUS 心跳间隔，控制 `CURSOR-MONITOR-STATUS:` 行输出频率 |

必须在 `terminal(command=...)` 字符串内 inline export，因为 Hermes `background=true` 不继承调用者的 shell 环境变量。
