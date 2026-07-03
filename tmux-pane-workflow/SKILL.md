---
name: tmux-pane-workflow
description: "Tmux pane 操作规范：zoom 前后、发前检查 agent 状态、发后验证送达。独立于任何项目，适用于所有 tmux + cursor-agent 协作场景。"
version: 1.0.0
---

# Tmux Pane Workflow

> 与 [tmux-cursor-agent](https://github.com/c456-com/skills/tree/main/tmux-cursor-agent) 配套使用。  
> 本技能只定义 pane 操作的基本规范，不含项目特定的文档模板或流程。

## Zoom before talking

To focus a specific pane before sending a message:

```bash
# ✅ CORRECT — select then zoom in one chain
tmux select-pane -t session:window.pane \; resize-pane -Z

# ❌ WRONG — resize-pane -Z -t pane fails silently when pane not active
```

This works for any pane index: 0.0, 0.1, 0.2, etc. Leave zoomed after sending.

## Zoom before reading

When you `capture-pane` to read a pane's output, **also zoom it first**. This makes your operations visible in tmux — the user sees which pane you're looking at and what you're doing.

```bash
# ✅ CORRECT — zoom before EVERY capture, not just before sending
tmux select-pane -t session:window.pane \; resize-pane -Z
tmux capture-pane -t session:window.pane -p -S -20
```

Rule: every `capture-pane` call should be preceded by zoom (unless already zoomed on that pane). Leave zoomed after reading.

## Check state before sending

Before ANY message, verify the agent's state:

| State | Indicator | Can send? |
|-------|-----------|-----------|
| Working | spinner, "Working"/"Reading"/"Editing"/"Grepping" | ❌ Wait |
| Waiting | "Waiting Nm for shell" | ⚠️ Goes to follow-ups queue |
| Idle | "→ Add a follow-up", no spinner | ✅ Yes |

Capture with: `tmux capture-pane -t session:0.X -p -S -15`

State classification detailed in [tmux-cursor-agent](https://github.com/c456-com/skills/blob/main/tmux-cursor-agent/SKILL.md) skill.

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Forgetting to zoom | Can't read agent output clearly | Always zoom before talking/reading |
| Sending without checking state | Message interrupts agent mid-work | Always capture-pane first |
| Not verifying after sending | Message stuck in input bar | Always capture-pane after Enter |
