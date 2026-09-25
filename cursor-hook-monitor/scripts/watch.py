#!/usr/bin/env python3
"""单会话监控探针：读 <conversation_id>.jsonc，把「一轮结束」转成进程完成通知唤醒 Hermes。

用法：
    watch.py <conversation_id> [timeout_seconds] [--tmux-session <name>]

判据（hook 为主、屏幕为辅）：
  主判据：jsonc 最后一个 stop 事件的 generation_id 变了 ⇒ 这一轮结束
          → 打印 STAGE-DONE 并退出（one-shot，进程退出即触发 Hermes 完成通知）
  副判据：窗口仍开着（最后一条是 beforeSubmitPrompt）且屏幕见 Question 面板
          ⇒ 打印 QUESTION-PANEL（hook 在此场景正确地不触发，必须靠屏幕抓）

  本轮已唤醒过就静音：STAGE-DONE 之后若又出现新 stop（同轮重复事件）不再重复唤醒。

  只读不写：探针不碰 jsonc，时间窗完全由 hook 维护，避免并发写风险。
"""
import os
import sys
import time
import json
import subprocess

CONV_ID = sys.argv[1]
args = sys.argv[2:]
TIMEOUT = int(args[0]) if args and args[0].isdigit() else 1800
SESSION = CONV_ID
if "--tmux-session" in args:
    SESSION = args[args.index("--tmux-session") + 1]

# 默认值须与 start.py / adopt.py / hook_event.py 一致，且不落技能目录。
LOG_DIR = os.environ.get("CURSOR_MONITOR_LOG_DIR") or os.path.join(
    os.environ.get("TMPDIR", "/tmp").rstrip("/"), "cursor-hook-monitor", "logs"
)
EVENTS = os.path.join(LOG_DIR, f"{CONV_ID}.jsonc")

# 启动时先记住已有 stop：避免把启动前的历史轮次当成本轮的新结束
baseline_stops = set()
if os.path.exists(EVENTS):
    with open(EVENTS, encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("event") == "stop":
                    baseline_stops.add(rec.get("generation_id"))
            except Exception:
                pass
seen_stops = set(baseline_stops)

print(f"WATCH-START conv={CONV_ID} session={SESSION} timeout={TIMEOUT}s", flush=True)


def read_state():
    """只读 jsonc 尾部，拿当前时间窗。不做任何写操作。"""
    if not os.path.exists(EVENTS):
        return None
    last = None
    with open(EVENTS, encoding="utf-8") as f:
        for line in f:            # 文件小，顺序扫；只保留最后一条
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line)
            except Exception:
                continue          # 跳过半截行（追加写过程中的瞬时状态）
    return last


def all_stops():
    """扫全部行，返回 [(generation_id, record)]，跳过半截行。"""
    out = []
    if not os.path.exists(EVENTS):
        return out
    with open(EVENTS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("event") == "stop":
                out.append((rec.get("generation_id"), rec))
    return out


def stops_since_baseline():
    """本轮 stop：generation_id 不在启动基线里的那些。"""
    return [(g, r) for g, r in all_stops() if g not in baseline_stops]


def pane_text():
    try:
        return subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{SESSION}:0", "-S", "-30"],
            capture_output=True, text=True, timeout=10,
        ).stdout
    except Exception:
        return ""


deadline = time.time() + TIMEOUT
tick = 0
idle_ticks = 0
while time.time() < deadline:
    tick += 1
    time.sleep(3)

    state = read_state()

    # 1) 主判据：新的 stop → 本轮结束
    #
    # 关键：不能只看「最后一行是不是 stop」。实测 stop 与 afterAgentResponse
    # 到达顺序不固定（两个方向都出现过），甚至同一秒内到达；若采样落在两者
    # 之间，最后一行是 afterAgentResponse，会漏判本轮已结束。
    # 正确判据 = 本轮是否出现过 stop（扫全部行，按 generation_id 去重）。
    if state:
        for gen, rec in stops_since_baseline():
            if gen in seen_stops:
                continue
            seen_stops.add(gen)
            start = rec.get("round_start_at")
            dur = round(rec["ts"] - start, 2) if isinstance(start, (int, float)) else None
            print(
                "STAGE-DONE conv={} gen={} status={} loops={} start_ts={} end_ts={} duration={}".format(
                    CONV_ID, gen, rec.get("status"), rec.get("loop_count"),
                    start if start else "unknown", rec.get("ts"),
                    f"{dur}s" if dur is not None else "unknown",
                ),
                flush=True,
            )
            sys.exit(0)
        # 同一轮重复 stop 已见过 ⇒ 本轮已唤醒过，保持静音
        continue

    # 2) 副判据：请示门面板（hook 不触发，靠屏幕抓）
    if tick % 5 == 0:
        pane = pane_text()
        if "Question 1 of" in pane or "Question 2 of" in pane:
            print(
                f"QUESTION-PANEL conv={CONV_ID} 小弟在请示门等裁决（hook 不会在此触发）",
                flush=True,
            )
            sys.exit(0)
        # 子代理仍在跑：主代理可能已回 Ready，但活没干完 ⇒ 不算结束，续等
        if "Running subagent" in pane or "Running in background" in pane:
            idle_ticks = 0
            continue

    # 3) 兜底：hook 静默失效时的唯一救命通道。
    #    严格条件：本轮完全没有 stop（hook 没工作）**且** 窗口已关（不在跑）
    #    **且** 持续空闲超阈值。缺任一条都会误报——实测踩过：
    #    stop 与 afterAgentResponse 同秒到达，采样落在两者之间，
    #    若只看「最后一行是 afterAgentResponse」就当空闲 ⇒ 长任务中途误报。
    pending = [g for g, _ in stops_since_baseline()]
    if not pending and state and state.get("event") in ("afterAgentResponse", "afterFileEdit") \
            and state.get("round_open") is False:
        idle_ticks += 1
        if idle_ticks >= 10:      # 10×3s ≈ 30s 持续空闲
            print(
                f"IDLE-FALLBACK conv={CONV_ID} 无 stop 事件且持续空闲约30s（hook 疑似未触发）",
                flush=True,
            )
            sys.exit(0)
    else:
        idle_ticks = 0

print(f"WATCH-TIMEOUT conv={CONV_ID} 等待 {TIMEOUT}s 仍未收到 stop 事件", flush=True)
sys.exit(0)
