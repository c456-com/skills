#!/usr/bin/env bash
# 单独抓取 Plan Question 多选界面（一条 prompt，等停稳再抓，不连发）
set -euo pipefail
SESSION=cursor-calibrate
TARGET="${SESSION}:0"
SANDBOX=/tmp/cursor-calibrate-sandbox
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FIXTURES_DIR="${PROJECT_DIR}/fixtures/calibrate"
CAPTURE="${SCRIPT_DIR}/calibrate-capture.sh"
LIB="${PROJECT_DIR}/core/cursor-watch-lib.sh"
source "$LIB"

_wait_stable() {
    local s=0 i=0
    while [ "$i" -lt 180 ]; do
        if is_executing "$(tmux capture-pane -t "$TARGET" -p -S -15 | tail -10)"; then
            s=0
        else
            s=$((s+1))
            [ "$s" -ge 4 ] && return 0
        fi
        sleep 1; i=$((i+1))
    done
}

# 确保 Plan 模式
tmux send-keys -t "$TARGET" "/plan"; sleep 1; tmux send-keys -t "$TARGET" Enter; sleep 4
_wait_stable

echo "send question-only prompt..."
tmux send-keys -t "$TARGET" "场景 plan-question：为「部署到生产环境」写计划。我只说了这一句话，细节全无。你必须用 AskQuestion 问我至少 2 个多选问题，在我回答前不要生成计划、不要读很多文件、不要写文件。"
sleep 2
tmux send-keys -t "$TARGET" Enter

echo "waiting for Question UI..."
for i in $(seq 1 120); do
    pane=$(tmux capture-pane -t "$TARGET" -p -S -50)
    if echo "$pane" | grep -qE 'Question [0-9]+ of [0-9]+'; then
        echo "AskQuestion tool UI found at ${i}s"
        CALIBRATE_FIXTURES_DIR="$FIXTURES_DIR" CALIBRATE_SESSION="$SESSION" \
            bash "$CAPTURE" plan-stopped-S02-question plan stopped needs_input "AskQuestion 多选界面"
        exit 0
    fi
    if is_executing "$(echo "$pane" | tail -10)"; then
        sleep 1
        continue
    fi
    sleep 1
done

echo "WARN: timeout, capture fallback"
CALIBRATE_FIXTURES_DIR="$FIXTURES_DIR" CALIBRATE_SESSION="$SESSION" \
    bash "$CAPTURE" plan-stopped-S02-miss plan stopped needs_input "未等到 Question"
