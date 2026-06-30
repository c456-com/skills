#!/usr/bin/env python3
"""Adaptive tmux pane reading — no fixed line counts in code.

Line counts are chosen by the caller per task; this CLI only executes capture ranges.

tmux capture-pane -S/-E use negative indices counted from the bottom of scrollback:
  --lines 100           → last 100 lines (-S -100)
  --offset 100 --lines 80 → lines 101-180 from bottom (-S -180 -E -101)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_MAX_LINES = 5000


def capture_range(session: str, window: str, start_from_bottom: int, end_from_bottom: int) -> str:
    """Capture pane lines between start/end (both counted from bottom, start > end)."""
    target = f"{session}:{window}"
    r = subprocess.run(
        [
            "tmux",
            "capture-pane",
            "-t",
            target,
            "-p",
            "-S",
            f"-{start_from_bottom}",
            "-E",
            f"-{end_from_bottom}",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        print(r.stderr or f"capture failed for {target}", file=sys.stderr)
        return ""
    return r.stdout


def capture_last(session: str, window: str, lines: int) -> str:
    if lines < 1:
        return ""
    return capture_range(session, window, lines, 1)


def cmd_capture(args: argparse.Namespace) -> int:
    if args.lines > args.max_lines:
        print(f"ERROR: --lines {args.lines} exceeds --max-lines {args.max_lines}", file=sys.stderr)
        return 1

    if args.offset > 0:
        start = args.offset + args.lines
        end = args.offset + 1
        meta = f"# cursor_read: {args.session}:{args.window} offset={args.offset} lines={args.lines}"
        text = capture_range(args.session, args.window, start, end)
    else:
        meta = f"# cursor_read: {args.session}:{args.window} lines={args.lines}"
        text = capture_last(args.session, args.window, args.lines)

    out = f"{meta}\n{text}"
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"WROTE {args.out} ({len(text.splitlines())} lines)", file=sys.stderr)
    else:
        sys.stdout.write(out if out.endswith("\n") else out + "\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read cursor-agent tmux pane; line counts supplied by caller."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("capture", help="capture scrollback slice")
    p.add_argument("session")
    p.add_argument("window")
    p.add_argument(
        "--lines",
        type=int,
        required=True,
        help="number of lines to capture (from bottom, or above --offset)",
    )
    p.add_argument(
        "--offset",
        type=int,
        default=0,
        help="skip this many lines from bottom before capturing (read older content)",
    )
    p.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_LINES,
        help=f"safety cap (default {DEFAULT_MAX_LINES})",
    )
    p.add_argument("--out", type=Path, default=None, help="write to file instead of stdout only")
    p.set_defaults(func=cmd_capture)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
