---
name: c456-wechat-layout
category: c456
tags: [c456, wechat, 公众号, layout, typography, darkmode, typography]
description: "公众号图文排版 — 标题层级、重点三档、深色模式适配、按段落配图、交付自检。当用户要排版公众号文章、抱怨读起来困难、或需要处理深色模式/配图/图片格式/图床问题时触发。与 c456-wechat-publish 分工：前者管品牌组件，本技能管排版规则。"
version: 1.0.0
related_skills:
  - c456-wechat-publish
  - c456-wechat-cover
  - c456-video
---

# 公众号图文排版

把一篇写好稿子的文章排成手机上读得下去的图文。只管**层级、节奏、配图、交付**；c456 品牌组件（导读块/CTA/署名）另见 c456 profile 里的 `c456-wechat-publish`。

## When to Use

要把文章发公众号、或用户抱怨“读起来很困难/没有层级/字太小”时。做配图动效见 `c456-video`。

## 一、先定层级，再填内容

排版难读的根因不是缺样式，是**所有文字一样大、一样重、一样间距**。动笔前把这四层定死，全文只允许用这四层。

### 一级标题（章节）—— 橙色序号块 + 粗黑 + 细线

每章一个，编号两位。全文唯一用“色块”的地方：

```html
<section style="margin:44px 0 14px;">
  <section style="display:flex;align-items:center;gap:10px;">
    <section style="width:26px;height:26px;border-radius:8px;background:#fa9704;color:#ffffff;font-size:13px;font-weight:700;text-align:center;line-height:26px;">01</section>
    <section style="font-size:20px;font-weight:700;color:#18181B;letter-spacing:.01em;line-height:1.4;">章节标题</section>
  </section>
  <section style="height:1px;background:#e8e4dd;margin:14px 0 0;"></section>
</section>
```

上方 44px 把上一章彻底断开；1px 浅灰线是章节分界符。

### 二级标题（小节）—— 左侧橙条

```html
<section style="margin:28px 0 12px;padding:0 0 0 12px;border-left:3px solid #fa9704;font-size:17px;font-weight:600;color:#18181B;line-height:1.5;">小节标题</section>
```

### 正文 —— 16px / 行高 1.9 / 段间 18px

```html
<p style="margin:0 0 18px;font-size:16px;line-height:1.9;color:#333;">…</p>
```

行高用 1.9 而不是 1.75：手机屏上更松，长文不易串行。一节最后一段 margin 归 0。

### 重点：三档，不要只用一种

| 档 | 样式 | 用在哪 |
|---|---|---|
| 判断句 | `<strong style="font-weight:600;color:#18181B;">` | 全文论点、结论句 |
| 关键概念 | `<strong style="font-weight:600;color:#fa9704;">` | 术语、反常识点，一节最多 2 处 |
| 荧光笔 | `<span style="background:linear-gradient(transparent 58%, rgba(250,151,4,0.38) 58%);">` | 金句、要读者记住的短语 |

**荧光笔用渐变没问题，关键是颜色用 rgba 半透明**（`rgba(250,151,4,0.38)`）：浅色底上透出浅橙、深色底上透出暗橙，两种模式都看得见。写死 `#ffe9c6` 这种实色底就相反——深色模式下会变成一块浅橙底，字就糊了。

三档混用才有节奏；全篇一种橙色加粗等于没强调。

### 金句块（一节一个呼吸口）

上下两条细线夹住的居中大字，一节最多一次：

```html
<section style="margin:0 0 34px;padding:26px 0;border-top:1px solid #efece6;border-bottom:1px solid #efece6;text-align:center;">
  <p style="margin:0;font-size:19px;font-weight:600;color:#18181B;line-height:1.75;">一句话<br>分两行</p>
</section>
```

### 结尾块（浅底 + 三行）

```html
<section style="margin:34px 0 0;padding:30px 22px;background:#faf8f4;border-radius:12px;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.22em;color:#b0aaa3;font-weight:600;">写在最后</p>
  <p style="margin:0;font-size:18px;font-weight:600;color:#18181B;line-height:1.85;">第一行<br>第二行<br><span style="color:#fa9704;">收尾金句</span></p>
</section>
```

## 二、配图：按段落配，不做横滑图集

图跟着段落走，读完一段看一张。**不要做左右滑动图集**——手机上滑不动、看不全，用户会直接否掉。

```html
<section style="margin:8px 0 24px;text-align:center;">
  <img src="..." style="width:82%;height:auto;display:inline-block;border-radius:10px;">
  <p style="margin:9px 0 0;font-size:12px;color:#a8a29e;line-height:1.55;">图注：一句话说明这张图在讲什么</p>
</section>
```

- 宽度 **82%** 居中：100% 的 3:4 图会占掉一屏多，82% 让图文交替得动
- 一张图只配一段，图注写“这张图在讲什么”，不写“图 1”
- 图放在**它解释的那段之后**，不是章节开头
- 配图一律 **3:4**（1080×1440 或 810×1080）：横屏 1920 在正文里只缩到 0.35 倍，48px 说明字显示成 17px，全糊。3:4 是 0.63 倍，同样 48px 显示 30px

## 三、图床：c456 素材库不能直接给公众号用

实测结论（2026-11）：c456 `asset upload` 上传 JPG/PNG 会被统一转成 `image/webp`。

- **微信能显示 WebP 外链**（实测粘贴后可正常显示），所以 WebP 本身不是障碍
- **真正的问题是 `previewUrl` 带时间戳会过期**（`c456 asset refresh-markdown` 就是用来续期的），文章发出去后图片会成片失效

所以当前最稳的路径仍是：**本地按 `01-xx.jpg / 02-xx.jpg` 顺序命名 → 后台逐张上传素材库 → 编辑器插到对应段落**。

要自动化就先接一个真图床（七牛 / 阿里 OSS / Cloudflare R2，需要 key），或等 c456 提供原图直出的稳定链接。

## 四、深色模式：背景和正文颜色都交还微信

这是踩过两次坑才想明白的一条。深色模式看不见，不是“暗色文字要改成亮色”，而是**根本不该写死颜色**。

| 元素 | 做法 | 原因 |
|---|---|---|
| 正文 `<p>` | **不写 `color`** | 微信自动反色，浅色模式黑字、深色模式白字 |
| 一级/二级标题 | **不写 `color`** | 层级靠字号 + 字重 + 间距，不靠颜色 |
| 判断句加粗 | `font-weight:600`，不写色 | 同上 |
| 正文根容器 | **不写 `background`** | 写死白底搭配自动反色文字 = 白白抵消 |
| 强调色 | 保留 `color:#fa9704` | 橙色在两种底色上都够对比度 |
| 有底色的块（导读/结尾） | 底色改半透明：`rgba(128,128,128,0.10)` 或 `rgba(250,151,4,0.07)`，块内文字也不写色 | 半透明灰/橙叠在什么底色上都协调；写死 `#fafafa` 在深色页面里就是一块刺眼的白纸 |

自检命令（交付前跑一遍）：

```bash
# 正文段落不应该有写死的 color，只允许强调色/图注/带底块
 grep -o 'color:#[0-9A-Fa-f]*' article.html | sort | uniq -c | sort -rn
```

预览页一定要带一个**深色预览开关**（`body.dark #js_content { background:#1b1b1b; color:#e8e8e8 }`），交付前自己先切一遍看。

## 五、交付格式

- 只保留 inline style：公众号编辑器会剥离 `<style>` 和 class
- 一律用 `<section>`，不用 `<div>`；小标题也不用 `<h2>/<h3>`（支持不稳）
- 正文**不含 H1**：标题在编辑器单独填
- 交完整 HTML 预览页（含工具栏 + 一键复制），不要只给正文片段

## 五、常见陷阱

| 陷阱 | 说明 |
|---|---|
| 全篇一种强调样式 | 分三档（黑粗 / 橙粗 / 荧光笔），混用才出节奏 |
| 每段间距一样大 | 一级标题上 44px、二级标题上 28px、段间 18px，三级不同 |
| 用横滑图集塞多张图 | 手机上滑不动，改按段落配图 |
| 图片放章节开头 | 放它解释的那段之后 |
| 3:4 图铺满 100% 宽 | 占掉一屏多，压到 82% |
| 横屏图直接塞正文 | 字号缩到 0.35 倍，必糊 |
| 用 c456 asset URL 当公众号图源 | WebP 能显示，但 URL 会过期 |
| 文字高亮用实色底 | 深色下变成浅橙块，字就糊了。用 `rgba(250,151,4,0.38)` 渐变 |
| 正文写死 `color:#333` | 深色模式不反色，黑底深灰字直接消失。不写 color 交给微信 |
| 根容器写死白底 | 和自动反色文字互相抵消，深色下白底白字 |
| 正文里写 H1 | 标题在后台单独填，正文重复会出现两个标题 |

## 六、定稿参数表（直接照抄，不要再试错）

| 项 | 值 |
|---|---|
| 一级标题 | 橙底序号块 26×26 + 20px/700 + 1px 浅灰线，上方 margin 44px |
| 二级标题 | 左边 3px 橙条 + 17px/600 |
| 正文 | 16px / 行高 1.9 / 段间 18px / **不写 color** |
| 重点一（判断句） | `<strong style="font-weight:600">` |
| 重点二（术语） | `<strong style="color:#fa9704;font-weight:600">` |
| 重点三（荧光笔） | `linear-gradient(transparent 58%, rgba(250,151,4,0.38) 58%)` |
| 导读块 / 结尾块 | 底色 `rgba(128,128,128,0.10)` / `rgba(250,151,4,0.07)`，文字不写色 |
| 配图 | 3:4、宽 82%、图注 12px 灰、放在它解释的段落**之后** |
| 正文根容器 | 不写 background、不写 color |

## 七、交付前自检（每篇都跑）

1. `grep -o 'color:#[0-9A-Fa-f]*' article.html | sort | uniq -c` —— 正文段落不该有写死的色，只允许橙色强调/图注灰/橙底白字
2. `grep -c 'background:#' article.html` —— 应该是 0，有底块全部用 `rgba(`
3. `grep -c 'linear-gradient' article.html` —— 有就要确认里面是 `rgba(...)` 不是实色
4. 预览页切一遍**深色预览**：文字、高亮、导读块、结尾块四块都看得见
5. 粘到公众号后看有无 `darkmode-no-gradient` 警告（有就是高亮里还藏着实色）
6. 配图是否接在它解释的那段之后，编号 01…N 是否按顺序

## 九、发布流程（封面、排版、配图串起来）

```
1. 排版正文（本技能）
2. 出封面 → 调 wechat-cover 技能
     node scripts/render.cjs --preset presets/<风格>.json --data '{...}' --out cover.png
     风格自动匹配文章主题；命中多个或零个才问用户
3. 配图 → 从视频按屏抽帧，按 01…N 命名，插到它解释的段落之后
4. 上传公众号 → 后台逐张传图，粘贴正文，填标题摘要
5. 验收 → 深色模式切一遍，看有无 darkmode 警告
```

封面和正文必须共用一套配色（米底 #F6F3ED / 墨 #1A1A1A / 橙 #FA9704），封面是同一栏目的门面，不能与正文视觉脱节。

## 十、技能职责划分（别串错）

| 要做什么 | 用哪个 |
|---|---|
| 写视频、分镜、音乐、渲 MP4 | `c456-video` |
| MP4 转 GIF、手写 SVG 小动图 | `c456-gif` |
| **出公众号封面** | **`c456-wechat-cover`** |
| 公众号排版、深色模式、配图、交付 | 本技能 |
