# 双层 tmux 监控（Python per-group）

## 架构

```
cursor_monitor.py group-create / add / remove
  → ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.state
  → cursor_monitor.py daemon --group <group>（15s 轮询，Hermes background + watch_patterns）
  → cursor_watch.py（working→stopped + reason）
  → CURSOR-STOPPED:<group>:<session>:<window>:<reason>
```

团队多任务：每 `task_id` 一个 group + 一个 daemon。见 [huichang-team](../../huichang-team/SKILL.md)。

## 快速启动（单 group）

```bash
export CURSOR_SKILL="$HOME/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate"
export MON="python3 $CURSOR_SKILL/scripts/cursor_monitor.py"
GROUP=default

$MON group-create "$GROUP" --label "主监控"
$MON add --group "$GROUP" cursor 3 --label "股性聚类"

terminal(
  command="exec python3 \"$CURSOR_SKILL/scripts/cursor_monitor.py\" daemon --group ${GROUP}",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
process(action='list')
```

## 检查

```bash
$MON list --group "$GROUP"
$MON status --group "$GROUP"
```

## 文件

| 路径 | 用途 |
|------|------|
| `~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.state` | 该 group 的 monitor 列表 |
| `~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.daemon` | daemon pid 元数据 |
| `~/.hermes/team-tasks/<id>.json` | 团队任务台账（持久） |

旧版 `~/.hermes/cursor-monitors.json` 已废弃。

## 故障

- daemon 崩溃：`status --group` 检查，重启 daemon
- 详见 `python-monitor-cli.md`、`monitoring-startup-verification.md`
