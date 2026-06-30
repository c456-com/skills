# Python 监控 CLI（cursor_monitor.py）

> Phase 4 切流后正式路径。替代已删除的 `cursor-monitor.sh` / `cursor-monitor-daemon.sh` / `cursor-watch.sh`。

## 变量

```bash
export CURSOR_SKILL="$HOME/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate"
export MON="python3 $CURSOR_SKILL/scripts/cursor_monitor.py"
export TASKS="python3 $CURSOR_SKILL/scripts/team_tasks.py"
```

## 架构

- **运行时 state：** `~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.state` + `.daemon`（每 group 独立）
- **双写日志：** `~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log`（stdout 与日志**逐行相同**，行首 ISO8601 时间戳）
- **watch 状态：** `~/.hermes/logs/cursor-monitors/watch/cursor-watch-<session>-<window>.*`（每窗口 held/working 等）
- **持久台账：** `~/.hermes/team-tasks/<task_id>.json`（团队任务，见 huichang-team）
- **首次启动** 若 `/tmp` 仍有旧文件，会自动复制到上述目录（一次性）
- **废弃：** `~/.hermes/cursor-monitors.json`（旧全局注册表，不再使用）

## Group 与 daemon

每个监控组一个 `group_id`（团队任务 = `task_id`；单窗口委派可用 `default` 或项目名）。

```bash
$MON group-create mygroup --label "说明"
$MON add --group mygroup cursor 3 --label "股性聚类"
$MON list --group mygroup

terminal(
  command="exec python3 \"$CURSOR_SKILL/scripts/cursor_monitor.py\" daemon --group mygroup",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
```

## 通知格式

每行统一为 `<ISO8601> <payload>`（stdout 与日志文件内容一致）：

```
2026-06-24T09:15:00+08:00 CURSOR-MONITOR-START group=mygroup pid=12345 interval=15s
2026-06-24T09:15:15+08:00 CURSOR-MONITOR-TICK group=mygroup ok=2 skipped=0 total=2
2026-06-24T09:15:15+08:00 CURSOR-MONITOR-WATCH group=mygroup session=cursor:0 state=stopped reason=idle
2026-06-24T09:15:15+08:00 CURSOR-STOPPED:mygroup:cursor:0:idle
...（pane 正文附在 STOPPED 后，同样双写，不截断）
2026-06-24T09:25:15+08:00 CURSOR-MONITOR-STATUS:mygroup:monitors=2:ok=2:skipped=0:daemon_pid=12345
```

`watch_patterns` 仅匹配行内子串 `CURSOR-STOPPED:`（行首时间戳不影响匹配）。TICK/WATCH/SKIP 不会误唤醒 agent。

排查：`tail -f ~/.hermes/logs/cursor-monitors/cursor-monitors--<group>.log` 与 `process poll` 看到的主轨迹一致。

## 常用命令

```bash
$MON group-create <id> [--label L]
$MON group-remove <id>
$MON add --group <id> <session> <window> [--label L]
$MON remove --group <id> <target>          # target: id 或 session:window
$MON list [--group <id>]
$MON status --group <id>
$MON set-pending --group <id> <target> <reason> <summary>
$MON clear-pending --group <id> <target>
$MON daemon --group <id> [--debug] [--once] [--log-file /path/to.log]

$TASKS list [--status active,paused]
$TASKS create --task-id ID --label L --project PATH --pm-session S --dev-session S
$TASKS show|update|resume|pause|complete|abandon|activate --task-id ID

python3 "$CURSOR_SKILL/scripts/cursor_watch.py" <session> <window> [lines] [--debug]
python3 "$CURSOR_SKILL/scripts/cursor_read.py" capture <session> <window> --lines <N> [--offset <M>] [--out path]
bash "$CURSOR_SKILL/scripts/test-cursor-watch-fixtures.sh"
python3 "$CURSOR_SKILL/scripts/test_cursor_monitor.py"
```

## 环境变量

| 变量 | 默认 | 用途 |
|------|------|------|
| `CURSOR_MONITOR_INTERVAL` | 15 | daemon tick 间隔（秒） |
| `CURSOR_MONITOR_STATUS_INTERVAL` | 600 | STATUS 心跳间隔（秒） |
| `CURSOR_MONITOR_DIR` | `~/.hermes/logs/cursor-monitors` | state / daemon / 日志 / watch 根目录 |
| `CURSOR_MONITOR_LOG` | 见上（`<group>.log`） | 双写日志路径（覆盖默认） |
| `CURSOR_MONITOR_STATE_PREFIX` | （空） | state/log 文件名前缀（测试隔离时可设 `v2`） |
| `TEAM_TASKS_DIR` | `~/.hermes/team-tasks` | 台账目录 |

inline export 须在 `terminal(command=...)` 内，Hermes background 不继承 shell env。

## 校准 / fixture（开发用）

- `scripts/cursor-watch-lib.sh` — 仅 calibrate 脚本使用
- `scripts/test-cursor-watch-fixtures.sh` — 调用 `cursor_watch.py` 回归
