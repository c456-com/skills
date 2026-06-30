# 读窗指南：不用脚本如何判断 Cursor 状态

> 调用本技能时，用 `tmux capture-pane -t <session>:<window> -p -S -15` 看最后约 15 行即可。**不必跑 `cursor_watch.py`**，按本文规则人工判断。  
> **读完一轮任务输出**（计划、relay）时用 [`cursor_read.py`](../scripts/cursor_read.py) 按任务自判 `--lines N`；见 [`huichang-team/references/adaptive-pane-reading.md`](../../huichang-team/references/adaptive-pane-reading.md)。

## 读哪里

```
┌─ 对话正文（历史消息、工具输出、表格）────────────┐
│  你之前发的消息会出现在这里（无 → 前缀）          │
│  agent 的回复、Read/Edited 工具行也在这一区        │
├─ 交互区（可选）──────────────────────────────────┤
│  Question 框 / Ready to build / 命令批准         │
├─ 活动行（可选）──────────────────────────────────┤
│  ⠘⠤ Working  /  Waiting for shell  /  1 background task │
├─ 输入框（底栏）──────────────────────────────────┤
│  → Add a follow-up   或   → 你未提交的文字         │
├─ 状态栏（最底）──────────────────────────────────┤
│  Auto · 45% · 3 files    Run Everything           │
│  ~/path/to/project · branch                       │
└──────────────────────────────────────────────────┘
```

**优先看：最底 10 行**（活动行 + 输入框 + 状态栏）。

---

## 一、运行状态：EXECUTING 还是 STOPPED

**问题：agent 此刻是否在干活？**

### EXECUTING（正在执行 — 不要发新消息）

底部 **任一** 出现即判为 EXECUTING：

| 信号 | 示例 |
|------|------|
| Braille 动画点 | `⠠⠛` `⠘⠤` `⠀⠞` 等 + 状态词 |
| 状态词 | `Working` `Running` `Thinking` `Reading` `Globbing` `Editing` `Waiting` `Reconnecting` |
| 后台任务 | `1 background task` / `2 background tasks` |
| 等 shell | `Waiting 4m 23s for shell`（常与 background task 同现） |

**注意：** `Waited 15s` 是**过去式**工具结果，不是 EXECUTING。

### STOPPED（未在执行 — 可关注、可择机发消息）

**没有**上述 EXECUTING 信号 → STOPPED。

STOPPED **不等于**「任务完成」或「可以不管」，只表示**当前没有活动执行**。还需看下一节「交互状态」和「输入框」。

### 绝不能当 EXECUTING 判据的

| 显示 | 实际 |
|------|------|
| `→ Add a follow-up` | 输入 placeholder，与是否在执行无关 |
| `Run Everything` | 全自动批准已开 |
| `Auto · 45%` / `Plan · 13%` | 模式 + 上下文占用，**不是进度** |
| `ctrl+o to expand` / `ctrl+b twice` | 热键提示 |

---

## 二、输入框状态：能不能发、会不会叠字

**问题：现在往输入框打字安全吗？输入框里有没有上次没发出去的字？**

### 输入为空（可以开始四步法发消息）

底栏 **只有** placeholder，没有你自己的文字：

| placeholder 文案 | 模式 |
|------------------|------|
| `→ Add a follow-up` | Auto / Ask / Debug 等 |
| `→ … /plan to review and build` | Plan |
| `→ Describe how to revise the plan...` | Plan 待修订 |

判断：**`→` 后面是固定提示语，不是你的句子** → 输入为空。

### 输入有残留（必须先处理，禁止直接叠发）

| 现象 | 含义 |
|------|------|
| `→ 阅读 /tmp/prompt.md` | 你的文字还在输入框，**未提交** |
| `→ 场景 plan-question：...` | 同上 |
| 底栏上方还有一行「待输入」但不在对话历史里 | 残留 |

**处理：** `Escape` 清空 → 再 capture 确认只剩 placeholder。不要用 Ctrl+C 清框。

### 消息在 follow-ups 队列（不是输入框，但也不能当正常对话）

```
┌─ follow-ups ─────────────────────────┐
│○ 你的第二条消息 · enter send now      │
└──────────────────────────────────────┘
```

说明之前连发过消息，**排队未处理**。不要继续 send-keys；等 agent STOPPED 且输入框干净后再发。

### 发之后：怎么确认「已发出」

| 现象 | 结论 |
|------|------|
| 你的文字出现在**对话正文区**（历史中），且常伴随 `Working`/spinner | ✅ 已发出 |
| 文字仍在底栏 `→ 你的字...`，未进历史 | ❌ 未提交，再 sleep 2 + Enter |
| capture 里完全看不到刚发的字 | ❌ 未送到，检查 session:window |

---

## 三、交互状态：STOPPED 时在等什么（发消息前/后都要看）

在已 STOPPED 的前提下，看**正文与交互区**：

| 界面 | 含义 | 你该做什么 |
|------|------|------------|
| `Question N of M` + `› [ ]` 选项 | Plan 多选问题 | ↑↓ + Space + Enter，**禁止输数字** |
| `Ready to build?` + 1/2/3 选项 | 计划待确认 | 选 build 或 propose changes |
| `Run this command?` + `Run (once) (y)` | 需批准命令 | 评估后 `y`+Enter 或请示辉哥 |
| `Press Ctrl+C again to exit` | 误触 C-c | **一次** Enter = 不退出，恢复正常 |
| 仅 placeholder，正文像汇报收尾 | 可能任务完成 | 验收后汇报或发下一条指令 |
| 仅 placeholder，无特殊框 | 空闲 | 可按四步法发新指令 |

---

## 四、模式标志（底栏状态行）

| 显示 | 模式 | 发消息注意 |
|------|------|------------|
| `Auto` | 默认，可读写执行 | 常规四步法 |
| `Plan` | 只出计划 | 易出 Question / Ready to build |
| `Ask` | 只读问答 | 不会改文件；拒执行 shell |
| `Debug` | 调试 | 可跑测试、改代码 |

模式标志 **不表示** EXECUTING 或 STOPPED。

---

## 五、发消息决策清单（给 AI 逐步执行）

```
1. tmux capture-pane -t <session>:<N> -p -S -15

2. 是 EXECUTING？
   有 spinner / Working|Reading|… / background task → 停，不要发

3. 输入框干净？
   仅 placeholder → 继续
   → 后有你的字 / follow-ups 框 → Escape 或先清队列，再 capture

4. 特殊交互？
   Question / 批准 / Ctrl+C 退出态 → 先处理交互，不要塞新任务

5. 四步法：send 内容 → sleep 2 → Enter → capture 确认已发出

6. 发后仍是 STOPPED 且无 Working？
   检查是否未提交（→ 前缀）或进了 follow-ups
```

---

## 六、与监控脚本的关系

| | 人工读窗（本文） | `cursor_watch.py` |
|--|------------------|-------------------|
| 用途 | 发消息前/后、Telegram 当场判断 | daemon 自动轮询、CURSOR-STOPPED 通知 |
| EXECUTING 规则 | 同上白名单 | 同 `cursor-watch-lib.sh` |
| 输入框 | **本文专讲** | STOPPED 时若 `→` 后有用户草稿 → **抑制通知**（`user_draft`） |

维护脚本规则见 [`monitoring-detection.md`](monitoring-detection.md)；fixture 见 [`ui-calibration.md`](ui-calibration.md)。
