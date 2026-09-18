# 收录配图：产品截图最佳实践

## 0. 铁律速查

| 场景 | 首图截什么 |
|------|-----------|
| GitHub / GitLab / Gitee 仓库，**项目有官网且官网可用** | **官网首页**（`homepage` 字段或 README 品牌链接） |
| 仓库**有官网但官网不可用 / 像半成品** | **回退 GitHub 仓库页** |
| GitHub 仓库，**无官网** | GitHub 仓库页 |
| RubyGems / npm 等包注册表页 | 该包对应的 **GitHub 仓库根页**；仓库有官网则用官网首页 |
| 普通产品官网 / 落地页 | 官网首页（hero 区） |
| 用户指定了截图 URL | **按用户给的 URL**（覆盖以上全部） |

> 用户 2026-09-18 定规：收录 GitHub 项目时，只要它有官网，就截官网——正文首图优先展示官网，不用仓库页。

## 1. 怎么判断「有没有官网」

1. `curl -s https://api.github.com/repos/<owner>/<repo>` → 看 `homepage` 字段是否非空
2. 读 README 顶部：`<a href="https://…">` 品牌 logo 链接、`👉 **https://…**` 文档/官网入口
3. 注意区分：文档站（docs.xxx.com）与官网（www.xxx.com）——**首图用官网**，文档站可作正文中的次要配图

## 1.5 什么才算「官网」——判据与反例

**合格官网**：独立域名 + 首屏是品牌化 hero（产品名 + 卖点句 + CTA）+ 有功能/定价/客户等营销内容。例：`https://www.embedpdf.com/`——独立域名，首屏 "Embed PDF files without the pain" + 三个 CTA + 框架支持图标。

**不合格（一律不用官网图，回退 GitHub 仓库页）**：

| 类型 | 例子 | 为什么不行 |
|------|------|-----------|
| 托管 demo 页（`*.github.io` / `*.vercel.app` 等） | `mozilla.github.io/pdf.js` | 是 demo 不是产品站，灰色播放器 + 示例列表，没有产品叙事 |
| 纯文档站 | `docs.xxx.com` | 给已有开发者看的 API 索引，不是给陌生访客看的产品门面 |
| 包注册表页 | npmjs.com / rubygems.org | 元数据页，无视觉信息 |
| README 式索引页 | GitHub Pages 默认首页 | 只有文件/示例列表 |
| 未完成品 | 「Coming soon」、只有 logo、布局错乱 | 放出去反而显得产品不靠谱 |

**一句话判据**：这张图能不能让**第一次见到这个产品的读者**在 3 秒内看出「它是什么、给谁用」？不能 → 用仓库页。

用户 2026-09-18 定规并点名反例：pdf.js 的展示页就不适合放进 c456。

## 2. 操作序列

```bash
cd <workspace>
mkdir -p .tmp
c456 browser start                      # 如未运行
c456 screenshot https://www.<官网>/ -o .tmp/<name>-hero.png   # 视窗截图，不加 -f
# 需要第二张：仓库页或官网功能页
# c456 screenshot https://github.com/<owner>/<repo> -o .tmp/<name>-repo.png
c456 asset upload -f .tmp/<name>-hero.png
# 取 markdownSnippet，写成 ![](https://c456.com/our-assets/… "c456:asset/<id>")
rm .tmp/<name>-hero.png                 # 上传完清理
c456 browser stop                       # 本次会话不再截图时
```

## 3. 截图参数

- **一律视窗截图**（默认即视口高度），**不要**加 `-f` / `--full-page`——整页长图在列表卡片和正文里都难读。
- 默认 `--wait-after-load 3000`，SPA 官网若首屏未渲染完可加长。
- `github.com` 会自动隐藏 README 上方文件表格（除非加 `--keep-github-files-table`）。
- 需要登录态才能在窗口内看到的内容：`c456 browser start` 后在该窗口手动登录（profile 持久化在 `~/.cache/c456-cli/chrome-profile`，登录态可复用）。

## 4. 正文里的写法

第一行即首图（tool / channel 类文章）：

```markdown
*[EmbedPDF](https://www.embedpdf.com/) — 官网首页。*

![EmbedPDF 官网首页](https://c456.com/our-assets/<id>/… "c456:asset/<id>")
```

- 图片 URL 必须是完整 `https://c456.com/our-assets/…`；`c456:asset/<id>` 只能放在 title 位置（第二个引号内）。
- 图说用一行斜体 + 外链，**不要**开「配图」二级标题。
- 配图数量：<3000 字 1-2 张；3000-5000 字 2-3 张；5000+ 字 3-5 张。

## 5. 常见错误

| 错误 | 后果 |
|------|------|
| GitHub 项目有官网却截仓库页当首图 | 首图信息量低（README 文件列表），不体现产品形态 |
| 用 `-f` 截整页 | 长图变糊、卡片展示差 |
| 图片 URL 写 `c456:asset/<id>` | 前端不展开，图不显示 |
| 引用对方 CDN（images.unsplash.com / 官网 assets） | 防盗链 / 过期，必须上传本站素材库 |
