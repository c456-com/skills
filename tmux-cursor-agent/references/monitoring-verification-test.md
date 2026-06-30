# 监控链路验证测试

端到端验证 `cursor_monitor.py daemon` + `watch_patterns`：cursor agent 从 WORKING → STOPPED 时 Hermes 被 CURSOR-STOPPED 唤醒。

## 步骤

1. 创建 group 并 add 测试窗口
2. Hermes 内启动：
   ```text
   terminal(
     command="exec python3 \"$CURSOR_SKILL/scripts/cursor_monitor.py\" daemon --group <group>",
     background=true,
     watch_patterns=["CURSOR-STOPPED:"]
   )
   ```
3. `process list` + `process poll` 确认跟踪
4. 四步法发短任务 → 等 `CURSOR-STOPPED:<group>:...`

## 团队多角色

[huichang-team](../../huichang-team/SKILL.md) 提供 PM+Dev 协调；每 task 独立 group + daemon。

## 被动等待

验证链路时见 `passive-monitoring-discipline.md`：发完消息后禁止 sleep+capture-pane 循环。
