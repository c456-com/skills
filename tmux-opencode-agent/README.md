# tmux-opencode-agent

> **在 tmux 里驱动与监控 OpenCode —— 可见 TUI 编排、SSE 终态判定、权限/提问面板处置。**

一套把活派给 [OpenCode](https://opencode.ai) 并把它的状态看准的操作手册。区别于
`tmux-cursor-agent`：OpenCode 的判据是 **SSE 事件流 + 屏上模式行**，不是 hook 文件；两者不可互相照搬。

## 适用场景

- 把一个开发/评审任务派给 tmux 里的 OpenCode，并要精准知道**它哪一轮说完了**
- 处理 `Permission required` 权限面板与 `AskUserQuestion` 提问面板（SSE 看不见提问面板，只能靠屏）
- 一个项目并行多个 OpenCode，需要按会话分开归因、避免串台
- 换机/换版本后要复验 OpenCode 的事件能力与键位

## 核心结论速览

| 主题 | 结论 |
|------|------|
| 会话形态 | 同一工作目录启动的 opencode **合并成一个 TUI**，用顶部 tab 并排；进程数 ≠ 会话数 |
| 轮次结束 | SSE 出现 `session.execution.succeeded` 或 `session.execution.interrupted` |
| 假终态 | `tool.failed` / `step.failed` 不是结束；主轮 `succeeded` 时子会话可能还在跑 |
| 取消执行 | `Esc` 两次（屏底出现 `esc again to interrupt` 再按一次）；**不是** `Ctrl+C` |
| 权限面板 | 按 Patterns 行的范围分诊；家目录级 `~/*` 一律 `Reject` |
| 提问面板 | 必须逐项选中提交，禁止 `esc dismiss`；面板选择一律配散文兜底 |
| 发送安全 | 正文禁用 `!` `#` `$` 等触发字符；发前核模式行是 `Build`，发后核 token 增量 |

## 快速开始

```bash
# 1. 起可见 TUI（cwd 必须是被派活的工作树）
tmux new-session -d -s oc -n agent -c /path/to/worktree
tmux send-keys -t oc:0 "opencode"; sleep 2; tmux send-keys -t oc:0 Enter; sleep 15

# 2. 核模型（屏底 Build · <模型名>），派活（纯中文、无 ! # 前缀）

# 3. 取会话 id（真源 = 服务端清单，不取自己的笔记）
URL=$(opencode service status | tr -d '[:space:]')
PW=$(python3 -c "import json;print(json.load(open('$HOME/.config/opencode/service.json'))['password'])")
curl -s -u "opencode:$PW" "$URL/api/session" | python3 -m json.tool

# 4. 挂监控探针（锚点会先做存在性与目录校验）
python3 scripts/watch.py <session_id> 86400 --tmux-session oc --expect-dir /path/to/worktree
```

## 目录结构

```
SKILL.md                          # 主手册（本技能的全部判据与配方）
references/session-identity.md    # 会话身份验真与归属判定
references/panel-selection-and-answers.md  # 权限/提问面板选中项解析与答复配方
references/opencode-v2-credentials.md      # v2 凭据真源、账号切换与额度判定
references/stage-done-false-terminal.md    # 假终态成因与派生规则
scripts/watch.py                  # 常驻监控探针（SSE 主通道）
scripts/screen_watch.py           # 屏副路轮询（识别提问面板）
```

## 相关技能

- `tmux-cursor-agent` — Cursor 版运行时手册（判据不同，共享通用坑）
- `tmux-pane-workspace` — 通用 pane 可见性、布局与会议协作

## 许可

MIT
