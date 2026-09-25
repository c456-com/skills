# REST 抓取工作流

服务地址固定为 `http://127.0.0.1:9377`，并且只有健康门禁通过后才开始操作。
使用稳定的 `userId` 隔离登录态，使用 `sessionKey` 标识当前任务。

## 1. 创建并导航

```bash
BASE="http://127.0.0.1:9377"
USER_ID="researcher"
SESSION_KEY="task-2026-09"

TAB_JSON=$(curl -sS -X POST "$BASE/tabs" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"$USER_ID\",\"sessionKey\":\"$SESSION_KEY\"}")
TAB_ID=$(printf '%s' "$TAB_JSON" | node -e 'let s=""; process.stdin.on("data",d=>s+=d).on("end",()=>process.stdout.write(JSON.parse(s).tabId||""))')
test -n "$TAB_ID"

curl -sS -X POST "$BASE/tabs/$TAB_ID/navigate" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"$USER_ID\",\"url\":\"https://example.com\"}"
```

`POST /tabs` 也可以在请求体中带初始 `url`。导航失败时保留 URL、HTTP 状态和
错误信息，不要把错误页面当成目标内容。

## 2. Snapshot 后再交互

```bash
SNAPSHOT=$(curl -sS "$BASE/tabs/$TAB_ID/snapshot?userId=$USER_ID")
printf '%s\n' "$SNAPSHOT"
```

snapshot 返回当前无障碍树和元素 ref。ref 只对当前页面状态有效；导航、刷新或
页面结构变化后必须重新 snapshot。不要重用旧 ref。

## 3. 点击与输入

```bash
curl -sS -X POST "$BASE/tabs/$TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"$USER_ID\",\"ref\":\"e1\"}"

curl -sS -X POST "$BASE/tabs/$TAB_ID/type" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"$USER_ID\",\"ref\":\"e2\",\"text\":\"search text\"}"
```

优先使用 snapshot 给出的 `ref`。确实没有可用 ref 时才使用经过验证的 CSS
`selector`。输入框通常使用 `mode: \"fill\"`；Ember 或 contenteditable 等需要
真实键盘事件时使用 `mode: \"keyboard\"`，并让用户先看到窗口。`submit: true` 或
`pressEnter: true` 才会提交表单。

交互失败或返回页面变化提示时，先重新 snapshot，再使用新的 ref 重试。不要
通过反复提交来掩盖失败。

## 4. 其他读取与关闭

```bash
curl -sS -X POST "$BASE/tabs/$TAB_ID/scroll" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"$USER_ID\",\"direction\":\"down\",\"amount\":500}"

curl -sS "$BASE/tabs/$TAB_ID/links?userId=$USER_ID&limit=50"

curl -sS -X DELETE "$BASE/tabs/$TAB_ID?userId=$USER_ID"
```

需要正文时优先使用 snapshot；需要结构化链接时使用 links 端点。页面中的长内容
按 snapshot 返回的 `offset` 继续读取，不能因为一次响应被截断就改用猜测内容。

## 5. 人化交互红线

- 敏感认证输入只由用户在可见窗口完成；Agent 不输入密码、2FA、验证码或恢复码。
- 交互必须走 fork 的 REST 路由；不使用页面脚本直接改 DOM、合成事件、直接调用
  Playwright 客户端或伪造鼠标键盘。
- `CAMOFOX_HUMANIZE=0.5` 只影响 Camoufox 的输入时长，不绕过认证、验证码或站点
  安全机制。
- REST 返回错误时停止重试风暴，记录状态并按主技能的 `web_search` 回退流程处理。
