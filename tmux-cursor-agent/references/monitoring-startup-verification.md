# 监控守护进程启动验证与故障排查

> 场景：启动了 `cursor_monitor.py daemon`，但收不到 CURSOR-STOPPED 通知。

## 根因速查

| 症状 | 最可能原因 | 修复 |
|------|-----------|------|
| `ps aux` 能找到 daemon，但 `process(action='list')` 为空 | (1) daemon 裸启动未走 `terminal(background=true)`；(2) Hermes task_id 折叠导致 list 过滤 miss（装 `cursor-delegate-fix` 插件或改用 poll） | kill 旧进程 → terminal(background=true) 重启；验证用 `process(poll, session_id=...)` |
| agent 长时间未响应 STOPPED（daemon 在跑、日志有 CURSOR-STOPPED） | Gateway 空闲时不 drain watch 队列（CLI 有、Gateway 缺） | 装 `cursor-watch-idle` hook（`~/Codings/hermes/hooks/`）并重启 gateway |
| `process(action='poll', session_id="...")` 报 session 不存在 | 旧 session 已过期；或上一步 terminal 返回的 session_id 被忽略了 | 重新启动 daemon，记好返回的 session_id |
| daemon 在跑但几天没收到通知 | daemon 被杀或 group state 空 | `$MON list --group <group>` + 重启 daemon |
| agent 长时间未响应 STOPPED | Hermes 未处理通知，但 daemon 可能已发出 | `tail -f ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log` 或 `grep CURSOR-STOPPED` 查历史 |
| 收到 `CURSOR-STOPPED:needs_input` 但窗口只有 placeholder | 正常误报（idle hash 变化触发的重判），capture-pane 验证后跳过即可 | |

## 验证清单

每次启动 daemon 后，依次确认：

```bash
# 1. 确认 daemon 在 Hermes 进程管理中（poll 为准；list 为辅）
process(action='poll', session_id="<返回的 session_id>")
# 可选：process(action='list') — 若为空但 poll 正常，多为 task_id 过滤问题（非未注册）

# 2. 确认注册表有窗口
python3 "$CURSOR_SKILL/scripts/cursor_monitor.py" list --group <group>

# 3. 确认窗口实际在跑 cursor-agent
tmux display-message -p -t <session>:<window> '#{pane_current_command}'
# 应为 "cursor-agent"（不是 "zsh" 或 "bash"）

# 4. 确认双写日志（agent 未响应时排查）
tail -5 ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log
grep CURSOR-STOPPED ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log
```

## 根本原理

```
terminal(background=true, watch_patterns=["CURSOR-STOPPED:"])
  ├─ 注册到 Hermes 进程管理器 → process(action='list') 可查
  ├─ stdout 由 Hermes 持续监控 → 匹配 watch_patterns → 触发通知
  └─ 通知在当前会话注入（不论什么平台：CLI / Telegram / Discord 等）

裸 bash / tmux / cron 启动 daemon
  ├─ 操作系统进程（ps 能查到）
  ├─ stdout 不被 Hermes 监控
  └─ 永远不会触发 watch_patterns → 永远不会通知 agent
```

**关键区别：** `ps -p <PID>` 查到进程只说明操作系统层面活着。`process(action='poll')` 能查到才说明通知链路完整。

## 常见错误

| 错误做法 | 后果 |
|---------|------|
| 用 `ps -p <PID>` 替代 `process(action='poll')` 验证 | 看到 OS 进程就以为通知链路正常，实际收不到任何事件 |
| 用 `nohup` / `&` / `tmux send-keys` 启动 daemon | 不在 Hermes 进程管理中，通知链路缺失 |
| 旧 daemon 在跑就跳过重启 | 旧进程可能是不完整的启动方式，不验证就等于埋雷 |
| 启动时漏了 `watch_patterns=["CURSOR-STOPPED:"]` | daemon 在跑但不会触发通知 |
