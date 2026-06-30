# Messaging Protocol

The **four-step protocol** is the only reliable way to send messages to a cursor-agent pane. Direct `send-keys "text" Enter` will frequently fail because the Enter key gets "swallowed" by tmux when the agent is processing.

## The Four Steps

```
┌──────────────────────────────────────────────┐
│  1. CAPTURE: Verify state + clean input box   │
│  2. SEND: Type message (NO Enter!)            │
│  3. WAIT: Sleep 2 seconds                     │
│  4. SUBMIT: Press Enter, then verify          │
└──────────────────────────────────────────────┘
```

### Step 1: Pre-flight Check

Before sending anything, verify the agent is ready:

```bash
# Check the last 5 lines of the pane
tmux capture-pane -t cursor:0 -p -S -5

# Verify these conditions:
# 1. No spinner/Working/Running (agent is STOPPED)
# 2. Input bar shows only placeholder (→ Add a follow-up), NOT user text
# 3. No "Waiting" with background tasks (agent is busy)
```

**Do NOT send if:**
- Agent is EXECUTING (spinner / `Working` / `Reading` / `Editing` visible) — wait for it to finish
- `Waiting` + background tasks visible — messages will queue, not be processed
- Input bar has unsubmitted text (`→ your-text`) — clear with `Escape` first

### Step 2: Type the Message

```bash
# Send the message text WITHOUT a trailing Enter
tmux send-keys -t cursor:0 "Implement user authentication with JWT tokens"

# ⚠️ DO NOT add "Enter" here!
# Wrong: tmux send-keys -t cursor:0 "text" Enter
```

### Step 3: Wait

```bash
# Give tmux time to buffer the text
sleep 2
```

The delay is needed because tmux processes keystrokes asynchronously. Without this pause, the Enter from Step 4 might arrive before the text is fully buffered.

### Step 4: Submit and Verify

```bash
# Press Enter to submit
tmux send-keys -t cursor:0 Enter

# Wait for the agent to begin processing
sleep 3

# Verify the message was sent
tmux capture-pane -t cursor:0 -p -S -5

# ✅ Success: Message appears in conversation history + "Working" spinner visible
# ❌ Failure: Text still in input bar (→ prefix) → retry with another Enter
```

## Cancelling Operations

### Cancel Current Execution

When the agent is working and you need to stop it:

```bash
# Send Ctrl+C once
tmux send-keys -t cursor:0 C-c

# Wait a moment
sleep 1

# The agent should show "Press Ctrl+C again to exit"
# OR it stopped the current operation and returned to idle
```

### Cancel Unsubmitted Input

If you typed text but haven't submitted it yet:

```bash
# Press Escape to clear the input box
tmux send-keys -t cursor:0 Escape

# Verify: input bar should show only placeholder
tmux capture-pane -t cursor:0 -p -S -3
```

### Force Exit

If the agent is unresponsive:

```bash
# First Ctrl+C
tmux send-keys -t cursor:0 C-c
sleep 1

# Second Ctrl+C triggers exit
tmux send-keys -t cursor:0 C-c
sleep 1

# Or send /exit command
tmux send-keys -t cursor:0 "/exit" Enter
```

## Handling the Selection Menu

Cursor agent's Plan mode uses a terminal UI with selectable options:

```
› [ ] Option 1        ← ↑/↓ to move cursor
  [ ] Option 2
  [ ] Option 3
  [ ] Other: (type to answer)    ← select this to type free-form

↑/↓ option · ←/→ question · Space select · Enter next/submit · Esc to skip
```

**Correct way to interact:**

```bash
# Move cursor up/down
tmux send-keys -t cursor:0 Up
tmux send-keys -t cursor:0 Down

# Toggle selection
tmux send-keys -t cursor:0 Space

# Submit / next
tmux send-keys -t cursor:0 Enter

# Skip
tmux send-keys -t cursor:0 Escape
```

**❌ Do NOT send numbers directly** — `send-keys "3" Enter` will be treated as text input for "Other", not as selecting option 3.

## Handling Follow-ups Queue

When you send a message and it enters a follow-ups queue (showing `○ … enter send now`):

```bash
# Press Enter again to submit as active message
tmux send-keys -t cursor:0 Enter

# Verify it's now processing
sleep 3
tmux capture-pane -t cursor:0 -p -S -5
```

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Text appears with `→` prefix in input bar | Enter was swallowed | Send another Enter |
| Text disappeared completely | Escape was pressed or C-c cleared it | Re-send using four-step |
| `command not found: 中文` | Sent to a zsh pane, not cursor-agent | Verify pane is running cursor-agent first |
| Text appears in conversation but no Working | Message queued as follow-up | Send another Enter |
| Agent shows `Run Everything` but doesn't start | Agent is idle, awaiting message | Send a message — it will start working |
