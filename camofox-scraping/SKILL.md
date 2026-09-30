---
name: camofox-scraping
description: "用户或任意 AI Agent 需要真实浏览器打开、访问、阅读、交互、调试或采集网页时使用；支持 CamoFox / Camoufox、browser automation、headless 与 headed browser、web scraping，覆盖公开或动态网页、有头人工登录、无头浏览、批量抓取，以及 Cloudflare、反爬和登录墙场景。⚠️ 须使用 fork 版 xiaohui-zhangxh/camofox-browser —— 官方 npm 包在 macOS 上有阻断性 bug。"
version: 3.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [scraping, camofox, browser-automation, research, cloudflare, anti-detection]
references:
  - references/fork-v1.17-contract.md
  - references/rest-workflow.md
  - references/persistence-and-login.md
  - references/camofox-api-cheatsheet.md
  - references/ui-automation-pitfalls.md
---

# CamoFox v1.17.0 抓取与可见登录

> ⚠️ **必须使用 fork 版本**：官方 npm 包 `@askjo/camofox-browser` 在 macOS 上有两个阻断性 bug（viewport 协议不兼容、headless 锁死），导致无法显示窗口、无法持久化登录。fork `xiaohui-zhangxh/camofox-browser` 修复了这些问题。不要用 `npx @askjo/camofox-browser` 安装或运行。

Scrape sites using CamoFox anti-detection browser. Camoufox is a patched Firefox binary that resists bot detection.

## 核心契约

- **唯一来源：** [xiaohui-zhangxh/camofox-browser](https://github.com/xiaohui-zhangxh/camofox-browser)；SSH 等价地址为 `git@github.com:xiaohui-zhangxh/camofox-browser.git`。
- **默认落点：** `~/Codes/camofox-browser-fork`。其他机器可以选择自己的绝对 clone 目录，但必须在
  `~/.camofox/camofox-local-root.txt` 记录该目录，并在后续所有命令中使用同一个值。
- **版本门禁：** fork 当前契约为 CamoFox `1.17.0`；安装后先确认版本，再继续。
- **禁止绕过：** 不从其他仓库、发布包、全局安装或临时安装器取得 CamoFox，也不修改 fork 业务源码来适配当前任务。仓内唯一允许的 `npx` 用法是 `npx tsc -p .` 严格 TypeScript 编译门禁。

完整的来源、安装、编译、启动和健康检查契约见
[fork v1.17 契约](references/fork-v1.17-contract.md)。安装、编译、启动或健康检查任一步失败，都停止；不拿已有进程或其他服务代替通过。

## 安装与构建（fail-closed 顺序）

每次安装或更新 fork 都从全新 clone 开始；已有目录必须先由用户决定保留或移走，不能直接复用：

1. 记录并验证唯一来源和 clone 根目录。
2. 进入仓根执行 `npm ci`。
3. 执行严格 `npx tsc -p .`，确认退出码为 `0`。
4. 执行 `npm run build`，确认退出码为 `0` 且 `dist/plugin.js` 存在。
5. 仍在仓根设置 v1.17 配置并用 `npm start` 启动。
6. 只以 `GET /health` 的 HTTP `200`、`ok: true` 和
   `browserConnected: true` 三项同时成立作为就绪证据。

健康检查不通过时，不创建 tab、不登录、不抓取，也不把 `ok: true`
单独当成浏览器已经连接。

## 启动与健康检查（每次用之前先过一遍）

**Hermes 自己的 browser 工具会走这个服务**：`browser.cloud_provider: camofox` + `.env` 里 `CAMOFOX_URL=http://localhost:9377` 时，`browser_navigate/snapshot/click/type/screenshot` 全部由 camofox 服务转发（服务日志里能看到 `POST /tabs`、userId=`hermes_<hash>`）。需要精确控制（fullPage 截图、Cookie 保存/恢复、视口、复用登录态）时才直接打 REST API。

```bash
# 启动（v1.17 现行写法：以 CAMOFOX_INTERACTIVE 控制有无窗口，⛔ 不再有 CAMOFOX_HEADLESS）
cd ~/Codes/camofox-browser-fork
BROWSER_IDLE_TIMEOUT_MS=0 node server.js                    # 无窗口（默认 off）
CAMOFOX_INTERACTIVE=desktop BROWSER_IDLE_TIMEOUT_MS=0 node server.js   # 显示真实窗口
#    其它可选：CAMOFOX_PORT（默认 9377）· CAMOFOX_WINDOW_SIZE=1280,860
#              CAMOFOX_DEVICE_SCALE_FACTOR=2 · CAMOFOX_HUMANIZE=0.5 · CAMOFOX_SHOWCURSOR=1

# 就绪判据：/health 必须三项同时成立 —— HTTP 200 + ok:true + browserConnected:true
# （⛔ 只看 ok:true 不够：fork 有 idle 自动关，浏览器可能已关而服务进程还活着）
curl -s http://127.0.0.1:9377/health
```

**⛔ `CAMOFOX_HEADLESS` 已是死变量**（v1.17 的 `lib/config.js` 不再读取它）。传它不会报错，但**窗口不会出来**——因为 `server.js` 只看 `CONFIG.interactiveMode === 'desktop'`。合法值：`off`（默认）· `desktop`（本机窗口）· `novnc` · `auto`。

| 症状 | 真因 | 处理 |
|------|------|------|
| `health` 返 `ok:true` 但 `browserConnected:false` | **不是挂了** —— fork 有 idle 自动关（`BROWSER_IDLE_TIMEOUT_MS` 默认 300000）：最后一个 tab 关掉 5 分钟后自动关浏览器省内存。服务进程还活着，只是浏览器被关了 | **用 `BROWSER_IDLE_TIMEOUT_MS=0` 启动**（0 = 永不自动关）。本技能不依赖外部启动脚本 |
| 传了 `CAMOFOX_HEADLESS=false` 但**没窗口** | ⛔ v1.17 已不读该变量；`server.js` 只看 `interactiveMode === 'desktop'` | 改用 `CAMOFOX_INTERACTIVE=desktop` |
| 启动即退，日志 `port in use` | 旧进程还占着 9377，新进程静默死掉（**你以为重启了，其实跑的还是旧代码**） | `lsof -ti:9377 \| xargs kill`；要保留旧实例（不影响别的用途）就换端口 `CAMOFOX_PORT=9378` |
| 浏览器起不来，日志 `NODE_MODULE_VERSION ... 127 ... 147` | Node 升级后 native 模块（better-sqlite3）不匹配 | `cd ~/Codes/camofox-browser-fork && npm rebuild better-sqlite3` |
| `POST /tabs` 返回 400 | `userId and sessionKey required` | body 必带两者（`userId` 放 query 无效；`listItemId` 是 legacy 别名） |
| `POST /sessions/:userId/cookies` 返回 403 | 未配 `CAMOFOX_API_KEY` 时**仅放行非生产的 loopback 请求** | 本机自用加 `CAMOFOX_API_KEY`，或确认不是从非 loopback 地址调用 |
| **测身份保持时自建 oracle 服务反复卡死** | Python `HTTPServer`（单线程）被 CamoFox 的 keep-alive 连接占住 → 进程还在（`lsof` 看得到）但 `curl` 全部超时 | 改 `ThreadingHTTPServer` + `protocol_version='HTTP/1.0'`（不开 keep-alive）+ `daemon_threads=True`。**症状是「进程在但不响应」，别误判成浏览器或功能问题** |
| 偶发 503 `session_expired` | session 回收与建 tab 撞车（fork 已加在飞保护 + 每 tick 限 3 个串行关） | 重试一次即可，不要判定为「服务坏了」 |

**登录态自检（⛔ 别用 `document.cookie` 判断）**：会话 cookie 是 **HttpOnly**，`document.cookie` 只能看到
CSRF 那一个（如 `csrf_token`），**看不到会话 cookie**。据此判「没登录」是错的（2026-09-25 实测踩过）。
正确判据任选其一：
- 页面内带会话请求 API：`fetch('/api/xxx').then(r=>r.status)` ⇒ 200 才是真登录；
- 看 UI 有无「退出登录 / 当前用户」；
- 看服务端日志 `POST .../login` 是否 `Completed 200`。

**停服务一律按端口**（`lsof -ti:9377 | xargs kill`）：进程命令行是 `node server.js`，不含目录名，`pkill -f ".../camofox-browser-fork/server.js"` 匹配不上。

### ⛔⛔ 起新实例前先查旧实例；收工必须把「自己开的」全部收掉

**2026-09-25 反复踩到的习惯性错误**：要对比多档窗口尺寸时，在 9378/9379/9380 起了三个新实例，
**却没关掉之前那个还在跑的 9377** ⇒ 屏幕上出现 4 个窗口，其中一个是空的（0 tab）。
「开了新窗口却留着旧的空窗」= 看着像重复访问、实际是收尾没做干净。

| 纪律 | 怎么做 |
|------|--------|
| **起之前查** | `lsof -ti:9377,9378,9379,9380` + 对每个端口看 `activeTabs`；已有能用的就别再起 |
| **要对比多档尺寸就换端口** | `CAMOFOX_PORT=9378/9379/9380` 各自独立，同时记住「这些也是我开的」 |
| **收工逐个收** | 关掉**自己起的每一个** tab（`DELETE /tabs/:tabId`）与实例（`lsof -ti:<port> | xargs kill -9`） |
| **⛔ 不动不是自己起的** | 预先存在的实例（如用户的 9377）**不擅自关**——但要在汇报里点明「还有一个空窗口，是你原有的，要关说一声」 |
| **收工自检** | 把你开过的每个端口列一遍，逐个确认 `activeTabs=0` 且端口已释放 |

**判据**：用户屏幕上不该出现「我没打算让他看的」窗口；每个窗口要么有用途，要么已关。

## Account Inventory Workflow

For multi-site research, follow this four-step process:

### Step 1: Assess Login Requirement
For each target site, determine if login is needed:
- **Content gated** (知乎评论区、小红书正文) → need login
- **Read-only accessible** (V2EX、GitHub Issues、G2) → no login needed
- **API accessible** (X/Twitter via xurl) → no login needed for search

Group sites into: `must login` / `no login needed` / `unknown`.

### Step 2: Review Accounts with User
Present the `must login` list to the user. Ask which they have accounts for.

### Step 3: Guide Login One by One (Keep Same Window)
For each site the user has an account for:
1. Tab already open on previous login? Create a **new tab** (`POST /tabs`) in the same visible browser instance
2. Navigate to login page (`POST /tabs/:tabId/navigate`)
3. User enters credentials manually in the visible Firefox window (passwords never touch agent)
4. User says "done"
5. Agent exports that tab's cookies and appends them to `~/.camofox/{userId}-cookies.json`（agent 侧自管累积）
6. Create next tab → repeat until all sites logged in

**Do NOT close the browser between logins.** A single visible CamoFox window handles
all login sessions. Closing and reopening forces a new browser launch.
### Step 4: Automated Research

Once all cookies are saved, switch to headless mode and begin automated research:

**Close the visible window:**
1. Close all login tabs via `DELETE /tabs/:tabId`
2. Kill the visible-window server: `process(action='kill')` (or Ctrl-C)
3. Restart without `CAMOFOX_INTERACTIVE=desktop`（回到默认 `off`）
4. 导出的 cookie 文件 persists at `~/.camofox/researcher-cookies.json` across restarts

**Create logged-in tabs:**
```bash
# Create tab
TAB=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","sessionKey":"s1"}')
TAB_ID=$(echo "$TAB" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tabId',''))")

# Navigate to target domain (must match the domain where cookies were saved)
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/navigate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","url":"https://www.xiaohongshu.com/explore"}'

# Restore saved cookies
# ⛔ v1.17 已无 /tabs/:tabId/restore-cookies（该端点不存在）；改为导入 session
curl -s -X POST "http://localhost:9377/sessions/researcher/cookies" \
  -H "Content-Type: application/json" \
  -d "{\"cookies\": $(cat ~/.camofox/researcher-cookies.json)}"
# 约束：cookies 必须是数组；每条必含 name / value / domain；单次上限 500 条。
#       未配 CAMOFOX_API_KEY 时仅放行「非生产 + loopback」，否则 403。

# Refresh page to apply cookies
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/navigate" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","url":"https://www.xiaohongshu.com/explore"}'
```

Then run full channel traversal with original API endpoints for each site.

## Fork & Current Version

**Fork repo**: `github.com/xiaohui-zhangxh/camofox-browser`
**Local path**: `~/Codes/camofox-browser-fork`
**Current version**: `1.17.0`（`package.json` 里 `name` 仍是 `@askjo/camofox-browser`，
**名字不变但已是我们的 fork** —— 判定看版本号 + remote，不要只看包名）

**Do NOT use 官方 npm 的二进制** —— 早期版本捆绑 Playwright 1.61.1，其 `setDefaultViewport`
CDP 调用会带 `isMobile`，而 Camoufox 二进制（FF 135.0.1）不认这个字段，直接 `Protocol error`。
**v1.17 依赖 `playwright-core ^1.58.0`**，已避开该问题。

### v1.17 现行配置（`lib/config.js` 实读的环境变量）

| 变量 | 作用 |
|---|---|
| `CAMOFOX_INTERACTIVE` | `off`（默认）· `desktop`（本机可见窗口）· `novnc` · `auto` —— **控制有无窗口的唯一开关** |
| `CAMOFOX_PORT` | 监听端口，默认 `9377` |
| `CAMOFOX_WINDOW_SIZE` | 外层窗口尺寸，如 `1280,860` |
| `CAMOFOX_DEVICE_SCALE_FACTOR` | 截图 DPR（走 `layout.css.devPixelsPerPx`） |
| `CAMOFOX_HUMANIZE` | 真人化输入时长：`true` / 秒数上限 / `false` |
| `CAMOFOX_SHOWCURSOR` | `1`/`true` 显示合成光标 |
| `BROWSER_IDLE_TIMEOUT_MS` | 浏览器空闲自动关闭阈值，**`0` = 永不自动关** |
| `CAMOFOX_API_KEY` | 开启后 cookie 导入等敏感端点需要 `Authorization: Bearer` |
| `CAMOFOX_PROFILE_DIR` / `CAMOFOX_COOKIES_DIR` / `CAMOFOX_TRACES_DIR` | 各类数据落盘目录 |

**⛔ 不再存在的变量**：`CAMOFOX_HEADLESS`（传了不报错，但窗口不会出来）。

## Viewport & Window Size Control

⚠️ **`CAMOFOX_DEVICE_SCALE_FACTOR` 只管截图清晰度，不改变 CSS 布局**（实码 `lib/config.js:194` 注释原文
`Device pixel ratio for screenshots (CSS layout remains unchanged)`）。所以：
- **CSS 视口 = `CAMOFOX_WINDOW_SIZE` 原值**，不会除以 DPR。`1920,1080` + DPR2 ⇒ 页面按 1920 宽排版、截图 3840 物理像素。
- 想「字大」不是调 DPR，而是**调小 `CAMOFOX_WINDOW_SIZE`**。
- 2x Retina 屏上 DPR=1 会让字看起来被压小一半（把半屏 CSS 内容塞进一个物理窗口）。
- 实测参照：3456,2230+DPR2（盖满 16" 屏，CSS 1728，偏大）→ 2880,1620+DPR1.5（仍偏大）→ 1920,1080+DPR2（字大小合适）→ **1600,840+DPR2（窗口更小、字仍合适，2026-09-25 实测选定）**。
- 拍「窄容器」场景**不要缩浏览器窗口**（会连带改掉其它图的版式）；用页面内 CSS 把该容器宽度调到 480–560px，并在对照文档写明造法。

**v1.17 事实（实测 server.js:911 / 1403 `viewport: null`）**：session context 用 `viewport: null`，
页面布局**服从外层 Camoufox/Firefox 窗口**。所以：

- `CAMOFOX_WINDOW_SIZE` 控制**外层窗口尺寸**（每维 100..4000），是可靠手段。
- `CAMOFOX_DEVICE_SCALE_FACTOR` 走 Firefox 偏好 `layout.css.devPixelsPerPx`（server.js:1188），
  只改物理像素，**不改 CSS 布局**。
- 工具栏会使内部页面高度小于外层窗口高度，**这是正常现象**。
- 需要改尺寸 ⇒ **改环境变量并完整重启**（配置只在启动时读），不在已有进程上临时修。
- `window.resizeTo()` / `page.setViewportSize()` 在创建 context 后**静默无效**（反检测锁定）。
- 另有 `POST /tabs/:tabId/viewport` 可按 tab 调；它同样是「改配置式」而非拉伸已有 context。

```bash
CAMOFOX_WINDOW_SIZE=390,844 CAMOFOX_INTERACTIVE=desktop node server.js   # mobile-sized
CAMOFOX_WINDOW_SIZE=1920,1080 node server.js                            # full HD
```

For content extraction, the default desktop viewport (1280x720) is sufficient —
pages render their content regardless of viewport size.

## Login Flow (Visible Window → Cookie Persistence)

**Do NOT script credential entry.** The user enters credentials manually in the visible browser:

```
1. Agent: Create tab, navigate to login page
2. User:  Enter username/password in the visible window
3. User:  Tell agent "done"
4. Agent: Export that tab's cookies, append to the combined file
5. Agent: Close visible window, continue without CAMOFOX_INTERACTIVE
```

Cookies are kept in a **single combined file** per userId at `~/.camofox/{userId}-cookies.json`
（agent 侧累积：一个文件里同时含多个已登录站点的 cookie）。v1.17 **没有** `save-cookies` /
`restore-cookies` 端点，导出与导入都是 agent 侧行为：

```bash
# 导出（agent 侧）：从该 tab 取 cookies，追加进合并文件
curl -s "http://localhost:9377/tabs/$TAB_ID" -H "Content-Type: application/json"
# → data 里含该 tab 的 cookies；agent 追加写 ~/.camofox/researcher-cookies.json

# 导入（新浏览器实例、需要已登录态时）：
# ⛔ 旧写法 /tabs/$TAB_ID/restore-cookies 已不存在
curl -s -X POST "http://localhost:9377/sessions/researcher/cookies" \
  -H "Content-Type: application/json" \
  -d "{\"cookies\": $(cat ~/.camofox/researcher-cookies.json)}"
# 约束：数组；每条必含 name/value/domain；单次上限 500；未配 CAMOFOX_API_KEY 时仅 loopback+非生产
# 导入后刷新页面，cookie 生效
```

**Key details:**
- `document.cookie` cannot read httpOnly cookies — always use the API endpoints
- `launchPersistentContext()` does NOT work with Camoufox binary on macOS — manual export/import is required
- 合并文件方案意味着**一次导入**即可同时恢复所有已登录站点

## API Usage (Original Endpoints)

Always pass `userId` in the **request BODY**, not query string:

```bash
# Create tab
TAB=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","sessionKey":"s1"}')
TAB_ID=$(echo "$TAB" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tabId',''))")

# Navigate (userId in body)
curl -s -X POST http://localhost:9377/tabs/$TAB_ID/navigate \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","url":"https://example.com"}'

# ⛔ Screenshot 是例外：GET + userId 走 QUERY（不是 body），可选 fullPage
curl -s -o shot.png "http://localhost:9377/tabs/$TAB_ID/screenshot?userId=researcher"
curl -s -o full.png "http://localhost:9377/tabs/$TAB_ID/screenshot?userId=researcher&fullPage=true"
# 实测：viewport 1280x799 ≈ 105KB；fullPage 1280x2086 ≈ 277KB
# 其它 GET 端点同样把 userId 放 query：/tabs · /tabs/:tabId/stats · /links · /images · /downloads

# Read structure（拿到可点元素的 ref 编号，click 用它）
curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=researcher"

# Type — uses Playwright's humanized input (character-by-character with latency)
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","selector":"#sign_in_form_login","text":"user@example.com"}'

# Click — uses Playwright's humanized mouse movement
# ⛔ 实测（2026-09-25）：click **只支持 ref**，用 selector 会返 HTTP 422。
# ref 来自 snapshot，且**每次 snapshot 后会变**——用前先重新 snapshot。
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","ref":"e4"}'

# Type — ⛔ 必须带 ref 或 selector，只给 text 会返 HTTP 400
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/type" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","selector":"input[type=password]","text":"...","submit":true}'
#   字段：ref | selector（二选一必填）、text、mode(fill|keyboard)、delay、submit

# Close tab
curl -s -X DELETE "http://localhost:9377/tabs/$TAB_ID" \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher"}'
```

## Polling for Readiness

Do **not** use fixed `sleep`. Poll the health endpoint every 1s:

```bash
for i in $(seq 1 30); do
  STATUS=$(curl -s http://localhost:9377/ 2>/dev/null)
  echo "$STATUS" | grep -q '"connected":true' && echo "✅ ${i}s" && break
  sleep 1
done
```

Typical startup time: 1–3 seconds on macOS.

## Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `window.resizeTo()` / `page.setViewportSize()` has no effect after launch | Window stays same size | Camoufox locks viewport for anti-detection after creation. **Fix: set `CAMOFOX_WINDOW_SIZE` at launch** — our fork passes it via `launchOptions.window` + `newContext({viewport})`. |
| 手动 `node server.js` 启动后 5 分钟，`/health` 从 `browserConnected:true` 变 `false` | fork 默认 `BROWSER_IDLE_TIMEOUT_MS=300000`（`lib/config.js:149`），最后一个 tab 关掉 5 分钟后自动关浏览器 | 启动时加 `BROWSER_IDLE_TIMEOUT_MS=0`（0 = disables idle browser shutdown）。本技能**不依赖任何外部启动脚本**，直接用上文启动块即可 |
| `page.fill()` / `page.click()` hangs | Playwright method times out | Camoufox Playwright bindings don't support these reliably. Use original API's `/type`/`/click` endpoints, or fall back to `page.evaluate()` with JS DOM manipulation. |
| Login URL redirects to error/404 page (e.g. `sspai.com/auth/signin` → `/whoops`) | Page shows "whoops" or blank, user can't log in | Some sites have non-standard login URL paths. **Fix: navigate to homepage first**, let the user click the sign-in button themselves in the visible window. The page's own JS will send them to the correct URL. |
| Tab "no longer exists (browser was restarted)" | API returns 410 | Camofox may restart the browser under load. Create a fresh tab. |
| `userId required` | API returns 400 | Include `userId` in the **request body**, not the query string. |
| `launchPersistentContext()` doesn't persist | Login lost on restart | Camoufox binary doesn't support persistent contexts on macOS. Save/restore cookies manually. |
| ❌ Never write custom mouse/keyboard simulation | User complains "that looks fake — the cursor jumps then wiggles in place" | Use the original API's built-in humanization (`/type`, `/click`). Formula-generated mouse movement (linear interpolation steps with random delay added) is instantly detectable — real human motion is continuous and non-linear. The browser contributors already solved this. Never use `page.evaluate()` to set input.value or dispatch synthetic events for login flows — that bypasses ALL humanization. If the original `/type`/`/click` fail for a specific element, accept the limitation and fall back to `web_search` rather than writing fake-looking simulation. |

## Direct Playwright Fallback (No Humanization)

If the original API fails for a specific site, use the direct server from `references/camofox-direct-server.js`:

```bash
cp <本技能目录>/references/camofox-direct-server.js .
NODE_PATH=$(npm root -g)/@askjo/camofox-browser/node_modules node camofox-direct-server.js
```

This provides a minimal API (`/tabs`, `/navigate`, `/evaluate`) using raw Playwright + `page.evaluate()` for all interactions. No humanization — use only when the original API's `/type`/`/click` fail.

## Fallback When CamoFox Fails

```python
from hermes_tools import web_search
results = web_search(query="site:reddit.com keyword")
```

Log the gap so the user knows what was missed.

## References

| File | About |
|------|-------|
| `scripts/camofox.py` | **浏览器操作首选入口**。12 个命令的 REST 封装：`health / open / list / wait / snapshot / click / type / press / scroll / navigate / evaluate`。纯 stdlib（urllib），无外部依赖。`python3 scripts/camofox.py health --base http://127.0.0.1:9377` |
| `references/camofox-api-cheatsheet.md` | REST 端点速查表（233 行）：路径、参数、body 结构、ref 交互时序、userId/sessionKey 用法 |
| `references/camofox-direct-server.js` | Minimal Playwright-direct API server. Use when original `/type`/`/click` fail for specific elements. Includes cookie save/restore endpoints. |
| `references/fork-v1.17-contract.md` | fork 的来源、安装、编译、启动、健康检查完整契约 |
| `references/rest-workflow.md` | REST 工作流请求模板与失败处理 |
| `references/persistence-and-login.md` | 持久化路径、会话清理与登录边界 |
| `references/ui-automation-pitfalls.md` | **驱动现代前端（Radix/shadcn 等）的实测坑**：`el.click()` 对组件库无效、改用坐标或 hover；`--base` 必跟在子命令后；登录态别看 `document.cookie`；权限菜单可能不在侧栏；窄容器改容器 CSS 不缩窗口；截图必须实际打开核 |
| `references/identity-persistence-verified.md` | 身份持久化（cookie / localStorage / IndexedDB）实测结论 |
| `scripts/identity_harness.py` | 身份持久化验证 harness（配合 `oracle_server.py` 使用） |
| `scripts/oracle_server.py` | 本地身份 oracle 服务：以「服务端 session 记录」为准判定是否真登录，可验证 cookie / localStorage / IndexedDB 的恢复 |
| `references/macos-headful-patcher.js` / `references/viewport-mobile-init.js` | macOS 有头窗口与移动视口的补丁脚本 |
| `references/kb-research-2026-07-03.md` | 历史调研快照（不是执行契约，不代表当前站点可访问性） |
