---
name: c456-wechat-publish
description: Use when generating WeChat Official Account (公众号) articles from c456 content. Converts c456 signals/playbooks into inline-style HTML for paste-to-WeChat workflow. ALL inline styles, pure white background (no bg colors on content blocks), orange decorative elements (left border / top border) are the only visual devices. Margin-based spacing, no left/right padding.
version: "2.2.0"
related_skills:
  - c456-voice-journalist
  - c456-write
  - c456-publish
---

# c456 公众号发布模板

> **Voice 层**: `c456-voice-journalist`（科技记者风格）
> **Visual 层**: 本技能（公众号 HTML 排版）
>
> 先确定文章内容与调性，再用本技能的组件排版。公众号编辑器只保留 inline style，所有样式必须写在 `style=""` 内。

---

## c456 视觉风格

取自 c456.com 的 CSS 变量与 logo SVG：

| 元素 | 色值 | 用途 |
|------|------|------|
| **品牌色** | `#fa9704`（暖橙） | **唯一的品牌色**——标记、强调、左侧条、上框线 |
| **正文** | `#333333` | 正文文字 |
| **浅灰边框** | `#e5e7eb` | 分隔线、表格边框 |
| **辅文** | `#666666` / `#555555` | 图注、次要信息、导读文字 |
| **深色标题** | `#18181B` | 小标题字色 |
| **字体** | `-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif` | 系统原生字体 |
| **行高** | `1.75` | 宽松排版 |

c456 的视觉设计是**极度克制的单色系 + 唯一的暖橙点缀**。公众号排版应延续这一气质。

---

## 布局原则

1. **纯白底，无背景**：正文所有内容区块不设 `background` 属性。视觉区分靠**间距**和**橙色装饰线**（左侧条、上框线）。`background:` 只用于导读/引用块的灰底 `#fafafa` 和代码块深底 `#18181B`。
2. **无左右 padding**：正文区块不设左右 padding，文字从页面左侧开始。只有带橙色左边条的元素设 `padding-left:10px`（导读）或 `14px`（小标题）。
3. **间距用 margin，段落自身无底部 padding**：区块之间的间距用 `margin-bottom:24px`。段落自身不设底部的 `padding`。
4. **有框无框搭配**：导读/引用块用 `border-left:4px solid #fa9704` + `background:#fafafa`；小标题用 `border-left:3px solid #fa9704` 无灰底；总结用 `border-top:3px solid #fa9704` 无灰底。
5. **正文不含标题**：公众号标题在编辑器中单独填写，正文 `<section id="js_content">` 内**不要**包含 `<h1>`。
6. **内容不精简**：公众号 HTML 应包含文章的**完整正文内容**，不得删减段落或压缩案例细节。
7. **零嵌套**：直接用 `<section>`、`<p>`、`<blockquote>`、`<hr>`、`<table>`，不用多层 `section > section > section`。

---

## 一、版式组件库

### 导读块（灰底 + 左侧橙条）

```html
<section style="background:#fafafa;border-left:4px solid #fa9704;padding:4px 10px;margin:0 0 24px;border-radius:7px;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#555;">
    导语文字，一句话点明核心判断。
  </p>
</section>
```

### 正文段落组

同一章节下的标题 + 所有段落共享一个 `<section>`，内部 `<p>` 用 `margin:0 0 14px` 隔开：

```html
<section style="margin:0 0 24px;">
  <section style="padding:0 0 0 14px;margin:0 0 14px;border-left:3px solid #fa9704;font-size:17px;font-weight:600;color:#18181B;line-height:1.5;">小标题文字</section>
  <p style="margin:0 0 14px;font-size:16px;line-height:1.75;color:#333;">
    正文段落一。<strong style="color:#fa9704;">关键词</strong>用暖橙加粗。
  </p>
  <p style="margin:0;font-size:16px;line-height:1.75;color:#333;">
    正文段落二（同一章节最后一段，无底部 margin）。
  </p>
</section>
```

### 小标题（左侧橙条，无灰底）

```html
<section style="padding:0 0 0 14px;margin:0 0 14px;border-left:3px solid #fa9704;font-size:17px;font-weight:600;color:#18181B;line-height:1.5;">小标题文字</section>
```

小标题不是 `<h3>` 而是 `<section>`——公众号对标题标签支持不稳定。

### 引用块（灰底 + 左侧橙条）

```html
<blockquote style="margin:0 0 24px;padding:12px 0 12px 10px;background:#fafafa;border-left:4px solid #fa9704;font-size:15px;line-height:1.75;color:#555;">
  引语内容——原文引用或核心观点。
</blockquote>
```

### 对比表（flex 行）

```html
<section style="display:flex;gap:1px;background:#e5e7eb;border-radius:8px;overflow:hidden;margin:0 0 24px;">
  <section style="flex:1;padding:12px;font-size:14px;color:#333;">方案 A</section>
  <section style="flex:1;padding:12px;font-size:14px;color:#333;font-weight:600;">$10</section>
  <section style="flex:1;padding:12px;font-size:14px;color:#333;">方案 C</section>
</section>
```

### 总结框（上方橙线，无灰底）

```html
<section style="border-top:3px solid #fa9704;padding:24px 0 0;margin:0 0 24px;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#555;">
    总结内容。
  </p>
</section>
```

### 图片

```html
<section style="margin:0 0 24px;text-align:center;">
  <img src="..." alt="说明" style="max-width:100%;height:auto;display:block;margin:0 auto;border-radius:8px;">
  <p style="margin:6px 0 0;font-size:14px;color:#999;line-height:1.5;">图注文字</p>
</section>
```

### 代码块

```html
<section style="background:#18181B;border-radius:8px;padding:16px;margin:0 0 24px;overflow-x:auto;">
  <pre style="margin:0;font-family:'SF Mono','Fira Code',monospace;font-size:14px;line-height:1.6;color:#e5e7eb;white-space:pre-wrap;">代码内容</pre>
</section>
```

### 分隔线

```html
<hr style="border:none;border-top:1px solid #e5e7eb;margin:0;padding:0;">
```

### 来源标注（底部 CTA 必须醒目）

```html
<section style="padding:16px 0 0;">
  <p style="margin:0 0 4px;font-size:13px;color:#999;line-height:1.6;">来源文字。</p>
</section>
<!-- CTA：必须使用暖橙按钮样式，不可使用 13px 灰色小字 -->
<section style="margin:24px 0 0;text-align:center;">
  <section style="display:inline-block;background:#fa9704;border-radius:6px;padding:12px 28px;">
    <a href="https://c456.com/playbooks/id" style="color:#ffffff;text-decoration:none;font-size:15px;font-weight:500;">点击下方「阅读原文」查看完整版本</a>
  </section>
</section>
```

---

## 二、文章类型模板

### 打法类 → 公众号深度（最常见）

```
正文直接开始（纯白底）
  → 导读（灰底 + 左侧橙条）
  → 章节 1：小标题 + 段落（无背景）
  → 章节 2：小标题 + 段落（无背景）
  → ……
  → 总结框（上橙线，无背景）
  → 分隔线
  → 来源标注
```

### 信号类 → 公众号快讯

```
正文直接开始
  → 导读（左侧橙条）
  → 正文段落组
  → 关键数据/对比表
  → 价值判断（上橙线）
  → 分隔线 + 来源标注
```

---

## 三、文件引用

- **骨架模板**: `references/shell-template.html` — 可预览+复制的基础 HTML 框架，含一键复制按钮
- **已发布示例**: `references/article-ai-differentiation.html` — 2026-07-14 发布的「AI 时代项目的真正差异化来自哪里」公众号版，经用户验收通过

---

## 四、设计原则

- **一个色就够了**：暖橙 `#fa9704` 是唯一的品牌色，只出现在装饰线（左侧条/上框线）和关键词加粗。
- **纯白底**：内容区块不设背景色。视觉分段靠间距和橙色装饰线。
- **无左右 padding**：全文不设左右 padding，文字从左侧排版。
- **间距用 margin**：区块间距用 `margin-bottom:24px`，段落自身无底部 padding。
- **正文没有标题**：公众号标题在编辑器单独填写。
- **内容完整**：不得删减案例细节或缩短段落。

---

## 五、双平台发布工作流

同一篇文章发布到 c456.com 和公众号两个平台：

```
c456-write §D 撰写 Playbook 正文
  ↓
c456-publish → c456.com/playbooks/<id>（new → --publish）
  ↓
本技能：基于同一份正文生成公众号 HTML
  ├── 去掉 h1 标题（公众号编辑器单独填）
  ├── 重组为纯白版式（无左右 padding, margin 间距）
  └── 复制到公众号后台 → 发布
```

### 从 c456 markdown 到公众号 HTML 的转换规则

| c456 原文元素 | 公众号 HTML 处理 |
|--------------|-----------------|
| `##` / `###` 章节标题 | 橙色左边条小标题（`border-left:3px solid #fa9704`） |
| `>` 引语 | 橙色左边条 blockquote，灰底 |
| 三个 `---` 分隔线 | 保留为 1px 浅灰 `<hr>` |
| **重点加粗** | `<strong style="color:#fa9704;">` 暖橙加粗 |
| 案例/来源标注 | 缩小到 13px 灰色小字 |
| c456 原文底部链接 | 上方分割线，后接「阅读原文 →」 |

### 常见陷阱

| 陷阱 | 说明 |
|------|------|
| **正文包含 h1 标题** | 标题在单独字段填写，正文不要重复 |
| **给段落加背景色** | 纯白底。background 只用于导读/引用块的 `#fafafa` 和代码块的 `#18181B` |
| **段落设左右 padding** | 全文不设左右 padding。只有带橙色左边条的元素设 `padding-left` |
| **用 padding 做区块间距** | 区块间距用 `margin-bottom:24px`，段落自身无底部 padding |
| **精简内容** | 公众号 HTML 必须包含完整正文，不得删减段落 |
| **用 `div` 而不是 `section`** | 公众号对 div 支持不稳定，一律用 `section` |
| **对比表忘记 gap 技巧** | 用 `gap:1px` + 父级 `#e5e7eb` 做列分隔线 |
| **小标题用 `h3`** | 公众号对 h3 支持不稳定，用 `section` + `border-left` 模拟 |
| **只输出正文片段** | 必须交付完整 HTML 文档（含预览壳 `<style>` + toolbar + 一键复制脚本），不要只输出 `#js_content` 片段 |
|| **CTA 使用灰色小字** | 底部「阅读原文」必须使用暖橙按钮样式（橙底白字圆角），不可用 13px/color:#999 的浅色文字 |

---

## 参考

- 技术约束：公众号仅保留 inline style
- 图片：发布前替换为公众号素材库 URL
- 配合技能：`c456-publish`（c456 发布）、`c456-write`（内容写作）
- 来源：[baklib-tools/skills/wechat-mp-html](https://github.com/baklib-tools/skills/tree/main/skills/wechat-mp-html)
- 色板来源：c456.com 的 `application.css` CSS 变量 + logo.svg brand color `#fa9704`
