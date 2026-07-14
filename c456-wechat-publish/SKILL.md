---
name: c456-wechat-publish
description: Use when generating WeChat Official Account (公众号) articles from c456 content. Converts c456 signals/playbooks into inline-style HTML for paste-to-WeChat workflow. Load c456-voice-journalist first for voice, then this skill for visual layout.
version: "1.1.0"
related_skills:
  - c456-voice-journalist
  - c456-write
  - c456-publish
---

# c456 公众号发布模板

> **Voice 层**: `c456-voice-journalist`（科技记者风格）
> **Visual 层**: 本技能（公众号 HTML 排版）
>
> 先确定文章内容与调性，再用本技能的组件排版。

---

## c456 视觉风格

取自 c456.com 的 CSS 变量与 logo SVG：

| 元素 | 色值 | 用途 |
|------|------|------|
| **品牌色** | `#fa9704`（暖橙） | **唯一的品牌色**——标记、强调、数字编号、左侧条 |
| **正文** | `#333333` | 正文文字 |
| **浅灰底** | `#fafafa` | 交替背景色，与白底交替产生段落层次 |
| **浅灰边框** | `#e5e7eb` | 分隔线、表格边框 |
| **辅文** | `#666666` | 图注、次要信息 |
| **深色标题** | `#18181B` | 标题字色 |
| **字体** | `-apple-system, "PingFang SC", "Microsoft YaHei", sans-serif` | 系统原生字体 |
| **行高** | `1.75` | 宽松排版 |

c456 的视觉设计是**极度克制的单色系 + 唯一的暖橙点缀**。公众号排版应延续这一气质：干净、克制、内容优先，暖橙只用于真正需要强调的元素。

---

## 布局原则

1. **全文零嵌套**：直接用 `p`、`h2`、`h3`、`div`、`blockquote`、`hr`、`table`，不用 `section > section > section` 多层嵌套。公众号对深嵌套支持不稳定。
2. **交替背景**：相邻内容块用白底 `#fff` ↔ 浅灰底 `#fafafa` 交替，视觉上自然分段，减少对边框的依赖。
3. **有框无框搭配**：引用块、小标题用左侧橙条；总结块用上方橙线；普通段落和章节标题无边框，靠背景色和间距区分。
4. **标准 HTML 标签**：标题用 `<h2>`、`<h3>`；引用用 `<blockquote>`；代码用 `<pre>`；列表用 `<ul>`/`<ol>`；表格用 `<table>`。公众号对标准标签的兼容性最好。

---

## 一、版式组件库

### 节背景块（容器）

所有内容放在交替背景的容器中。两种底色交替使用即可自然分段：

```html
<!-- 白底节 -->
<div style="background:#fff;padding:24px 20px;">
  ...标题/段落/引用...
</div>

<!-- 浅灰底节（交替） -->
<div style="background:#fafafa;padding:24px 20px;">
  ...标题/段落/引用...
</div>
```

容器不限制标签（div/p/section 均可），核心是 `background` 交替 + `padding` 产生呼吸感，相邻同色背景会自动合并。

### H2 章节标题

```html
全部使用 `<section>` 作为块容器——公众号不支持 `<div>`，`<section>` 是替代它的标准块元素。

每条内容包裹在 `<section>` 中，所有样式必须 inline。

### 导读块（左侧橙条）

```html
<section style="padding:20px;border-left:4px solid #fa9704;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#555;">
    导语文字，一句话点明核心判断。
  </p>
</section>
```

### 正文段落

```html
<section style="padding:0 20px 14px;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#333;">
    正文内容。<strong style="color:#fa9704;">关键词</strong>用暖橙加粗。
  </p>
</section>
```

同一背景下连续段落共享一个 `section`，内部多个 `<p>` 用 `margin-bottom:14px`。

### 小标题（左侧橙条）

```html
<section style="padding:0 0 0 14px;border-left:3px solid #fa9704;font-size:17px;font-weight:600;color:#18181B;line-height:1.5;">小标题文字</section>
```

小标题不是 `<h3>` 而是 `<section>`——公众号对标题标签支持不稳定。

### 引用块（浅灰底 + 左侧橙条）

```html
<blockquote style="margin:0;padding:12px 16px;background:#fafafa;border-left:4px solid #fa9704;font-size:15px;line-height:1.75;color:#555;">
  引语内容——原文引用或核心观点。
</blockquote>
```

### 对比表（横向列交替背景）

使用 flex 行，外容器带 `1px` 间隙（充当分隔线），各列独立设背景色实现横向交替：

```html
<section style="display:flex;gap:1px;background:#e5e7eb;border-radius:8px;overflow:hidden;">
  <section style="flex:1;padding:12px;background:#fff;">
    <section style="line-height:1.6;margin:0;font-size:14px;color:#999;">方案 A</section>
    <section style="line-height:1.6;margin:4px 0 0;font-size:15px;color:#18181B;font-weight:600;">$10</section>
  </section>
  <section style="flex:1;padding:12px;background:#fafafa;">
    <section style="line-height:1.6;margin:0;font-size:14px;color:#999;">方案 B</section>
    <section style="line-height:1.6;margin:4px 0 0;font-size:15px;color:#18181B;font-weight:600;">$20</section>
  </section>
  <section style="flex:1;padding:12px;background:#fafafa;">
    <section style="line-height:1.6;margin:0;font-size:14px;color:#999;">方案 C</section>
    <section style="line-height:1.6;margin:4px 0 0;font-size:15px;color:#18181B;font-weight:600;">免费</section>
  </section>
</section>
```

关键点：

- 外容器 `gap:1px` 利用父 `#e5e7eb` 背景色充当列分隔线，替代 `border`。
- 各列 `flex:1` 等宽分布。
- 列背景色横向交替：第一列 `#fff`，后续列 `#fafafa`。
- 如果表头和数据行需要多行，每行是一个独立的 flex 容器——**不要**把多行塞进一个容器。

多行对比表示例（每行独立 flex 容器）：

```html
<!-- 表头行：浅灰底 -->
<section style="display:flex;gap:1px;background:#e5e7eb;border-radius:8px;overflow:hidden;margin-bottom:4px;">
  <section style="flex:1;padding:10px 12px;background:#fafafa;font-size:14px;color:#666;font-weight:600;">维度</section>
  <section style="flex:1;padding:10px 12px;background:#e5e7eb;font-size:14px;color:#666;font-weight:600;">OpenCode Go</section>
  <section style="flex:1;padding:10px 12px;background:#e5e7eb;font-size:14px;color:#666;font-weight:600;">Cursor Pro</section>
  <section style="flex:1;padding:10px 12px;background:#e5e7eb;font-size:14px;color:#666;font-weight:600;">Trae</section>
</section>
<!-- 数据行：白底 -->
<section style="display:flex;gap:1px;background:#e5e7eb;border-radius:8px;overflow:hidden;">
  <section style="flex:1;padding:10px 12px;background:#fff;font-size:14px;color:#333;">月费</section>
  <section style="flex:1;padding:10px 12px;background:#fafafa;font-size:14px;color:#18181B;font-weight:600;">$10</section>
  <section style="flex:1;padding:10px 12px;background:#fafafa;font-size:14px;color:#18181B;font-weight:600;">$20</section>
  <section style="flex:1;padding:10px 12px;background:#fafafa;font-size:14px;color:#18181B;font-weight:600;">免费</section>
</section>
```

**不要**使用 `display:grid` 或 `<table>`——flex 在各手机微信版本中兼容性最好，且列交替背景更可控。

### 总结框（上方橙线）

```html
<section style="border-top:3px solid #fa9704;padding:24px 20px;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#555;">
    总结内容。
  </p>
</section>
```

通常放在文章末尾，作为收束。

### 图片

```html
<section style="margin:24px 0;text-align:center;">
  <img src="https://c456.com/our-assets/..." alt="说明" style="max-width:100%;height:auto;display:block;margin:0 auto;border-radius:8px;">
  <p style="margin:6px 0 0;font-size:14px;color:#999;line-height:1.5;">图注文字</p>
</section>
```

### 代码块

```html
<section style="background:#18181B;border-radius:8px;padding:16px;margin:16px 0;overflow-x:auto;">
  <pre style="margin:0;font-family:'SF Mono','Fira Code',monospace;font-size:14px;line-height:1.6;color:#e5e7eb;white-space:pre-wrap;">代码内容</pre>
</section>
```

### 分隔线

```html
<hr style="border:none;border-top:1px solid #e5e7eb;margin:0;padding:0;">
```

---

## 二、文章类型模板

### 信号类 → 公众号快讯

```
导读（浅灰底 + 橙条）
  → 正文段落（白底）
  → 关键数据/对比表（灰底）
  → 价值判断/总结（灰底 + 上方橙线）
  → 分隔线 + 来源标注（小字）
```

### 打法类 → 公众号深度

```
导读（灰底）
  → 章节 1（白底）：H2 + 段落 + 配图
  → 章节 2（灰底）：H2 + 段落 + 引用
  → ……
  → 总结框（灰底 + 上橙线）
  → 分隔线 + 延展阅读
```

### 对比评测 → 公众号选型

```
导读（灰底）
  → 场景描述（白底）
  → 方案 A（白底/灰底交替）
  → 方案 B（交替）
  → 对比表（灰底）
  → 选型建议（灰底 + 上橙线）
```

---

## 三、完整骨架

完整可预览+复制的 HTML 文件见 `references/shell-template.html`，含一键复制按钮和全部组件示例。

---

## 四、设计原则

- **一个色就够了**：暖橙 `#fa9704` 是唯一的品牌色。其余全是黑白灰。
- **零嵌套**：每个内容元素一层到底，不用 `section > section > section`。
- **交替出节奏**：白底 ↔ 浅灰底交替，自然产生段落感，无需额外边框。
- **有框无框搭配**：引用块/小标题用橙条强化；普通段落靠背景色区分。

## 参考

- 技术约束：公众号仅保留 inline style，所有样式必须写在 `style=""` 内
- 图片：发布前替换为公众号素材库 URL
- 来源：[baklib-tools/skills/wechat-mp-html](https://github.com/baklib-tools/skills/tree/main/skills/wechat-mp-html) — 底层 HTML 约束参考
- 色板来源：c456.com 的 `application.css` CSS 变量 + logo.svg brand color `#fa9704`
