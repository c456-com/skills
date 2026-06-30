"""Structured log output for cursor monitor daemon (stdout + optional log file)."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from core.registry import log_path as registry_log_path


class MonitorLog:
    """Writes structured cursor-monitor log lines to stdout and optionally to a file."""

    def __init__(self, group_id: str, override_path: Path | None = None) -> None:
        self.group_id = group_id
        self.path: Path = override_path or registry_log_path(group_id)
        self._file = None

    def _iso(self) -> str:
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    def emit(self, line: str) -> None:
        iso = self._iso()
        sys.stdout.write(f"[{iso}] {line}\n")
        sys.stdout.flush()
        self._write_file(f"[{iso}] {line}\n")

    def emit_with_body(self, headline: str, body: str | None) -> None:
        self.emit(headline)
        if body and body.strip():
            for line in body.rstrip("\n").split("\n"):
                self._write_line(f"  | {line}")

    def _write_file(self, text: str) -> None:
        if not self._file:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._file = self.path.open("a", encoding="utf-8")
        self._file.write(text)
        self._file.flush()

    def _write_line(self, line: str) -> None:
        self._write_file(line + "\n")

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None
