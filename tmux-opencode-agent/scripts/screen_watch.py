#!/usr/bin/env python3
"""OpenCode 探针的屏幕副路。

SSE 仍是主判据；本模块只负责低频读取 tmux 屏幕，识别 TUI 渲染出来的
终态/异常关键字并打印，不触发探针退出。轮询间隔固定 15 秒：探针的职责是
避免长时间不知情地丢信号，不是提供秒级实时反馈；15 秒足够在一次人工处理
窗口内发现权限面板或静默僵死，同时不会在长任务里刷屏。
"""
import subprocess


SCREEN_POLL_INTERVAL = 15
SCREEN_SOURCE = "这是屏副路发现的，不是 SSE"


def parse_pane_text(text):
    """把一段 tmux 屏面文本解析成稳定的信号列表。

    ``esc interrupt`` 是运行中的对照提示；只要它出现，就不把同一屏里的
    ``interrupted`` 关键字误报成终态。返回项是 ``kind``/``keyword`` 字典，
    供打印和自测共用。
    """
    if not isinstance(text, str) or not text.strip():
        return []

    lowered = text.casefold()
    signals = []
    running_hint = "esc interrupt" in lowered or "esc to interrupt" in lowered
    if running_hint:
        signals.append({"kind": "active", "keyword": "esc interrupt"})

    if "interrupted" in lowered and not running_hint:
        signals.append({"kind": "terminal", "keyword": "interrupted"})

    permission_markers = (
        "permission required",
        "permission panel",
        "权限面板",
    )
    if any(marker in lowered for marker in permission_markers):
        signals.append({"kind": "permission", "keyword": "Permission required"})

    # OpenCode 的提问面板（AskUserQuestion）**不走 permission.asked 事件**，
    # 走 SSE 只会看到小弟静默等人 ⇒ 必须靠屏副路兜底。
    # 2026-09-28 实测文案：`↑↓ select  enter submit  esc dismiss`。
    question_markers = ("enter submit", "esc dismiss")
    if all(marker in lowered for marker in question_markers):
        signals.append({"kind": "question", "keyword": "AskUserQuestion panel"})

    process_markers = (
        "process exited",
        "process has exited",
        "session ended",
        "no tui",
        "tui is not running",
        "no active pane",
    )
    if any(marker in lowered for marker in process_markers):
        signals.append({"kind": "process", "keyword": "process/session not running"})

    # 同一屏里重复出现的同一信号只保留一次。
    unique = []
    seen = set()
    for signal in signals:
        key = (signal["kind"], signal["keyword"])
        if key not in seen:
            seen.add(key)
            unique.append(signal)
    return unique


def format_screen_signal(session, signal, detail=""):
    """生成明确标注来源、且不与 SSE 输出混淆的一行。"""
    prefixes = {
        "terminal": "SCREEN-TERMINAL",
        "active": "SCREEN-ACTIVE",
        "permission": "SCREEN-PERMISSION",
        "question": "SCREEN-QUESTION",
        "process": "SCREEN-PROCESS",
    }
    prefix = prefixes.get(signal["kind"], "SCREEN-ALERT")
    suffix = f" detail={detail}" if detail else ""
    return (
        f"{prefix} session={session} keyword={signal['keyword']} "
        f"source=screen（{SCREEN_SOURCE}）{suffix}"
    )


def capture_pane(session):
    """抓取最近 30 行；返回 ``(text, error)``，错误只交给副路打印。"""
    if not session:
        return "", "no --tmux-session configured"
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", f"{session}:0", "-S", "-30"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return "", f"capture-pane failed: {exc}"

    if result.returncode != 0:
        detail = result.stderr.strip().replace("\n", " ")[:200]
        return "", f"capture-pane rc={result.returncode}" + (f": {detail}" if detail else "")
    if not result.stdout.strip():
        return "", "capture-pane returned no TUI content"
    return result.stdout, None


def _emit(session, signal, seen, detail="", dedupe_key=None):
    key = dedupe_key or (signal["kind"], signal["keyword"])
    if key in seen:
        return
    seen.add(key)
    print(format_screen_signal(session, signal, detail), flush=True)


def run_screen_loop(session, stop_event, interval=SCREEN_POLL_INTERVAL):
    """每 15 秒读屏；只打印，不抛退出、不改变 SSE 主路生命周期。"""
    seen = set()
    while not stop_event.wait(interval):
        try:
            text, error = capture_pane(session)
            if error:
                signal = {"kind": "process", "keyword": "process/session not running"}
                _emit(session, signal, seen, detail=error, dedupe_key=("process", "capture-failed"))
                continue

            # 读屏恢复后，下一次失联仍应重新报警。
            seen.discard(("process", "capture-failed"))
            for signal in parse_pane_text(text):
                _emit(session, signal, seen)
        except Exception as exc:
            # 副路自身异常也不能杀掉 SSE 主路。
            signal = {"kind": "process", "keyword": "screen watcher error"}
            _emit(session, signal, seen, detail=str(exc)[:200], dedupe_key=("process", "watcher-error"))
