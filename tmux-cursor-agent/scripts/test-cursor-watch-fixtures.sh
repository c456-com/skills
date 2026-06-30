#!/usr/bin/env bash
# test-cursor-watch-fixtures.sh — Run fixture regression on state detection engine
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

FIXTURES_DIR="${PROJECT_DIR}/fixtures/calibrate"
if [ -n "${CALIBRATE_FIXTURES_DIR:-}" ]; then
    FIXTURES_DIR="${CALIBRATE_FIXTURES_DIR}"
fi

cd "$PROJECT_DIR"
exec python3 -m core.watch --test-fixtures --fixtures-dir "$FIXTURES_DIR"
