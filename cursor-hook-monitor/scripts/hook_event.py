#!/usr/bin/env python3
"""Cursor CLI hook —— 每会话一个事件流文件 <conversation_id>.jsonc。

为什么从 state.json 改成事件流：
  状态文件只留「当前状态」，历史丢失、事后无法观测；且 stop_seq 这类全局
  计数器需要读-改-写，跨进程并发下天然脆弱。
  改成「每事件一行」的追加流后：
    · 完整历史保留 ⇒ 事后能复盘整场对话的时间线
    · 最后一行即当前状态 ⇒ 监控 tail -1 就拿到时间窗，无需任何计数器
    · hook 只追加、不读改写 ⇒ 并发只争 append 位置，风险极低

  文件名即 conversation_id：配合 `cursor-agent create-chat` 预分配，
  监控可在 agent 启动前就确定文件路径，无需事后反查。

  格式：UTF-8，每行一个 JSON 对象（JSON Lines；用 .jsonc 扩展名沿用既有约定，
  内容不含注释，任意 JSON 解析器都能逐行读）。

  硬约束（均为实测踩出来的）：
    1. 必须 chmod +x，否则静默失效且 agent 不报错。
    2. 必须在本进程启动前完成配置；长驻进程不重载 hook 配置。
    3. 进程内只追加即退，禁止跑测试/git/网络（hook 会阻塞 agent 轮次）。
    4. 解析失败 fail-open：报错但绝不阻塞 agent。
    5. 没有 CURSOR_MONITOR_TAG 时写进 _UNATTRIBUTED，暴露问题而非静默丢弃。
"""
import sys
import os
import json
import time
import fcntl

TAG = os.environ.get("CURSOR_MONITOR_TAG") or "_UNATTRIBUTED"
# 默认值须与 start.py / adopt.py / watch.py 一致，且不落技能目录。
# 经 start.py / adopt.py 启动时会显式注入 CURSOR_MONITOR_LOG_DIR，此默认只在手工装 hook 时生效。
LOG_DIR = os.environ.get("CURSOR_MONITOR_LOG_DIR") or os.path.join(
    os.environ.get("TMPDIR", "/tmp").rstrip("/"), "cursor-hook-monitor", "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)
EVENTS = os.path.join(LOG_DIR, f"{TAG}.jsonc")

try:
    payload = json.load(sys.stdin)
    event = payload.get("hook_event_name", "?")
except Exception as exc:
    print(json.dumps({"error": f"hook payload parse failed: {exc!r}"}), flush=True)
    sys.exit(0)  # fail-open

record = {
    "ts": round(time.time(), 3),
    "event": event,
    "conversation_id": payload.get("conversation_id"),
    "generation_id": payload.get("generation_id"),
    "workspace_roots": payload.get("workspace_roots"),
    "status": payload.get("status"),
    "loop_count": payload.get("loop_count"),
    "input_tokens": payload.get("input_tokens"),
}

# 只保留尾部，避免超长回复把单行撑到不可读；完整正文可从会话 store 取
if event == "afterAgentResponse":
    text = payload.get("text")
    if text:
        record["text_tail"] = text[-800:]

# 时间窗起点：扫一遍已有事件，取最后一个 beforeSubmitPrompt 的 ts。
# 纯读，不改文件；这样 stop/afterAgentResponse 行自带 round_start_at，
# 监控 tail -1 即可拿到本轮开始时间，无需维护跨进程计数器。
if os.path.exists(EVENTS):
    last_start = None
    try:
        with open(EVENTS, encoding="utf-8") as rf:
            for prev in rf:
                try:
                    prec = json.loads(prev)
                except Exception:
                    continue
                if prec.get("event") == "beforeSubmitPrompt":
                    last_start = prec.get("ts")
    except Exception:
        pass
    if last_start is not None:
        record["round_start_at"] = last_start
        record["round_open"] = event not in ("stop",)

line = json.dumps(record, ensure_ascii=False) + "\n"

# 追加写。flock 保证多 hook 进程（stop 与 afterAgentResponse 是不同进程）
# 不会交错撕裂；单行 <PIPE_BUF 的追加在 POSIX 下也是原子的。
with open(EVENTS, "a", encoding="utf-8") as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    try:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

sys.exit(0)
