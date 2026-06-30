#!/usr/bin/env python3
"""cursor monitor CLI + daemon (per-group state files).

A polling daemon that watches cursor-agent tmux panes and emits
CURSOR-STOPPED notifications when agent transitions from EXECUTING to STOPPED.
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.registry import (
    daemon_path,
    list_groups,
    load_daemon_meta,
    load_group_state,
    remove_group_files,
    save_daemon_meta,
    save_group_state,
)
from core.monitor_log import MonitorLog
from core.watch import WatchResult

SCRIPT_DIR = Path(__file__).resolve().parent.parent
WATCH_SCRIPT = SCRIPT_DIR / "core" / "watch.py"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def _find_monitor(data: dict[str, Any], session: str, window: int) -> dict[str, Any] | None:
    for m in data["monitors"]:
        if m["session"] == session and int(m["window"]) == int(window):
            return m
    return None


def cmd_group_create(args: argparse.Namespace) -> int:
    if args.group in list_groups():
        print(f"EXISTS {args.group}", file=sys.stderr)
        return 1
    data = {
        "group_id": args.group,
        "label": args.label or args.group,
        "created_at": _now_iso(),
        "monitors": [],
    }
    save_group_state(args.group, data)
    print(f"GROUP_CREATED {args.group}")
    return 0


def cmd_group_remove(args: argparse.Namespace) -> int:
    if args.group not in list_groups():
        print(f"NOT_FOUND {args.group}", file=sys.stderr)
        return 1
    remove_group_files(args.group)
    print(f"GROUP_REMOVED {args.group}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    data = load_group_state(args.group)
    window = int(args.window)
    existing = _find_monitor(data, args.session, window)
    if existing:
        existing["enabled"] = True
        if args.label:
            existing["label"] = args.label
        save_group_state(args.group, data)
        print(f"UPDATED {existing['id']} ({args.session}:{window})")
        return 0
    mid = (args.label or f"{args.session}-{window}").replace(" ", "-").lower()[:40]
    entry = {
        "id": mid,
        "session": args.session,
        "window": window,
        "label": args.label or f"{args.session}:{window}",
        "enabled": True,
        "created_at": _now_iso(),
        "pending": None,
    }
    data["monitors"].append(entry)
    save_group_state(args.group, data)
    print(f"ADDED {mid} ({args.session}:{window})")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    data = load_group_state(args.group)
    key = args.target
    before = len(data["monitors"])
    if ":" in key:
        session, window = key.rsplit(":", 1)
        if window.isdigit():
            data["monitors"] = [
                m
                for m in data["monitors"]
                if not (m["session"] == session and str(m["window"]) == window)
            ]
    else:
        data["monitors"] = [m for m in data["monitors"] if m["id"] != key]
    if len(data["monitors"]) >= before:
        print(f"NOT_FOUND {key}", file=sys.stderr)
        return 1
    save_group_state(args.group, data)
    print(f"REMOVED {key}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    groups = [args.group] if args.group else list_groups()
    if not groups:
        print("(no groups)")
        return 0
    for gid in groups:
        data = load_group_state(gid)
        print(f"# group {gid} ({data.get('label', gid)})")
        for m in data["monitors"]:
            if not m.get("enabled", True):
                continue
            pending = m.get("pending")
            p = f" pending={pending['reason']}" if pending else ""
            print(f"{m['id']}\t{m['session']}:{m['window']}\t{m.get('label', '')}{p}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    meta = load_daemon_meta(args.group)
    pid = meta.get("pid") if meta else None
    print(f"daemon_pid={pid or 'none'}")
    data = load_group_state(args.group)
    for m in data["monitors"]:
        if not m.get("enabled", True):
            continue
        print(f"monitor\t{m['session']}:{m['window']}\t{m.get('label', '')}")
    return 0


def cmd_set_pending(args: argparse.Namespace) -> int:
    data = load_group_state(args.group)
    session, window = args.target.rsplit(":", 1)
    m = _find_monitor(data, session, int(window))
    if not m:
        print(f"NOT_FOUND {args.target}", file=sys.stderr)
        return 1
    m["pending"] = {"reason": args.reason, "summary": args.summary, "since": _now_iso()}
    save_group_state(args.group, data)
    print(f"PENDING_SET {args.target}")
    return 0


def cmd_clear_pending(args: argparse.Namespace) -> int:
    data = load_group_state(args.group)
    session, window = args.target.rsplit(":", 1)
    m = _find_monitor(data, session, int(window))
    if not m:
        print(f"NOT_FOUND {args.target}", file=sys.stderr)
        return 1
    m["pending"] = None
    save_group_state(args.group, data)
    print(f"PENDING_CLEARED {args.target}")
    return 0


def _invoke_watch(session: str, window: int, lines: int, debug: bool) -> WatchResult:
    """Run watch in-process; reload module so long-running daemon picks up script edits."""
    import importlib

    from core import watch as cw

    importlib.reload(cw)
    return cw.run_watch(session, str(window), lines, debug=debug)


def _format_stopped(group: str, raw_line: str) -> str:
    """Convert CURSOR-STOPPED:sess:win:reason -> CURSOR-STOPPED:group:sess:win:reason"""
    if not raw_line.startswith("CURSOR-STOPPED:"):
        return raw_line
    parts = raw_line.split(":", 4)
    if len(parts) == 4:
        _, session, window, reason = parts
        return f"CURSOR-STOPPED:{group}:{session}:{window}:{reason}"
    return raw_line


def daemon_tick(group: str, lines: int, debug: bool, log: MonitorLog) -> tuple[int, int, int]:
    data = load_group_state(group)
    ok = skipped = 0
    for m in data["monitors"]:
        if not m.get("enabled", True):
            continue
        session = m["session"]
        window = int(m["window"])
        target = f"{session}:{window}"
        if subprocess.run(["tmux", "has-session", "-t", session], capture_output=True).returncode != 0:
            if debug:
                print(f"  [{target}] SKIP session missing", file=sys.stderr)
            log.emit(
                f"CURSOR-MONITOR-SKIP group={group} session={target} reason=session_missing"
            )
            skipped += 1
            continue
        result = _invoke_watch(session, window, lines, debug)
        ok += 1
        log.emit(
            f"CURSOR-MONITOR-WATCH group={group} session={target} "
            f"state={result.state} reason={result.reason}"
        )
        if result.notify_line:
            log.emit_with_body(
                _format_stopped(group, result.notify_line),
                result.pane_content,
            )
    return ok, skipped, len(data["monitors"])


def cmd_daemon(args: argparse.Namespace) -> int:
    group = args.group
    interval = int(os.environ.get("CURSOR_MONITOR_INTERVAL", "15"))
    status_interval = int(os.environ.get("CURSOR_MONITOR_STATUS_INTERVAL", "600"))
    lines = int(os.environ.get("CURSOR_MONITOR_LINES", "15"))
    debug = args.debug
    once = args.once
    log_path = Path(args.log_file) if args.log_file else None
    log = MonitorLog(group, log_path)

    def _log(msg: str) -> None:
        print(f"[cursor-monitor-daemon:{group}] {msg}", file=sys.stderr)

    log.emit(
        f"CURSOR-MONITOR-START group={group} pid={os.getpid()} interval={interval}s"
    )
    _log(f"started pid={os.getpid()} interval={interval}s log={log.path}")
    save_daemon_meta(group, os.getpid())

    def _cleanup(*_a: Any) -> None:
        log.emit(f"CURSOR-MONITOR-STOP group={group} pid={os.getpid()}")
        _log("stopped")
        save_daemon_meta(group, None)
        log.close()

    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)

    tick_count = 0
    last_status_at = time.time()

    try:
        while True:
            if debug:
                _log(f"tick {time.strftime('%H:%M:%S')}")
            ok, skipped, total = daemon_tick(group, lines, debug, log)
            tick_count += 1
            log.emit(
                f"CURSOR-MONITOR-TICK group={group} ok={ok} skipped={skipped} total={total}"
            )
            now = time.time()
            if status_interval > 0 and (now - last_status_at) >= status_interval:
                log.emit(
                    f"CURSOR-MONITOR-STATUS:{group}:monitors={total}:ok={ok}:"
                    f"skipped={skipped}:daemon_pid={os.getpid()}"
                )
                last_status_at = now

            if once:
                _log("done (--once)")
                _cleanup()
                return 0
            time.sleep(interval)
    except Exception:
        log.close()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="cursor monitor")
    sub = parser.add_subparsers(dest="command")

    p_gc = sub.add_parser("group-create")
    p_gc.add_argument("group")
    p_gc.add_argument("--label", default="")
    p_gc.set_defaults(func=cmd_group_create)

    p_gr = sub.add_parser("group-remove")
    p_gr.add_argument("group")
    p_gr.set_defaults(func=cmd_group_remove)

    p_add = sub.add_parser("add")
    p_add.add_argument("--group", required=True)
    p_add.add_argument("session")
    p_add.add_argument("window")
    p_add.add_argument("--label", default="")
    p_add.set_defaults(func=cmd_add)

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("--group", required=True)
    p_rm.add_argument("target")
    p_rm.set_defaults(func=cmd_remove)

    p_list = sub.add_parser("list")
    p_list.add_argument("--group", default="")
    p_list.set_defaults(func=cmd_list)

    p_st = sub.add_parser("status")
    p_st.add_argument("--group", required=True)
    p_st.set_defaults(func=cmd_status)

    p_sp = sub.add_parser("set-pending")
    p_sp.add_argument("--group", required=True)
    p_sp.add_argument("target")
    p_sp.add_argument("reason")
    p_sp.add_argument("summary")
    p_sp.set_defaults(func=cmd_set_pending)

    p_cp = sub.add_parser("clear-pending")
    p_cp.add_argument("--group", required=True)
    p_cp.add_argument("target")
    p_cp.set_defaults(func=cmd_clear_pending)

    p_d = sub.add_parser("daemon")
    p_d.add_argument("--group", required=True)
    p_d.add_argument("--debug", action="store_true")
    p_d.add_argument("--once", action="store_true")
    p_d.add_argument("--log-file", default="", help="override log path (or CURSOR_MONITOR_LOG)")
    p_d.set_defaults(func=cmd_daemon)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
