#!/usr/bin/env bash
# calibrate-capture.sh — 抓取 tmux pane 存为校准 fixture
# 用法: calibrate-capture.sh <fixture-name> <mode> <expected> [reason] [trigger_note]
# 例: calibrate-capture.sh auto-stopped-S01 auto stopped idle "启动后空闲"

set -euo pipefail

FIXTURE_NAME="${1:?fixture name}"
MODE="${2:?mode}"
EXPECTED="${3:?executing|stopped}"
REASON="${4:-}"
NOTE="${5:-}"
SESSION="${CALIBRATE_SESSION:-cursor-calibrate}"
WINDOW="${CALIBRATE_WINDOW:-0}"
LINES="${CALIBRATE_LINES:-40}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FIXTURES_DIR="${CALIBRATE_FIXTURES_DIR:-${PROJECT_DIR}/fixtures/calibrate}"
META_DIR="${FIXTURES_DIR}/meta"
mkdir -p "$FIXTURES_DIR" "$META_DIR"
TXT="${FIXTURES_DIR}/${FIXTURE_NAME}.txt"
META="${META_DIR}/${FIXTURE_NAME}.json"

CONTENT=$(tmux capture-pane -t "${SESSION}:${WINDOW}" -p -S "-${LINES}" 2>/dev/null || true)
if [ -z "$CONTENT" ]; then
    echo "ERROR: no content from ${SESSION}:${WINDOW}" >&2
    exit 1
fi

printf '%s\n' "$CONTENT" > "$TXT"
HASH=$(printf '%s' "$CONTENT" | md5sum | cut -d' ' -f1)
TS=$(date -Iseconds)

cat > "$META" <<EOF
{
  "id": "${FIXTURE_NAME}",
  "mode": "${MODE}",
  "expected": "${EXPECTED}",
  "reason": "${REASON}",
  "trigger": "${NOTE}",
  "session": "${SESSION}:${WINDOW}",
  "captured_at": "${TS}",
  "content_hash": "${HASH}"
}
EOF

echo "captured ${FIXTURE_NAME} -> ${TXT}"
echo "  expected=${EXPECTED} reason=${REASON}"
