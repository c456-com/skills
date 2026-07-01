#!/usr/bin/env bash
# c456-summit-layout — 动态 tmux 布局管理器
# 用法:
#   layout.sh grid          → 网格模式（自动计算最佳行/列）
#   layout.sh cols          → 多列模式（根据宽度和最小列宽自动分列/分行）
#   layout.sh focus <pane>  → 聚焦某窗口（zoom）
#   layout.sh zoom          → 恢复 zoom 前布局

SESSION="c456-summit"
WINDOW="Agents"
id() { echo "$SESSION:$WINDOW"; }

cmd_cols() {
  local panes
  panes=$(tmux list-panes -t "$(id)" | wc -l | tr -d ' ')
  local width
  width=$(tmux display-message -p -t "$(id)" '#{window_width}')
  local min_width=50  # 每列最小宽度
  local max_cols=$(( width / min_width ))

  if [ "$max_cols" -ge "$panes" ]; then
    # 一行排得下 → 多列
    tmux select-layout -t "$(id)" even-horizontal
  else
    # 排不下 → 自动计算行数
    local rows=$(( (panes + max_cols - 1) / max_cols ))
    # 用 tiled 自动排列
    tmux select-layout -t "$(id)" tiled
  fi
}

cmd_grid() {
  tmux select-layout -t "$(id)" tiled
}

cmd_focus() {
  local pane="$1"
  if [ -z "$pane" ]; then
    echo "用法: focus <pane_index|role_keyword>"
    return 1
  fi
  # 支持按角色名模糊匹配
  if ! [[ "$pane" =~ ^[0-9]+$ ]]; then
    pane=$(tmux list-panes -t "$(id)" -F '#{pane_index} #{pane_title}' | \
      grep -i "$pane" | head -1 | awk '{print $1}')
  fi
  if [ -n "$pane" ]; then
    tmux resize-pane -Z -t "$(id).$pane"
  fi
}

cmd_zoom() {
  # 恢复 zoom（tmux 的 zoom 是 toggle，再按一次恢复）
  local active_pane
  active_pane=$(tmux display-message -p -t "$(id)" '#{pane_index}')
  tmux resize-pane -Z -t "$(id).$active_pane"
}

case "${1:-grid}" in
  grid)    cmd_grid ;;
  cols)    cmd_cols ;;
  focus)   cmd_focus "$2" ;;
  zoom)    cmd_zoom ;;
  *)
    echo "用法: $0 {grid|cols|focus <pane>|zoom}"
    exit 1
    ;;
esac
