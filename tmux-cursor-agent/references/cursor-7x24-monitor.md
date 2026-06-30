# 7×24 Cursor Agent 监控

```
~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.state
  → cursor_monitor.py daemon --group <group>（15s，background + watch_patterns）
  → cursor_watch.py（每窗口）
  → CURSOR-STOPPED:<group>:<session>:<window>:<reason>
```

## 注册窗口

```bash
export MON="python3 ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/cursor_monitor.py"
$MON group-create default --label "7x24"
$MON add --group default cursor 3 --label "my-task"

terminal(
  command="exec python3 \"$HOME/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/cursor_monitor.py\" daemon --group default",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
```

详见 `python-monitor-cli.md`。
