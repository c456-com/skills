"""Per-group monitor state under ~/.hermes/logs/cursor-monitors/ (configurable via env).

Environment variables:
  CURSOR_MONITOR_DIR    - override state directory (default: ~/.hermes/logs/cursor-monitors/)
  CURSOR_MONITOR_STATE_PREFIX - optional prefix for state file names
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LEGACY_TMP = Path("/tmp")
_MIGRATION_FLAG = ".migrated-from-tmp"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def default_monitor_dir() -> Path:
    return Path.home() / ".hermes" / "logs" / "cursor-monitors"


def state_prefix() -> str:
    return os.environ.get("CURSOR_MONITOR_STATE_PREFIX", "")


def monitor_dir() -> Path:
    base = Path(os.environ.get("CURSOR_MONITOR_DIR", str(default_monitor_dir())))
    if not os.environ.get("CURSOR_MONITOR_DIR"):
        _migrate_legacy_tmp_once(base)
    return base


def watch_state_dir() -> Path:
    return monitor_dir() / "watch"


def log_path(group_id: str) -> Path:
    if path := os.environ.get("CURSOR_MONITOR_LOG"):
        return Path(path)
    pfx = state_prefix()
    name = f"cursor-monitors-{pfx}--{group_id}.log" if pfx else f"cursor-monitors--{group_id}.log"
    return monitor_dir() / name


def _migrate_legacy_tmp_once(dest: Path) -> None:
    flag = dest / _MIGRATION_FLAG
    if flag.is_file():
        return
    dest.mkdir(parents=True, exist_ok=True)
    watch_dest = dest / "watch"
    migrated = False
    for path in _LEGACY_TMP.glob("cursor-monitors--*"):
        if path.suffix in {".state", ".daemon", ".log"} and not (dest / path.name).exists():
            shutil.copy2(path, dest / path.name)
            migrated = True
    for path in _LEGACY_TMP.glob("cursor-watch-*"):
        if path.suffix in {".state", ".boot", ".notify-hash"}:
            watch_dest.mkdir(parents=True, exist_ok=True)
            if not (watch_dest / path.name).exists():
                shutil.copy2(path, watch_dest / path.name)
                migrated = True
    if migrated or not flag.exists():
        flag.write_text(_now() + "\n", encoding="utf-8")


def state_path(group_id: str) -> Path:
    pfx = state_prefix()
    name = f"cursor-monitors-{pfx}--{group_id}.state" if pfx else f"cursor-monitors--{group_id}.state"
    return monitor_dir() / name


def daemon_path(group_id: str) -> Path:
    pfx = state_prefix()
    name = f"cursor-monitors-{pfx}--{group_id}.daemon" if pfx else f"cursor-monitors--{group_id}.daemon"
    return monitor_dir() / name


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_group_state(group_id: str) -> dict[str, Any]:
    path = state_path(group_id)
    if not path.is_file():
        return {
            "group_id": group_id,
            "label": group_id,
            "created_at": _now(),
            "monitors": [],
        }
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("monitors", [])
    return data


def save_group_state(group_id: str, data: dict[str, Any]) -> None:
    atomic_write_json(state_path(group_id), data)


def list_groups() -> list[str]:
    pfx = state_prefix()
    pattern = f"cursor-monitors-{pfx}--*.state" if pfx else "cursor-monitors--*.state"
    groups: list[str] = []
    for path in sorted(monitor_dir().glob(pattern)):
        stem = path.name
        if pfx:
            prefix = f"cursor-monitors-{pfx}--"
        else:
            prefix = "cursor-monitors--"
        if stem.startswith(prefix) and stem.endswith(".state"):
            groups.append(stem[len(prefix) : -len(".state")])
    return groups


def load_daemon_meta(group_id: str) -> dict[str, Any] | None:
    path = daemon_path(group_id)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save_daemon_meta(group_id: str, pid: int | None) -> None:
    path = daemon_path(group_id)
    if pid is None:
        if path.is_file():
            path.unlink()
        return
    atomic_write_json(path, {"pid": pid, "started_at": _now()})


def remove_group_files(group_id: str) -> None:
    for path in (state_path(group_id), daemon_path(group_id), log_path(group_id)):
        if path.is_file():
            path.unlink()
