# Source Login Status Reference

Common research sources and their login requirements (updated 2026-07-03).

## Login Strategy Priority

1. **First try w/o login** — CamoFox can reach many sites without auth
2. **Headful login** — Start CamoFox with `CAMOFOX_HEADLESS=false`, navigate to login page, user logs in directly in the CamoFox browser window. Persistence plugin saves state automatically.
3. **Cookie import** — Export cookies from normal browser (Netscape format) and import into CamoFox session
4. **web_search fallback** — Snippets often contain key data even when full page is blocked

## 🔴 Requires Login

### Reddit
- **r/selfhosted**: All posts require login to view content. CamoFox is detected by Reddit's anti-bot → redirects to random NSFW subreddits.
- Even with cookies, Reddit may still detect CamoFox's fingerprint.
- **Best fix**: web_search snippets or use normal browser directly.

### 小红书 (Xiaohongshu)
- Requires QR code scan or phone number login.
- Search results page shows login wall immediately.
- **Fix**: Log in via CamoFox headful mode (`CAMOFOX_HEADLESS=false`). Use consistent userId. Persistence plugin saves state. May need to re-scroll after login.

### 知乎 (Zhihu)
- Full question/answer pages: accessible without login (partial content).
- Comments: require login.
- **Fix**: Many answers are visible without login. For comments, use headful login via CamoFox.

### Glukhov PKM
- Returns 403 "Authorization required".
- Not a login issue — requires direct authorization or is behind Cloudflare.
- **Fix**: Skip — not scrapeable.

## 🟢 No Login Required

### Wiki/Knowledge Base Comparison Sites
- **selfhosting.sh** — Full article accessible.
- **geekflare.com** — Full article accessible.
- **contabo.com** — Full article accessible.
- **docsio.co** — Full article accessible.

### Pricing Pages
- **getoutline.com/pricing** — Fully accessible.
- **affine.pro/pricing** — Fully accessible.
- **b3log.org/siyuan/pricing.html** — Fully accessible (Siyuan Note pricing).

### Hacker News
- **news.ycombinator.com** — Posts and comments accessible without login.
- **news.mcan.sh** (HN mirror) — Fully accessible.
- **alt-hn.vercel.app** (HN mirror) — Fully accessible.

### GitHub
- **GitHub repositories** — README, issues, PRs accessible.
- **GitHub discussions** — Accessible but may have limited comments.
- **GitHub releases** — Accessible.

## ✅ Known Working CamoFox URLs (Researched 2026-07-03)

| URL | Status | Notes |
|-----|--------|-------|
| getoutline.com/pricing | ✅ Works | Pricing extracted |
| affine.pro/pricing | ✅ Works | Pricing extracted |
| selfhosting.sh/best/wiki | ✅ Works | 7-tool comparison |
| docsio.co/blog/free-knowledge-base-software | ✅ Works | 9-KB comparison |
| geekflare.com/software/self-hosted-wiki-software | ✅ Works | 7 Wiki comparison |
| contabo.com/blog/how-to-set-up-a-self-hosted-wiki | ✅ Works | Deployment guide |
| news.mcan.sh | ✅ Works | HN mirror |
| github.com/outline/outline/discussions | ✅ Works | Low-value (2021) |
| b3log.org/siyuan/pricing.html | ✅ Works | Pricing extracted |
| zhihu.com/question/645107504 | ✅ Works | Digital garden Q&A |
| zhihu.com/question/15133096760 | ✅ Works | Personal KB Q&A |
| xiaohongshu.com/search_result | ❌ Login wall | Needs headful login |
| reddit.com/r/selfhosted | ❌ Bot detection | Unreliable even with login |
