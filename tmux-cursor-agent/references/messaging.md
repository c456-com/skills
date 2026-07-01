# Messaging Protocol Reference

## Four steps (mandatory)

```
① capture-pane → verify STOPPED + clean input box
② send-keys "text" (NO Enter!)
③ sleep 2
④ send-keys Enter → capture-pane verify
```

## Selection menu handling

| Action | Command |
|--------|---------|
| Navigate up | `send-keys Up` |
| Navigate down | `send-keys Down` |
| Toggle select | `send-keys Space` |
| Submit | `send-keys Enter` |
| Skip | `send-keys Escape` |

**Don't send numbers** — they go into "Other" input field, not menu selection.

## Cancel operations

| Action | Command | Effect |
|--------|---------|--------|
| Cancel execution | `send-keys C-c` | Stops current agent task |
| Clear input | `send-keys Escape` | Clears unsubmitted text from input bar |
| Exit gracefully | `send-keys "/exit" Enter` | Saves session, prints resume ID |
| Force exit | `send-keys C-c` then `C-c` again | Kills agent without saving |

## Anti-pattern: sending shell commands to cursor-agent

**Never use `tmux send-keys` to send shell commands** (`echo`, `cat`, heredoc, variable assignments) to a cursor-agent pane.

| ❌ Wrong (shell command) | Why it fails |
|---|---|
| `tmux send-keys -t pane \"cat file\" Enter` | Executes `cat file` in the shell behind cursor-agent, not as an agent message |
| `tmux send-keys -t pane \"echo 'hello'\" Enter` | Shell echo, never reaches agent conversation |
| Heredoc via `tmux send-keys` | Still a shell command; agent never sees it |

| ✅ Correct (four-step protocol) | What happens |
|---|---|
| `tmux send-keys -t pane \"Your message\"` (NO Enter) | Text queued in agent input buffer |
| `sleep 2` | Wait for agent to be ready |
| `tmux send-keys -t pane Enter` | Submit to agent conversation |
| `tmux capture-pane -t pane -p -S -3` | Verify message is in history, not stuck in input |

**How to tell you made this mistake**: The pane shows `cat /tmp/file` or `echo 'text'` as if typed in a shell, and cursor-agent's `→ Add a follow-up` prompt disappears or the message appears as shell output rather than conversation history.

**Recovery**: `tmux send-keys C-c` to cancel any running shell command, then `Escape` to clear input, then re-send using the four-step protocol with plain text only.

| Symptom | Cause | Fix |
|---------|-------|-----|
| Text in input bar (`→` prefix) | Enter swallowed | Send another Enter |
| `command not found` | Wrong pane (shell, not agent) | Check `pane_current_command` |
| No response | Agent still EXECUTING | Wait, or send C-c to cancel |
| Text queued as follow-up | Message sent during background tasks | Send Enter again to activate |
