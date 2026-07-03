#!/usr/bin/env python3
"""Persistent team task ledger (~/.hermes/team-tasks/ by default)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def tasks_dir() -> Path:
    default = Path.home() / ".hermes" / "team-tasks"
    return Path(os.environ.get("TEAM_TASKS_DIR", str(default)))


def task_path(task_id: str) -> Path:
    return tasks_dir() / f"{task_id}.json"


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_task(task_id: str) -> dict[str, Any]:
    with task_path(task_id).open(encoding="utf-8") as f:
        return json.load(f)


def list_task_ids(status_filter: list[str] | None = None) -> list[dict[str, Any]]:
    d = tasks_dir()
    if not d.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(d.glob("*.json")):
        if path.name.endswith(".json.tmp"):
            continue
        with path.open(encoding="utf-8") as f:
            t = json.load(f)
        if status_filter and t.get("status") not in status_filter:
            continue
        out.append(t)
    return out


def cmd_list(args: argparse.Namespace) -> int:
    statuses = [s.strip() for s in args.status.split(",")] if args.status else None
    tasks = list_task_ids(statuses)
    if not tasks:
        print("(no tasks)")
        return 0
    for t in tasks:
        print(
            f"{t['task_id']}\t{t.get('status','?')}\t{t.get('label','')}\t"
            f"{t.get('last_summary','')[:60]}"
        )
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    path = task_path(args.task_id)
    if path.is_file():
        print(f"EXISTS {args.task_id}", file=sys.stderr)
        return 1
    data = {
        "task_id": args.task_id,
        "label": args.label,
        "status": "active",
        "project_path": args.project,
        "pm_session": args.pm_session,
        "dev_session": args.dev_session,
        "comm_path": args.comm_path or "",
        "hermes_proc_session_id": "",
        "daemon_pid": None,
        "last_summary": "",
        "created_at": _now(),
        "updated_at": _now(),
    }
    atomic_write(path, data)
    print(f"CREATED {args.task_id}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    t = load_task(args.task_id)
    print(json.dumps(t, ensure_ascii=False, indent=2))
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    t = load_task(args.task_id)
    if args.last_summary is not None:
        t["last_summary"] = args.last_summary
    if args.hermes_proc_session_id is not None:
        t["hermes_proc_session_id"] = args.hermes_proc_session_id
    if args.daemon_pid is not None:
        t["daemon_pid"] = args.daemon_pid
    t["updated_at"] = _now()
    atomic_write(task_path(args.task_id), t)
    print(f"UPDATED {args.task_id}")
    return 0


def _set_status(task_id: str, status: str) -> int:
    t = load_task(task_id)
    t["status"] = status
    t["updated_at"] = _now()
    atomic_write(task_path(task_id), t)
    print(f"{status.upper()} {task_id}")
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    t = load_task(args.task_id)
    v2 = Path(__file__).resolve().parent
    skill = v2.parent
    print(f"# Resume checklist for {args.task_id}")
    print(f"task_id={t['task_id']}")
    print(f"project={t['project_path']}")
    print(f"pm_session={t['pm_session']}")
    print(f"dev_session={t['dev_session']}")
    print(f"last_summary={t.get('last_summary','')}")
    print("--- commands ---")
    print(f'python3 "{v2}/cursor_monitor.py" group-create {t["task_id"]} --label "{t.get("label","")}"')
    print(f"# tmux: recreate {t['pm_session']} and {t['dev_session']}")
    print(
        f'python3 "{v2}/cursor_monitor.py" add --group {t["task_id"]} '
        f'{t["pm_session"]} 0 --label "PM"'
    )
    print(
        f'python3 "{v2}/cursor_monitor.py" add --group {t["task_id"]} '
        f'{t["dev_session"]} 0 --label "Dev"'
    )
    print(
        f'python3 "{v2}/cursor_monitor.py" daemon --group {t["task_id"]}'
    )
    print(f"# Ask PM: 我们上次停在哪？ last: {t.get('last_summary','')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="辉常团队任务台账")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--status", default="active,paused", help="comma-separated statuses")
    p_list.set_defaults(func=cmd_list)

    p_create = sub.add_parser("create", help="create task")
    p_create.add_argument("--task-id", required=True)
    p_create.add_argument("--label", required=True)
    p_create.add_argument("--project", required=True)
    p_create.add_argument("--pm-session", required=True)
    p_create.add_argument("--dev-session", required=True)
    p_create.add_argument("--comm-path", default="")
    p_create.set_defaults(func=cmd_create)

    p_show = sub.add_parser("show", help="show task")
    p_show.add_argument("--task-id", required=True)
    p_show.set_defaults(func=cmd_show)

    p_update = sub.add_parser("update", help="update task")
    p_update.add_argument("--task-id", required=True)
    p_update.add_argument("--last-summary", default=None)
    p_update.add_argument("--hermes-proc-session-id", default=None)
    p_update.add_argument("--daemon-pid", type=int, default=None)
    p_update.set_defaults(func=cmd_update)

    for name, status in (("pause", "paused"), ("complete", "completed"), ("abandon", "abandoned"), ("activate", "active")):
        p = sub.add_parser(name, help=f"set status={status}")
        p.add_argument("--task-id", required=True)

        def _make(st: str):
            def _cmd(args: argparse.Namespace) -> int:
                return _set_status(args.task_id, st)

            return _cmd

        p.set_defaults(func=_make(status))

    p_resume = sub.add_parser("resume", help="print recovery checklist")
    p_resume.add_argument("--task-id", required=True)
    p_resume.set_defaults(func=cmd_resume)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
