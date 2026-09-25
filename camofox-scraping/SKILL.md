---
name: camofox-scraping
description: "通用浏览器 / browser automation / web browsing / scraping：当用户或任意 AI Agent 需要打开、访问、阅读、交互、调试或采集任何网页时触发，包括公开或动态页面、有头窗口登录与人工操作、无头浏览、批量抓取，以及 Cloudflare、反爬或登录墙场景；用于浏览器操作、页面内容读取和网页数据采集。"
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [scraping, camofox, browser-automation, research, cloudflare]
references:
  - references/fork-v1.17-contract.md
  - references/rest-workflow.md
  - references/persistence-and-login.md
---

# CamoFox v1.17.0 抓取与可见登录

## 核心契约

- **唯一来源：** [xiaohui-zhangxh/camofox-browser](https://github.com/xiaohui-zhangxh/camofox-browser)；SSH 等价地址为 `git@github.com:xiaohui-zhangxh/camofox-browser.git`。
- **本机默认落点：** `/Users/xiaohui/Codes/camofox-browser-fork`。
- **其他机器：** 可以选择自己的绝对 clone 目录，但必须在
  `~/.camofox/camofox-local-root.txt` 记录该目录，并在后续所有命令中使用同一个值。
- **版本门禁：** fork 当前契约为 CamoFox `1.17.0`；安装后先确认版本，再继续。
- **禁止绕过：** 不从其他仓库、发布包、全局安装或临时安装器取得 CamoFox，也不修改 fork 业务源码来适配当前任务。仓内唯一允许的 `npx` 用法是 `npx tsc -p .` 严格 TypeScript 编译门禁。

完整的来源、安装、编译、启动和健康检查契约见
[ fork v1.17 契约](references/fork-v1.17-contract.md)。安装、编译、启动或健康检查任一步失败，都停止；不拿已有进程或其他服务代替通过。

## Fail-closed 顺序

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

## 可见登录与人化交互

需要账号、密码、二维码、短信、2FA 或验证码时，使用
`CAMOFOX_INTERACTIVE=desktop` 打开的真实窗口，由用户完成敏感输入。
Agent 不索取、不输入、不记录这些凭据；只在登录完成后继续用 REST 读取页面。

页面交互只走 fork 的 REST 工作流：创建 tab、导航、snapshot、用当前
元素 ref 点击或输入，必要时重新 snapshot。不使用页面脚本直接改 DOM、合成事件、直接调用 Playwright 客户端或伪造鼠标键盘来替代 REST。`CAMOFOX_HUMANIZE` 只控制
fork 的 Camoufox 输入时长，不能用来绕过站点的认证或安全检查。

完整请求模板和失败处理见 [REST 工作流](references/rest-workflow.md)；
持久化路径、会话清理和登录边界见 [持久化与登录](references/persistence-and-login.md)。

## 持久化与清理

默认 persistence 插件把每个用户的状态写入：

```text
~/.camofox/profiles/<SHA256(userId) 的前 32 个十六进制字符>/storage-state.json
```

保持同一个 `userId` 才能复用同一份状态。正常结束任务时先关闭 tab，再按需要
关闭 user session，让插件完成检查点。登出或要清除登录态时，使用
`DELETE /sessions/:userId/storage_state`；该操作会关闭 live session，并删除
对应的状态文件和元数据。

不要手工读取、复制或输出 storage state，也不要把敏感页面内容贴进日志。

## 失败时回退

CamoFox 被目标站点拦截、登录过期、交互不可靠、二进制或网络失败时：

1. 记录目标 URL、时间、HTTP/REST 错误和缺失内容。
2. 停止继续硬点、硬输或重复提交。
3. 调用 Hermes `web_search` 查找可公开核验的替代信息，保留来源 URL。
4. 搜索也失败时如实报告，不用猜测补齐内容。

## 历史资料

[数据源登录状态](references/source-login-status.md) 与
[调研快照](references/kb-research-2026-07-03.md) 只保存历史观察，不是执行
契约，也不替代上面的 v1.17.0 门禁。
