#!/usr/bin/env bash
# calibrate-cursor-states.sh — 逐步交互式 UI 校准（停稳再发下一条）
#
# 原则:
#   1. 空沙箱 /tmp/cursor-calibrate-sandbox，禁止改真实项目
#   2. 每条 prompt 前确认 STOPPED（无 spinner/状态词）
#   3. 发一条 → 等停稳 → capture → 再发下一条
#
# 用法: bash calibrate-cursor-states.sh [phase]
#   phase: boot | auto | plan | ask | debug | approval | all

set -euo pipefail

SESSION="${CALIBRATE_SESSION:-cursor-calibrate}"
TARGET="${SESSION}:0"
SANDBOX="/tmp/cursor-calibrate-sandbox"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FIXTURES_DIR="${PROJECT_DIR}/fixtures/calibrate"
CAPTURE="${SCRIPT_DIR}/calibrate-capture.sh"
LIB="${PROJECT_DIR}/core/cursor-watch-lib.sh"
# shellcheck source=cursor-watch-lib.sh
source "$LIB"

STABLE_SECS="${STABLE_SECS:-4}"      # 连续 N 秒 STOPPED 才算停稳
EXEC_TIMEOUT="${EXEC_TIMEOUT:-90}"
DONE_TIMEOUT="${DONE_TIMEOUT:-180}"
POLL=1

_log() { echo "[calibrate $(date +%H:%M:%S)] $*"; }

_pane_bottom() {
    tmux capture-pane -t "$TARGET" -p -S -20 | tail -12
}

_is_executing_pane() {
    is_executing "$(_pane_bottom)"
}

_is_followups_queue() {
    _pane_bottom | grep -q 'follow-ups'
}

_wait_executing() {
    local max="${1:-$EXEC_TIMEOUT}" i=0
    while [ "$i" -lt "$max" ]; do
        _is_executing_pane && return 0
        sleep "$POLL"
        i=$((i + POLL))
    done
    _log "WARN: executing not seen within ${max}s"
    return 1
}

_wait_stable_stopped() {
    local max="${1:-$DONE_TIMEOUT}"
    local stable=0 i=0
    while [ "$i" -lt "$max" ]; do
        if _is_executing_pane; then
            stable=0
        elif _is_followups_queue; then
            _log "WARN: follow-ups queue detected — waiting (do not send next prompt)"
            stable=0
        else
            stable=$((stable + POLL))
            [ "$stable" -ge "$STABLE_SECS" ] && return 0
        fi
        sleep "$POLL"
        i=$((i + POLL))
    done
    _log "WARN: not stable-stopped within ${max}s"
    return 0
}

_send_one() {
    local text="$1"
    _log "wait stable before send..."
    _wait_stable_stopped "$DONE_TIMEOUT"
    if _is_followups_queue; then
        _log "ERROR: follow-ups queue still present, skip send: ${text:0:50}..."
        return 1
    fi
    _log "send: ${text:0:60}..."
    tmux send-keys -t "$TARGET" "$text"
    sleep 2
    tmux send-keys -t "$TARGET" Enter
}

_mode() {
    local cmd="$1"
    _wait_stable_stopped 60
    _log "mode: $cmd"
    tmux send-keys -t "$TARGET" "$cmd"
    sleep 1
    tmux send-keys -t "$TARGET" Enter
    sleep 4
    _wait_stable_stopped 30
}

_capture() {
    local name="$1" mode="$2" expected="$3" reason="${4:-}" note="${5:-}"
    CALIBRATE_SESSION="$SESSION" CALIBRATE_WINDOW=0 CALIBRATE_FIXTURES_DIR="$FIXTURES_DIR" \
        bash "$CAPTURE" "$name" "$mode" "$expected" "$reason" "$note"
}

_boot_session() {
    mkdir -p "$FIXTURES_DIR/meta"
    if tmux has-session -t "$SESSION" 2>/dev/null; then
        tmux kill-session -t "$SESSION"
        sleep 1
    fi
    tmux new-session -d -s "$SESSION" -n calibrate \
        "cd ${SANDBOX} && exec cursor-agent"
    _log "waiting for cursor-agent TUI..."
    sleep 12
    # Workspace Trust 对话框：按 a 信任
    if tmux capture-pane -t "$TARGET" -p -S -20 | grep -q 'Workspace Trust'; then
        _log "trusting workspace..."
        tmux send-keys -t "$TARGET" a
        sleep 5
    fi
    _wait_stable_stopped 60
    _capture boot-stopped-idle auto stopped idle "沙箱启动后空闲"
}

_INTRO='【UI校准沙箱】这是监控检测专用空目录。请只读 README.md 配合模拟，禁止创建/编辑/删除任何文件，禁止运行 shell 命令。'

phase_auto() {
    _log "=== AUTO ==="
    # 确保在 Auto 模式
    local bottom=$(_pane_bottom)
    if echo "$bottom" | grep -qE 'Plan |Ask |Debug '; then
        until echo "$bottom" | grep -qE 'Auto '; do
            tmux send-keys -t "$TARGET" BTab
            sleep 2
            bottom=$(_pane_bottom)
        done
        _wait_stable_stopped 20
    fi

    _send_one "${_INTRO} 场景 auto-S01：保持空闲，不要做任何事。"
    _wait_stable_stopped 30
    _capture auto-stopped-S01 auto stopped idle "Auto 空闲"

    _send_one "场景 auto-E01：思考 10 秒后只回答数字 7。不要改文件。"
    _wait_executing 45 || true
    _capture auto-executing-E01 auto executing "" "Thinking spinner"
    _wait_stable_stopped "$DONE_TIMEOUT"
    _capture auto-stopped-S02 auto stopped idle "思考完成后静止"

    _send_one "场景 auto-E02：只读 README.md 第一句话，用中文复述。不要改文件。"
    _wait_executing 45 || true
    _capture auto-executing-E02 auto executing "" "Reading"
    _wait_stable_stopped "$DONE_TIMEOUT"
    _capture auto-stopped-S03 auto stopped idle "读完后静止"
}

phase_plan() {
    _log "=== PLAN ==="
    _mode "/plan"
    _send_one "${_INTRO} 场景 plan-S01：Plan 模式保持空闲。"
    _wait_stable_stopped 30
    _capture plan-stopped-S01 plan stopped idle "Plan 空闲"

    _send_one "场景 plan-S02：为 README 写安装章节计划。需求故意模糊，必须先问我 2 个澄清问题（用 AskQuestion 多选），不要写文件。"
    _wait_executing 60 || true
    _capture plan-executing-E01 plan executing "" "读 README 调研中" || true
    _wait_stable_stopped 120

    # 等待 Question 界面
    local pane
    pane=$(tmux capture-pane -t "$TARGET" -p -S -50)
    if echo "$pane" | grep -qE 'Question [0-9]+ of [0-9]+|AskQuestion'; then
        _capture plan-stopped-S02-question plan stopped needs_input "Question 多选界面"
    else
        _log "WARN: Question UI not found; run calibrate-plan-question.sh"
        _capture plan-stopped-S02-miss plan stopped needs_input "未抓到 Question"
    fi

    # 不自动答题 — 留给用户或下一步手动；为抓 Ready to build 需要完整走完
    # 发送明确需求跳过问题直接出计划（若还在 question 则 esc）
    _send_one "场景 plan-E02：跳过提问，直接为 README 安装章节生成文字计划（纯文本输出即可，不要写文件到磁盘）。"
    _wait_executing 90 || true
    _capture plan-executing-E02 plan executing "" "生成计划中"
    _wait_stable_stopped 180

    pane=$(tmux capture-pane -t "$TARGET" -p -S -50)
    if echo "$pane" | grep -qi 'ready to build'; then
        _capture plan-stopped-S05 plan stopped needs_input "Ready to build"
    elif echo "$pane" | grep -qi 'revise the plan'; then
        _capture plan-stopped-S04 plan stopped needs_input "revise placeholder"
    else
        _capture plan-stopped-S06 plan stopped idle "计划输出后静止"
    fi
}

phase_ask() {
    _log "=== ASK ==="
    _mode "/ask"
    _send_one "${_INTRO} 场景 ask-S01：Ask 模式保持空闲。"
    _wait_stable_stopped 30
    _capture ask-stopped-S01 ask stopped idle "Ask 空闲"

    _send_one "场景 ask-E01：只读 README.md 并一句话说明用途。不要改任何文件。"
    _wait_executing 45 || true
    _capture ask-executing-E01 ask executing "" "Ask Reading"
    _wait_stable_stopped "$DONE_TIMEOUT"
    _capture ask-stopped-S02 ask stopped idle "Ask 回答完成"
}

phase_debug() {
    _log "=== DEBUG ==="
    _mode "/debug"
    _send_one "${_INTRO} 场景 debug-S01：Debug 模式保持空闲。"
    _wait_stable_stopped 30
    _capture debug-stopped-S01 debug stopped idle "Debug 空闲"

    _send_one "场景 debug-E01：阅读 README.md，分析「若 sandu --help 失败可能有哪些原因」（纯推理，不要运行命令）。"
    _wait_executing 45 || true
    _capture debug-executing-E01 debug executing "" "Debug 分析中"
    _wait_stable_stopped "$DONE_TIMEOUT"
    _capture debug-stopped-S02 debug stopped idle "Debug 完成"
}

phase_approval() {
    _log "=== APPROVAL (Auto, no Run Everything) ==="
    _mode "/ask"
    tmux send-keys -t "$TARGET" BTab; sleep 1
    tmux send-keys -t "$TARGET" BTab; sleep 1
    tmux send-keys -t "$TARGET" BTab; sleep 3
    _wait_stable_stopped 30
    # Turn off run everything if on - send /run-everything to toggle? or leave as is
    _send_one "场景 auto-S03：运行命令 ls -la（需要批准的话会弹框）。不要改文件。"
    _wait_stable_stopped 60
    local pane
    pane=$(tmux capture-pane -t "$TARGET" -p -S -30)
    if echo "$pane" | grep -qE 'Run this command|Run \(once\)'; then
        _capture auto-stopped-S03-approval auto stopped needs_approval "命令批准框"
        # 拒绝批准：按 n 或 esc
        tmux send-keys -t "$TARGET" n
        sleep 2
        _wait_stable_stopped 30
    else
        _log "WARN: approval UI not shown (Run Everything may be on)"
        _capture auto-stopped-S03-no-approval auto stopped idle "未出现批准框"
    fi
}

PHASE="${1:-all}"
case "$PHASE" in
    boot) _boot_session ;;
    auto) phase_auto ;;
    plan) phase_plan ;;
    ask) phase_ask ;;
    debug) phase_debug ;;
    approval) phase_approval ;;
    all)
        _boot_session
        phase_auto
        phase_plan
        phase_ask
        phase_debug
        phase_approval
        _log "DONE. fixtures in ${FIXTURES_DIR}"
        ls -1 "$FIXTURES_DIR"/*.txt 2>/dev/null | wc -l
        ;;
    *) echo "unknown phase: $PHASE" >&2; exit 1 ;;
esac
