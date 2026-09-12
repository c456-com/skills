# 手动补采 SOP — 每日策展 cron 失败后的恢复路径

> 触发场景：辉哥说「今天没有执行每日资讯采集」，或 cron `last_status: error` 连续多天。先按 `hermes-cron-diagnostics` Pattern E 确认根因（通常是模型 API 挂死），再按本 SOP 手动补当天策展。

## 0. 前置判断

- `cronjob action='list'` 看 `last_error`；若是 `TimeoutError ... waiting for non-streaming API response` → agent 第一步就死了，当天零产出（无 digest、无信号草稿）。
- 先修 cron 根因（model override 到本地模型），再补当天内容——否则明天还会失败。

## 1. 采集（blogwatcher 失败时直接 curl fallback）

`blogwatcher-cli scan` 可能大面积失败（实测 23/38 源 fail、无输出）。直接 curl 抓以下源（浏览器 UA），存 `.tmp/rss-<name>.xml`：

| 源 | URL |
|----|-----|
| Search Engine Land | https://searchengineland.com/feed |
| Moz Blog | https://moz.com/blog/feed |
| TLDR AI | https://tldr.tech/api/rss/ai |
| Simon Willison | https://simonwillison.net/atom/entries/ |
| TechCrunch AI | https://techcrunch.com/category/artificial-intelligence/feed/ |
| Search Engine Journal | https://www.searchenginejournal.com/feed/ |
| Content Marketing Institute | https://contentmarketinginstitute.com/feed/ |

注意：
- CMI feed 常 malformed（`not well-formed`），解析失败直接跳过，不阻塞。
- Perplexity blog 403（Cloudflare），跳过。
- 解析脚本要同时处理 RSS `<item>` 和 Atom `<entry>`（Simon Willison 是 Atom），按 pubDate/updated 过滤最近 2 天。

## 2. 读原文（轨道 1 必须读原文）

- `web_extract` 若报 `DuckDuckGo (ddgs) is a search-only backend` → 说明 extract 后端不可用，改用 curl 抓 HTML。
- curl + 浏览器 UA 抓正文，剥 `<script>`/`<style>` 后取 `<article>` 块转文本。
- **SEL 有 Cloudflare 防护**：可能返回 "Just a moment..." 或静默重定向到另一篇推荐文章（字节数异常大时要警惕）。**首选路径：启动 CamoFox（`~/Codes/camofox-browser-fork`，headless `node server.js`）抓全文**——实测可过 SEL/SEJ 的 Cloudflare（navigate 后 sleep 6s 再 evaluate `document.body.innerText` 分段取）。CamoFox 不可用时才降级：用 RSS description 摘要 + 其他源交叉验证，正文标注「据 SEL 报道」，不要把重定向页当原文。
- SEJ 一般能直接抓到正文。

## 3. 写 digest + 建信号草稿

- 格式参照最近的 `daily-digest-YYYY-MM-DD.md`（首行摘要 + 轨道 1 条目：标题链接+品类+简介+来源+→价值+📌可组合打法 + 分隔线 + 轨道 2 格局 + 轨道 3 入库）。
- 创建信号：
  ```bash
  npx c456-cli signal new -t "c456 每日信号精选 | YYYY-MM-DD" \
    --description "今日摘要（轨道 1：N 条 + 轨道 2：N 条）" \
    --body-file /Users/xiaohui/hermes-workspaces/c456-com/.tmp/daily-digest-YYYY-MM-DD.md
  ```
- 输出 ID 后即为草稿（raw/approved），**保持草稿，绝不 `--publish`**。

## 3.5 信号发布规则（2026-08-13 事故教训，铁律）

**每日精选 digest 信号永远不对外发布。** 它只是内部选稿工具：

- 每日精选（标题「c456 每日信号精选 | YYYY-MM-DD」）= 草稿，供辉哥选稿，**绝不 `update <id> --publish`**
- 辉哥确认某条后 → 把该条**另建为单条独立信号**（500-1500 字记者体，写前先读原文拿数据）→ 再 `signal update <新id> --publish`
- 误 publish 后撤回：`npx c456-cli signal update <id> --draft`
- 判断标准：**列表 = 草稿；单篇文章 = 可发布**。拿不准就问，或保持草稿让辉哥决定。

## 4. 验证 cron 修复

- `cronjob action='run'` 验证修复；跑完检查 `last_status` 是否为 ok、输出文件是否含真实工作内容。
- **注意（2026-08-13 实测）**：手动 run 会重放整个 prompt，副作用比「重复产物」更严重——cron agent 会**覆盖共享文件**（`.tmp/daily-digest-YYYY-MM-DD.md` 被替换成它自己的版本）甚至 **`signal update` 已有信号**（cron prompt 常含「当天已有则 signal update 更新」）。**验证前先备份** `.tmp/` 和 signal list；验证后把被覆盖的 digest 恢复、把被改写的信号用自己版本 `update` 回去。
- 修完 cron 后记忆里更新 job 的 model override 事实。

## 5. 时间成本参考

一次完整补采（curl 8 源 + 解析 + 读 2-4 篇原文 + 写 digest + 建信号 + 修 cron + 验证）≈ 15-20 个工具调用，全程可在一个会话完成。
