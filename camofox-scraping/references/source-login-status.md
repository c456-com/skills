# 数据源登录状态参考

常见调研数据源及其登录要求（更新于 2026-07-03）。

## 登录策略优先级

1. **先尝试免登录访问** —— CamoFox 可以在无认证的情况下访问许多站点
2. **有头模式登录** —— 使用 `CAMOFOX_HEADLESS=false` 启动 CamoFox，导航到登录页面，用户直接在 CamoFox 浏览器窗口中登录。持久化插件自动保存状态。
3. **Cookie 导入** —— 从普通浏览器导出 Cookie（Netscape 格式）并导入 CamoFox 会话
4. **web_search 回退** —— 即使完整页面被屏蔽，搜索摘要通常也包含关键数据

## 🔴 需要登录

### Reddit
- **r/selfhosted**：所有帖子需要登录才能查看内容。Reddit 的反机器人检测会识别 CamoFox → 重定向到随机的 NSFW 子版块。
- 即使有 Cookie，Reddit 仍可能检测到 CamoFox 的指纹。
- **最佳方案**：使用 web_search 摘要或直接使用普通浏览器。

### 小红书 (Xiaohongshu)
- 需要扫码或手机号登录。
- 搜索结果页面立即弹出登录墙。
- **解决方案**：通过 CamoFox 有头模式登录（`CAMOFOX_HEADLESS=false`）。使用一致的 userId。持久化插件会保存状态。登录后可能需要重新滚动页面。

### 知乎 (Zhihu)
- 完整问答页面：无需登录即可访问（部分内容）。
- 评论：需要登录。
- **解决方案**：许多回答无需登录即可查看。对于评论，通过 CamoFox 有头模式登录。

### Glukhov PKM
- 返回 403 "Authorization required"（需要授权）。
- 不是登录问题 —— 需要直接授权或位于 Cloudflare 后面。
- **解决方案**：跳过 —— 不可抓取。

## 🟢 无需登录

### Wiki/知识库对比站点
- **selfhosting.sh** —— 完整文章可访问。
- **geekflare.com** —— 完整文章可访问。
- **contabo.com** —— 完整文章可访问。
- **docsio.co** —— 完整文章可访问。

### 定价页面
- **getoutline.com/pricing** —— 完全可访问。
- **affine.pro/pricing** —— 完全可访问。
- **b3log.org/siyuan/pricing.html** —— 完全可访问（思源笔记定价）。

### Hacker News
- **news.ycombinator.com** —— 帖子和评论无需登录即可访问。
- **news.mcan.sh**（HN 镜像） —— 完全可访问。
- **alt-hn.vercel.app**（HN 镜像） —— 完全可访问。

### GitHub
- **GitHub 仓库** —— README、Issues、PR 可访问。
- **GitHub Discussions** —— 可访问，但评论可能受限。
- **GitHub Releases** —— 可访问。

## ✅ 已验证可用的 CamoFox URL（调研于 2026-07-03）

| URL | 状态 | 备注 |
|-----|------|------|
| getoutline.com/pricing | ✅ 可用 | 定价已提取 |
| affine.pro/pricing | ✅ 可用 | 定价已提取 |
| selfhosting.sh/best/wiki | ✅ 可用 | 7 款工具对比 |
| docsio.co/blog/free-knowledge-base-software | ✅ 可用 | 9 款知识库对比 |
| geekflare.com/software/self-hosted-wiki-software | ✅ 可用 | 7 款 Wiki 对比 |
| contabo.com/blog/how-to-set-up-a-self-hosted-wiki | ✅ 可用 | 部署指南 |
| news.mcan.sh | ✅ 可用 | HN 镜像 |
| github.com/outline/outline/discussions | ✅ 可用 | 低价值（2021 年） |
| b3log.org/siyuan/pricing.html | ✅ 可用 | 定价已提取 |
| zhihu.com/question/645107504 | ✅ 可用 | 数字花园问答 |
| zhihu.com/question/15133096760 | ✅ 可用 | 个人知识库问答 |
| xiaohongshu.com/search_result | ❌ 登录墙 | 需要有头模式登录 |
| reddit.com/r/selfhosted | ❌ 机器人检测 | 即使登录也不可靠 |
