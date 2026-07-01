# Cross-Platform State Detection

cursor-agent pane state detection differs between macOS and Linux:

## macOS

cursor-agent updates the pane title with status suffixes:
- ` - ✅ Ready` (idle)
- ` - ⏳ Working ···` (executing)

Detection via title (fast, no content scan needed):
```bash
title=$(tmux display-message -p -t session:0.pane '#{pane_title}')
echo "$title" | grep -qE "⏳|[⠘⠠⠙⠸⠴⠦]" && echo "EXECUTING"
```

## Linux

cursor-agent keeps the pane title as `Cursor Agent` throughout. Detection requires content scanning:

```bash
content=$(tmux capture-pane -t session:0.pane -p -S -5)
echo "$content" | grep -qE "(Working|Reading|Thinking|Editing)" && echo "EXECUTING"
```

## Dual-Mode Fallback (Recommended)

```bash
_is_working() {
  local title
  title=$(tmux display-message -p -t "$(id).$1" '#{pane_title}')
  # macOS: title suffix
  if echo "$title" | grep -qE "⏳|[⠘⠠⠙⠸⠴⠦]"; then return 0; fi
  # Linux: content scan
  if echo "$title" | grep -qvE "✅|⏳"; then
    local content
    content=$(tmux capture-pane -t "$(id).$1" -p -S -5 2>/dev/null)
    if echo "$content" | grep -qE "(Working|Reading|Thinking|Editing)"; then return 0; fi
  fi
  return 1
}
```

## Key Settings

For cursor-agent's title updates to work (macOS) or not get overwritten (Linux):
- `automatic-rename off` on each window
- `allow-rename on` globally
- `pane-border-status top` to show titles
