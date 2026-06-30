# 监控：Cursor Agent 工作状态检测

## 状态检测逻辑 (`cursor_watch.py`)

`cursor_watch.py` 通过分析 tmux pane 底部内容判断 agent 是否在**活动**（判据与 `cursor-watch-lib.sh` 一致，供 calibrate 使用）。

### 核心原则（勿误判 UI 占位符）

| UI 元素 | 实际含义 | 能否当空闲判据 |
|---------|----------|----------------|
| `→ Add a follow-up` | 输入框 **placeholder**（输入为空） | ❌ 不能 |
| `Describe how to revise the plan...` | Plan 模式输入 placeholder | ❌ 不能 |
| `Run Everything`（底栏） | 执行权限模式标志 | ❌ 不能 |
| Braille spinner / `Working` / `Running` | agent 正在活动 | ✅ 正向信号 |

### EXECUTING 检测（正向活动信号）

扫描 **输入框之上的 activity_region**（从 capture 顶部到 `→` 输入行 / `N task(s)` / `Auto ·` 底栏之前），**不再**仅用底部 10 行。Cursor UI 把 `Reading`/`Running`/spinner 放在输入框上方，底栏永远是 placeholder + 百分比，旧逻辑会误判 Dev 为 STOPPED。

满足 activity_region 任一即 EXECUTING：

```bash
# Braille spinner（完整 Unicode 盲文区 U+2800–U+28FF）
grep -qP '[\x{2800}-\x{28FF}]'

# 活动状态词（Waited 不匹配 Waiting）
grep -qE '(^|[[:space:]])(Working|Running|Thinking|Reading|Globbing|Editing|Waiting|Reconnecting)([[:space:]:]|$)'

# 后台 shell 轮询
grep -qE '[0-9]+ background tasks?'

# Dev 长任务监控输出（进度/elapsed）
grep -qE 'progress:[[:space:]]*[0-9]+/[0-9]+|elapsed=[0-9]|zone_accuracy progress'
```

**明确排除：** placeholder、`Run Everything`、`ctrl+o to expand`、`ctrl+b twice`、模式标志（Auto/Plan/Ask/Debug）

### STOPPED 检测

**未识别到 EXECUTING** → STOPPED。不靠 placeholder 判断。

实测 fixture 回归：`bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/test-cursor-watch-fixtures.sh`

校准抓取：`bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-cursor-states.sh all`（空沙箱 `/tmp/cursor-calibrate-sandbox`，停稳再发下一条）；Question 界面：`bash ~/.hermes/skills/autonomous-ai-agents/cursor-agent-delegate/scripts/calibrate-plan-question.sh`

### reason 分类（STOPPED 时附带）

在 STOPPED 且满足通知时机时，根据**正文内容**分类：

| reason | 检测特征 |
|--------|----------|
| `exited` | `Press Ctrl+C again to exit` |
| `needs_approval` | `Run this command?` / `Run (once) (y)` |
| `needs_input` | `Question N of M`、`Enter to submit, Esc to cancel`、正文「待你/请回复」等 |
| `task_done` | 正文「任务完成/已完成/All tests passed」等收尾语义 |

**⚠️ `needs_input` 误报**：window 刚进入 STOPPED（首次 boot、内容 hash 变化等）时也可能分类为 `needs_input`，即使没有实际交互要求。收到通知后必须 `capture-pane` 确认——仅当看到 Question 框、批准提示、或 agent 明确提问才处理。若窗口仅显示 placeholder 和已读正文，属于误报，忽略即可。
| `idle` | 以上都不匹配 |

### 通知时机

```
EXECUTING → 持续          → 静默
EXECUTING → STOPPED       → 输出 CURSOR-STOPPED（输入框须为空）
boot 且已 STOPPED         → 输出 CURSOR-STOPPED（输入框须为空）
STOPPED + 归一化 hash 变  → 输出 CURSOR-STOPPED（输入框须为空）
STOPPED 且无变化          → 静默
STOPPED + 输入框有草稿    → 静默（reason=user_draft，state=held）
held → STOPPED 且草稿清空 → 输出 CURSOR-STOPPED
```

**归一化 hash（`normalize_for_hash`）**：比较通知去重时对 pane 内容去掉易变行后再算 MD5，避免 Dev 跑着仅进度/百分比/spinner 帧变化就每 15s 刷 `CURSOR-STOPPED:idle`。剥离项包括：`progress: N/M`、`elapsed=`、`Auto · xx%`、`xx.xk tokens`、纯 braille 行、带时间戳的监控行。

### 输入框草稿（人在控制）

底部输入行 `→` 后若是**用户未提交文字**（非 `Add a follow-up` 等 placeholder），视为有人在控制窗口，**不触发** `CURSOR-STOPPED`，避免 Hermes 误以为任务完成。

| 底栏 | 判定 |
|------|------|
| `→ Add a follow-up` | placeholder，可通知 |
| `→ Add a follow-up — /plan to review and build` | placeholder，可通知 |
| `→ 阅读 /tmp/prompt.md` | 用户草稿，**抑制通知** |

## 监控 daemon (`cursor_monitor.py`)

### Hermes 进程管理跟踪（必须）

```bash
terminal(
  command="exec python3 \"$CURSOR_SKILL/scripts/cursor_monitor.py\" daemon --group <group>",
  background=true,
  watch_patterns=["CURSOR-STOPPED:"]
)
```

### 注册表与 daemon 的关系

`cursor_monitor.py` daemon 为长驻进程，**启动时加载** `cursor_watch`；修改 `cursor_watch.py` 后，daemon 会在每次 tick 通过 `importlib.reload` 自动加载新逻辑（无需手动重启）。若修改的是 `cursor_monitor.py` 本身，仍需重启 daemon。

### 迁移 session 后更新注册

把窗口从 `cursor:3` 迁移到 `cursor-dev:0` 后必须删除旧注册 `cursor:3`，添加新注册 `cursor-dev:0`。旧注册会产生误报。
