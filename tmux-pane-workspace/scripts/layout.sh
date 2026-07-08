#!/usr/bin/env bash
# tmux-pane-workspace layout helper
# 用法:
#   TMUX_WORKSPACE_SESSION=roundtable TMUX_WORKSPACE_WINDOW=Agents bash layout.sh grid
#   bash layout.sh cols
#   bash layout.sh focus <pane_index|role_keyword>
#   bash layout.sh zoom

set -euo pipefail

SESSION="${TMUX_WORKSPACE_SESSION:-roundtable}"
WINDOW="${TMUX_WORKSPACE_WINDOW:-0}"
MIN_WIDTH="${TMUX_WORKSPACE_MIN_WIDTH:-50}"

target_window() {
  echo "$SESSION:$WINDOW"
}

cmd_cols() {
  local panes width max_cols
  panes=$(tmux list-panes -t "$(target_window)" | wc -l | tr -d ' ')
  width=$(tmux display-message -p -t "$(target_window)" '#{window_width}')
  max_cols=$(( width / MIN_WIDTH ))

  if [ "$max_cols" -lt 1 ]; then
    max_cols=1
  fi

  if [ "$max_cols" -ge "$panes" ]; then
    tmux select-layout -t "$(target_window)" even-horizontal
  else
    tmux select-layout -t "$(target_window)" tiled
  fi
}

cmd_grid() {
  tmux select-layout -t "$(target_window)" tiled
}

cmd_focus() {
  local pane="$1"
  if [ -z "$pane" ]; then
    echo "用法: focus <pane_index|role_keyword>" >&2
    return 1
  fi

  if ! [[ "$pane" =~ ^[0-9]+$ ]]; then
    pane=$(tmux list-panes -t "$(target_window)" -F '#{pane_index} #{pane_title}' | \
      grep -i "$pane" | head -1 | awk '{print $1}')
  fi

  if [ -z "$pane" ]; then
    echo "未找到匹配 pane" >&2
    return 1
  fi

  tmux select-pane -t "$(target_window).$pane" \; resize-pane -Z
}

cmd_zoom() {
  tmux resize-pane -Z
}

case "${1:-grid}" in
  grid)  cmd_grid ;;
  cols)  cmd_cols ;;
  focus) cmd_focus "${2:-}" ;;
  zoom)  cmd_zoom ;;
  *)
    echo "用法: $0 {grid|cols|focus <pane>|zoom}" >&2
    exit 1
    ;;
esac
