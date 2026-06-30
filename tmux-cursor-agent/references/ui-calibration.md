# UI 校准：Cursor Agent 状态检测 fixture

> 实现代码在技能目录 `cursor-agent-delegate/scripts/` 与 `fixtures/calibrate/`。

## 何时需要重跑校准

- Cursor CLI 升级后 UI 文案/布局变化
- `test-cursor-watch-fixtures.sh` 失败
- 新增 reason 类型（如 `needs_approval`）需补 fixture

## 沙箱（禁止用真实项目）

```bash
# 目录由 calibrate-cursor-states.sh boot 使用
/tmp/cursor-calibrate-sandbox/README.md
```

README 写明：只模拟、不改文件、不跑 shell。**绝不在 huichang-stock-picker 等业务仓库里抓 fixture。**

## 抓取纪律（v2 定稿）

```
停稳 4s（无 EXECUTING 信号）
  → 发一条 prompt
  → 若要抓 EXECUTING：等 spinner 出现再 capture
  → 等停稳再 capture STOPPED
  → 才能发下一条
```

**禁止**批量连发——消息会进 `follow-ups` 队列，抓到的不是真实 UI 态。

发 tmux 指令给生产窗口时同样：**先 `capture-pane` 确认不在 EXECUTING，再 send-keys**。

## 命令

```bash
# 全量（约 15–20 分钟）
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh all

# 分阶段
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh boot   # 含 Workspace Trust 按 a
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh auto
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh plan
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh ask
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh debug

# Plan Question 多选（单独一条 prompt，轮询 Question N of M）
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-plan-question.sh

# 回归
bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/test-cursor-watch-fixtures.sh
```

## Fixture 目录

```
~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/fixtures/calibrate/
├── *.txt              # capture-pane 快照
├── meta/*.json        # 抓取元数据
├── ground-truth.json  # 底部 10 行人工标注 executing|stopped
└── SUMMARY.md
```

更新检测逻辑后：**同步改 `cursor_watch.py` 与 `cursor-watch-lib.sh` → 跑 `test-cursor-watch-fixtures.sh` 回归 → 失败则重抓或改 ground-truth**。

## 必抓 STOPPED 界面（四模式）

| 界面 | 典型特征 | 参考 fixture |
|------|----------|--------------|
| 空闲 | 无 spinner，仅 placeholder | `auto-stopped-S01` |
| Question 多选 | `Question N of M`、`› [ ]` | `plan-stopped-S02-question` |
| Ready to build | `Ready to build?` + 选项 | `plan-stopped-S05-ready-to-build` |
| 命令批准 | `Run this command?` | 待补（需关 Run Everything） |

## EXECUTING 白名单

见 `monitoring-detection.md`。核心：**只正向识别**；`Add a follow-up`、`Run Everything`、模式标志均不是判据。

## 脚本一览

| 脚本 | 作用 |
|------|------|
| `cursor-watch-lib.sh` | `is_executing()` / `classify_reason()` |
| `cursor_watch.py` | 单窗口检测，输出 `CURSOR-STOPPED:` |
| `calibrate-capture.sh` | 单次 capture → fixture |
| `calibrate-cursor-states.sh` | 驱动沙箱逐步场景 |
| `calibrate-plan-question.sh` | 单独抓 Question 框 |
| `test-cursor-watch-fixtures.sh` | fixture 回归 |
