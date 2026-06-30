# Cursor UI 校准 Fixture

空沙箱 `/tmp/cursor-calibrate-sandbox` 逐步交互抓取，停稳再发下一条。

## 回归

```bash
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/test-cursor-watch-fixtures.sh
```

## 重新抓取

```bash
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh all
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-plan-question.sh   # 单独抓 Question 多选
```

## 关键 STOPPED 界面

| Fixture | 界面 |
|---------|------|
| `plan-stopped-S02-question` | Question 1 of N 多选框 |
| `plan-stopped-S05-ready-to-build` | Ready to build? |

## EXECUTING 白名单

见 `cursor_watch.py` / `cursor-watch-lib.sh`：`is_executing()` — Braille spinner / 状态词 / background task
