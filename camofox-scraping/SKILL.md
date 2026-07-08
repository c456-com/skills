---
name: camofox-scraping
description: "CamoFox scraping / Cloudflare bypass：当用户要抓取受 Cloudflare/反爬保护的网页、做浏览器自动化采集、登录态页面研究或 CamoFox 失败回退 web_search 时触发；用于 npx 运行的反检测浏览器抓取。"
version: 1.2.1
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [scraping, camofox, browser-automation, research, cloudflare]
---

# CamoFox 网页抓取

使用 CamoFox 反检测浏览器抓取网站 —— 在它能用的时候。**用不了就别硬上。** 使用回退方案。

## 安装启动（无需克隆）

```bash
# 启动 — 无需 git clone，无需本地仓库
npx @askjo/camofox-browser

# 有头模式（可见浏览器窗口，用于登录）
CAMOFOX_HEADLESS=false npx @askjo/camofox-browser

# 端口 9377，验证：curl -s http://localhost:9377/
```

就这样。不需要 `~/Codes/camofox-browser`，不需要本地修改。

## 理念：能用就用，不能用就跳过

Camofox 是工具，不是项目。如果它访问不了某个站点，不要修补它 —— 改用 web_search。

| 情况 | 应对 |
|------|------|
| Camofox 能用 | 直接使用 |
| Camofox 被屏蔽（Reddit） | 用 web_search 获取摘要；报告中注明缺口 |
| Camofox 崩溃 | 用相同 userId 重启 —— 持久化会恢复登录状态 |
| Viewport/isMobile bug | 已知上游 Camoufox 问题。不要修补 Playwright。等待或使用回退方案。 |

## API 工作流

### 创建标签页

```bash
curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","sessionKey":"<session-key>"}'
```

### 导航 + 提取 — 标准步骤

完整参考见 `references/camofox-web-scraping.md`。关键参数：`expression`（不是 `script`）。

## 持久化（跳过登录烦恼）

```bash
# 重启前优雅关闭会话
curl -s -X DELETE "http://localhost:9377/sessions/<userId>"

# 然后 pkill 是安全的
pkill -f "node server.js"
```

## 回退方案

当 Camofox 失败时（Reddit、二进制文件损坏等）：

```python
from hermes_tools import web_search
results = web_search(query="site:reddit.com keyword")
```

在调研报告中记录缺口，让用户知情。

## 注意事项

- **只用 npx** —— 永远不要克隆仓库。`npx @askjo/camofox-browser` 是唯一支持的方式。
- **不要修补 Playwright** —— 如果 Camoufox 二进制文件不支持某功能，接受这个限制。
- **Reddit 会屏蔽 Camofox** —— 使用 web_search 回退方案。
- **持久化需要在 pkill 之前执行 DELETE /sessions/:userId** —— 没有这一步，登录状态会丢失。
