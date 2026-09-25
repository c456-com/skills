# 持久化与可见登录

## 登录边界

1. 先尝试无需认证的页面。
2. 需要认证时，用 `CAMOFOX_INTERACTIVE=desktop` 启动并在真实窗口中打开登录页。
3. 用户自己输入账号、密码、二维码、短信、2FA 或验证码；Agent 不索取、不输入、
   不记录这些值。
4. 登录完成后重新 snapshot，确认页面状态，再继续抓取。

登录页可能改变 URL 或刷新 refs。以 snapshot 的当前结果为准，不预设某个登录
按钮 ref 在所有站点都存在。

## 默认状态文件

persistence 插件默认启用，状态目录由 `userId` 的 SHA-256 前 32 个十六进制
字符组成：

```text
~/.camofox/profiles/<SHA256(userId) 的前 32 个十六进制字符>/storage-state.json
```

插件在创建 session 时恢复合法状态，在 session 正常关闭、服务 shutdown 或
其他受支持的检查点时机保存 cookies 与 localStorage。默认不捕获 IndexedDB；
只有 fork 配置明确启用时才捕获可序列化 IndexedDB。

保持 `userId` 稳定，才能在同一台机器上复用对应 profile。不要手工打开、复制、
编辑或输出 `storage-state.json`，也不要把状态内容放进日志或报告。

## 结束与清除

任务结束时按顺序关闭 tab，再按需要关闭 user session：

```bash
curl -sS -X DELETE "http://127.0.0.1:9377/tabs/$TAB_ID?userId=$USER_ID"
curl -sS -X DELETE "http://127.0.0.1:9377/sessions/$USER_ID"
```

正常关闭 session 会触发检查点。要登出、换账号或清除整份登录态时，使用：

```bash
curl -sS -X DELETE \
  "http://127.0.0.1:9377/sessions/$USER_ID/storage_state"
```

这个清除端点会关闭 live session、等待在途写入，并删除对应的
`storage-state.json` 与 `meta.json`；不要在它之前假定状态已经被清除。
