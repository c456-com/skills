#!/usr/bin/env python3
"""Watch cursor-agent tmux pane — state detection engine.

Detects whether a cursor-agent pane is EXECUTING or STOPPED,
and classifies the reason for STOPPED states.

Supports reading from live tmux panes or from fixture files for testing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from core.registry import watch_state_dir

BRAILLE_RE = re.compile(r"[\u2800-\u28FF]")
ACTIVITY_RE = re.compile(
    r"(^|[\s])(Working|Running|Thinking|Reading|Globbing|Editing|Waiting|Reconnecting)([\s:]|$)"
)
BACKGROUND_RE = re.compile(r"[0-9]+ background tasks?")
MONITORING_RE = re.compile(
    r"progress:\s*\d+/\d+|elapsed=\d+"
)
TASK_COUNT_RE = re.compile(r"^\s*\d+\s+tasks?\s*$")
AUTO_STATUS_RE = re.compile(r"^\s*Auto\s*·")
VOLATILE_HASH_RES = (
    re.compile(r"progress:\s*\d+/\d+"),
    re.compile(r"elapsed="),
    re.compile(r"Auto\s*·\s*[\d.]+%"),
    re.compile(r"[\d.]+k tokens"),
    re.compile(r"^\d{2}:\d{2}:\d{2}\s"),
)
NEEDS_INPUT_RE = re.compile(
    r"Question [0-9]+ of [0-9]+|Enter to submit, Esc to cancel|AskQuestion|"
    r"Ready to build"
)
TASK_DONE_RE = re.compile(r"All tests passed|✅|done\.")
INPUT_PLACEHOLDER_RES = (
    re.compile(r"^Add a follow-up(?:.*)?$"),
    re.compile(r"^Describe how to revise(?: the plan)?", re.I),
    re.compile(r"^Plan, search, build anything$"),
)


def _input_line_text(line: str) -> str | None:
    if "│" in line:
        return None
    match = re.match(r"^\s*→\s*(.+)$", line)
    if not match:
        return None
    text = re.sub(r"\s+ctrl\+c to stop\s*$", "", match.group(1)).strip()
    return text or None


def has_unsubmitted_input(bottom: str) -> bool:
    """True when the follow-up input box holds user text (not an empty placeholder)."""
    for line in bottom.splitlines():
        text = _input_line_text(line)
        if text is None:
            continue
        if any(pattern.search(text) for pattern in INPUT_PLACEHOLDER_RES):
            continue
        return True
    return False


@dataclass
class WatchResult:
    notify_line: str | None
    pane_content: str | None
    state: str  # executing | stopped
    reason: str


def watch_state_prefix() -> str:
    pfx = os.environ.get("CURSOR_WATCH_STATE_PREFIX", os.environ.get("CURSOR_MONITOR_STATE_PREFIX", ""))
    return pfx or ""


def _state_file(session: str, window: str) -> Path:
    pfx = watch_state_prefix()
    base = f"cursor-watch-{session}-{window}"
    if pfx:
        base = f"cursor-watch-{pfx}-{session}-{window}"
    return watch_state_dir() / f"{base}.state"


def _boot_file(session: str, window: str) -> Path:
    pfx = watch_state_prefix()
    base = f"cursor-watch-{session}-{window}"
    if pfx:
        base = f"cursor-watch-{pfx}-{session}-{window}"
    return watch_state_dir() / f"{base}.boot"


def _hash_file(session: str, window: str) -> Path:
    pfx = watch_state_prefix()
    base = f"cursor-watch-{session}-{window}"
    if pfx:
        base = f"cursor-watch-{pfx}-{session}-{window}"
    return watch_state_dir() / f"{base}.notify-hash"


def _is_footer_line(line: str) -> bool:
    stripped = line.strip()
    if _input_line_text(line) is not None:
        return True
    if TASK_COUNT_RE.match(stripped):
        return True
    if AUTO_STATUS_RE.match(stripped):
        return True
    if "Run Everything" in line:
        return True
    if stripped.startswith("~/") and " · " in stripped:
        return True
    return False


def _activity_region(content: str) -> str:
    """Pane lines above the Cursor input box / status footer."""
    lines: list[str] = []
    for line in content.splitlines():
        if _is_footer_line(line):
            break
        lines.append(line)
    return "\n".join(lines)


def normalize_for_hash(content: str) -> str:
    """Strip volatile lines before hash compare to avoid idle re-notify spam."""
    kept: list[str] = []
    for line in content.splitlines():
        if any(pattern.search(line) for pattern in VOLATILE_HASH_RES):
            continue
        if BRAILLE_RE.search(line) and ACTIVITY_RE.search(line):
            continue
        stripped = line.strip()
        if stripped and all(
            (0x2800 <= ord(ch) <= 0x28FF) or ch.isspace() for ch in stripped
        ):
            continue
        kept.append(line)
    return "\n".join(kept)


def is_executing(activity_text: str) -> bool:
    if BRAILLE_RE.search(activity_text):
        return True
    if ACTIVITY_RE.search(activity_text):
        return True
    if BACKGROUND_RE.search(activity_text):
        return True
    if MONITORING_RE.search(activity_text):
        return True
    return False


def classify_reason(content: str, bottom: str) -> str:
    if "Press Ctrl+C again to exit" in bottom:
        return "exited"
    if re.search(r"Run this command\?|Run \(once\) \(y\)", bottom):
        return "needs_approval"
    if NEEDS_INPUT_RE.search(content):
        return "needs_input"
    if TASK_DONE_RE.search(content):
        return "task_done"
    return "idle"


def capture_pane(session: str, window: str, lines: int) -> str:
    target = f"{session}:{window}"
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", target, "-p", "-S", f"-{lines}"],
        capture_output=True,
        text=True,
    )
    return result.stdout or ""


def run_watch(
    session: str,
    window: str,
    lines: int = 15,
    *,
    fixture_file: Path | None = None,
    debug: bool = False,
) -> WatchResult:
    """Returns watch outcome; notify_line set when agent should be notified."""
    target = f"{session}:{window}"
    if fixture_file is not None:
        content = fixture_file.read_text(encoding="utf-8")
        target = f"fixture:{fixture_file.name}"
    else:
        content = capture_pane(session, window, lines)

    if not content:
        if debug:
            print(f"[cursor-watch:{target}] no pane content", file=sys.stderr)
        return WatchResult(None, None, "stopped", "empty")

    bottom = "\n".join(content.splitlines()[-10:])
    activity_text = _activity_region(content)
    content_hash = hashlib.md5(normalize_for_hash(content).encode()).hexdigest()
    executing = is_executing(activity_text)
    stopped = not executing
    state = "executing" if executing else "stopped"

    state_file = _state_file(session, window)
    boot_file = _boot_file(session, window)
    hash_file = _hash_file(session, window)
    watch_state_dir().mkdir(parents=True, exist_ok=True)

    last = state_file.read_text(encoding="utf-8").strip() if state_file.is_file() else ""
    if last == "stopped":
        last = "idle"
    last_hash = hash_file.read_text(encoding="utf-8").strip() if hash_file.is_file() else ""
    boot = not boot_file.exists()
    if boot:
        boot_file.touch()

    reason = classify_reason(content, bottom)

    if debug:
        print(
            f"[cursor-watch:{target}] EXECUTING={executing} reason={reason} "
            f"LAST={last or 'none'} BOOT={boot} hash_changed={content_hash != last_hash} "
            f"user_draft={stopped and has_unsubmitted_input(bottom)}",
            file=sys.stderr,
        )

    if stopped and has_unsubmitted_input(bottom):
        state_file.write_text("held", encoding="utf-8")
        return WatchResult(None, None, state, "user_draft")

    should_notify = False
    if stopped:
        if last == "working":
            should_notify = True
        elif boot:
            should_notify = True
        elif last == "idle" and content_hash != last_hash:
            should_notify = True
        elif last == "held":
            should_notify = True

    if should_notify:
        notify = f"CURSOR-STOPPED:{session}:{window}:{reason}"
        state_file.write_text("idle", encoding="utf-8")
        hash_file.write_text(content_hash, encoding="utf-8")
        return WatchResult(notify, content, state, reason)

    if executing:
        state_file.write_text("working", encoding="utf-8")
        return WatchResult(None, None, state, reason)

    if stopped:
        state_file.write_text("idle", encoding="utf-8")
    return WatchResult(None, None, state, reason)


def run_fixture_regression(fixtures_dir: Path) -> int:
    ground_truth = fixtures_dir / "ground-truth.json"
    if not ground_truth.is_file():
        print("missing ground-truth.json", file=sys.stderr)
        return 1
    truth = json.loads(ground_truth.read_text(encoding="utf-8"))
    passed = failed = 0
    for name in sorted(truth.keys()):
        expected = truth[name]
        file_path = fixtures_dir / f"{name}.txt"
        if not file_path.is_file():
            print(f"MISSING {file_path}")
            failed += 1
            continue
        file_content = file_path.read_text(encoding="utf-8")
        activity_text = _activity_region(file_content)
        detected = "executing" if is_executing(activity_text) else "stopped"
        bottom = "\n".join(file_content.splitlines()[-10:])
        if detected == expected:
            passed += 1
            print(f"PASS {name}")
        else:
            failed += 1
            snippet = bottom.replace("\n", " ")[:160]
            print(f"FAIL {name} expected={expected} detected={detected}")
            print(f"  bottom: {snippet}")
    total = passed + failed
    print("---")
    print(f"{passed}/{total} passed, {failed} failed")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="cursor-agent tmux watch (v2)")
    parser.add_argument("--fixture", type=Path, help="fixture file path")
    parser.add_argument("--test-fixtures", action="store_true", help="run fixture regression")
    parser.add_argument("--fixtures-dir", type=Path, help="fixtures directory for --test-fixtures")
    parser.add_argument("session", nargs="?", default="cursor")
    parser.add_argument("window", nargs="?", default="3")
    parser.add_argument("lines", nargs="?", type=int, default=15)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.test_fixtures:
        script_dir = Path(__file__).resolve().parent.parent
        fixtures_dir = args.fixtures_dir or (script_dir / "fixtures" / "calibrate")
        return run_fixture_regression(fixtures_dir)

    if args.fixture:
        result = run_watch(
            args.session,
            str(args.window),
            args.lines,
            fixture_file=args.fixture,
            debug=args.debug,
        )
    else:
        result = run_watch(
            args.session,
            str(args.window),
            args.lines,
            debug=args.debug,
        )

    if result.notify_line:
        print(result.notify_line)
        if result.pane_content:
            print(result.pane_content, end="" if result.pane_content.endswith("\n") else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
