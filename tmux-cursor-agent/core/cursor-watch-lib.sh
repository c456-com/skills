#!/usr/bin/env bash
# cursor-watch-lib.sh — 共享状态检测（供 calibrate 脚本与 fixture 对照使用）

# 正向识别 EXECUTING：底部出现活动信号即视为执行中
# 未识别到 = STOPPED
# 排除：placeholder、Run Everything、ctrl+o/ctrl+b 热键提示
is_executing() {
    local bottom="$1"
    # Braille spinner（完整 Unicode 盲文区）
    if echo "$bottom" | grep -qP '[\x{2800}-\x{28FF}]' 2>/dev/null; then
        return 0
    fi
    # 活动状态词（Waited 不匹配 Waiting）
    if echo "$bottom" | grep -qE '(^|[[:space:]])(Working|Running|Thinking|Reading|Globbing|Editing|Waiting|Reconnecting)([[:space:]:]|$)'; then
        return 0
    fi
    # 后台 shell 轮询
    if echo "$bottom" | grep -qE '[0-9]+ background tasks?'; then
        return 0
    fi
    return 1
}

classify_reason() {
    local content="$1"
    local bottom="$2"
    if echo "$bottom" | grep -q 'Press Ctrl+C again to exit'; then
        echo "exited"
    elif echo "$bottom" | grep -qE 'Run this command\?|Run \(once\) \(y\)'; then
        echo "needs_approval"
    elif echo "$content" | grep -qE 'Question [0-9]+ of [0-9]+|Enter to submit, Esc to cancel|AskQuestion|待你|请回复|需要你|确认|拍板|Ready to build'; then
        echo "needs_input"
    elif echo "$content" | grep -qE '任务完成|已完成|正式关单|All tests passed|✅|done\.|已完成。'; then
        echo "task_done"
    else
        echo "idle"
    fi
}

# 输入框有未提交文字（非 placeholder）→ 有人在控制，不应触发 STOPPED 通知
has_unsubmitted_input() {
    local bottom="$1"
    local line text
    while IFS= read -r line; do
        [[ "$line" == *"│"* ]] && continue
        if [[ "$line" =~ ^[[:space:]]*→[[:space:]]*(.+)$ ]]; then
            text="${BASH_REMATCH[1]}"
            text="${text% ctrl+c to stop}"
            text="${text%"${text##*[![:space:]]}"}"
            [[ -z "$text" ]] && continue
            if echo "$text" | grep -qE '^Add a follow-up([[:space:]]*[—–-][[:space:]]*/plan to review and build)?$'; then
                continue
            fi
            if echo "$text" | grep -qiE '^Describe how to revise'; then
                continue
            fi
            if echo "$text" | grep -qE '^Plan, search, build anything$'; then
                continue
            fi
            return 0
        fi
    done <<< "$bottom"
    return 1
}
