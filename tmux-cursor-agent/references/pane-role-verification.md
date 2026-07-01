# Pane Role Verification

How to verify cursor-agent role assignments before registering panes in the monitor daemon.

## The Problem

When setting up pane-level monitoring for multi-agent windows, manually-set pane titles (e.g., `tmux select-pane -T "PM 产品经理"`) may be wrong. Cursor-agent dynamically overrides pane titles after initialization based on its actual role loading. The resulting title suffix (` - ✅ Ready`) reveals the true role.

Initial assumptions about which pane holds which role are frequently wrong. Example: in a 10-pane summit window, the initial setup labeled pane 0 as "PM" but cursor-agent later set it to "Trend Researcher".

## The Fix: Ask Each Agent to Self-Identify

Before registering any pane in the monitor group:

### 1. Scan ALL panes first

```bash
tmux list-panes -t session:0 -F '#{pane_index}: #{pane_title}'
```

This reveals the actual count — don't assume you know how many panes exist.

### 2. Ask each pane "你是谁"

Use the four-step messaging protocol:

```bash
# Type the question (NO Enter yet)
tmux send-keys -t session:0.0 "你是谁？请用一句话介绍你的角色职责"
sleep 2

# Press Enter on ALL panes simultaneously
for i in 0 1 2 3 4 5 6 7 8 9; do
  tmux send-keys -t session:0.$i Enter
done

# Wait for agents to process (10-15s for cursor-agent)
sleep 15

# Capture each pane's response
for i in 0 1 2 3 4 5 6 7 8 9; do
  echo "=== Pane $i ==="
  tmux capture-pane -t session:0.$i -p -S -10
  echo ""
done
```

### 3. Read the actual role from each response

Each agent will respond with something like:
```
我是 Trend Researcher（趋势研究员）：通过上网检索行业趋势...
```

The pane title suffix (`Trend Researcher - ✅ Ready`) also confirms the role.

### 4. Register with verified labels

```bash
python3 -m core.monitor add --group summit session 0 --pane 0 --label "TREND"
python3 -m core.monitor add --group summit session 0 --pane 1 --label "ARCH"
# ... for each verified role
```

## Why Manual Labels Are Wrong

1. **Initial setup guesses**: The operator assigns pane labels based on intent ("I'll put PM in pane 0"), but cursor-agent may load roles in a different order.
2. **Dynamic overrides**: Cursor-agent updates pane titles after initialization, overriding manual labels with actual role names.
3. **Mid-conference changes**: Agents can be reassigned to different tasks, changing their pane title and role.

## Always Verify

Never trust pane labels set before cursor-agent starts. After cursor-agent is running and logged in for all panes:

1. Wait for all panes to show `✅ Ready` (stopped/idle state)
2. Ask "你是谁" to every pane
3. Read the actual role from each response
4. Register with the verified labels
