#! /usr/bin/env bash
# git-raw-policy.sh — Check raw/ size and suggest exclusion
# Usage: bash git-raw-policy.sh <project-root>

set -euo pipefail
ROOT="${1:-.}"

for dir in "$ROOT/raw" "$ROOT"/domains/*/raw; do
    [ -d "$dir" ] || continue
    size=$(du -sh "$dir" 2>/dev/null | cut -f1)
    echo "$dir: $size"
done
