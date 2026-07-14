---
name: c456-wechat-publish
description: Use when generating WeChat Official Account (公众号) articles from c456 content. Converts c456 signals/playbooks into inline-style HTML for paste-to-WeChat workflow. Load c456-voice-journalist first for voice, then this skill for visual layout.
version: "1.2.0"
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

1. **全文零嵌套**：直接用 `p`、`h2`、`h3`、`section`、`blockquote`、`hr`、`table`。公众号对深嵌套支持不稳定。
2. **背景只用于特殊块**：只对导读/引用块使用浅灰底 `#fafafa`，正文段落和章节标题**不设背景色**。
3. **间距用 margin 不用 padding**：区块之间的间距用 `margin-bottom:24px`，段落自身不设底部 padding。
4. **无左右 padding**：正文区块不设左右 padding，文字从页面左侧开始排版。只有带橙色左边条的元素设 `padding-left`。
5. **有框无框搭配**：导读/引用块用 `border-left:4px solid #fa9704` + 灰底；小标题用 `border-left:3px solid #fa9704` 无灰底；总结块用 `border-top:3px solid #fa9704`。
6. **正文不含标题**：公众号标题在编辑器中单独填写，正文 `<section id="js_content">` 内**不要**包含 `<h1>` 标题或文章副标题。正文直接以导语/首段开始。
7. **内容不精简**：公众号 HTML 应包含文章的**完整正文内容**，不得删减段落或压缩案例细节。
8. **c456 供文的分发策略**：当公众号 HTML 的数据源来自 c456 信号/方案时，**必须先询问用户选择「精简版」还是「完整版」**：
   - **精简版**：保留核心论点和判断，删减案例展开细节，保持可读性的同时制造信息差。正文末尾加醒目引导，促使用户到 c456 阅读全文。
   - **完整版**：不删减，全文原样输出。适合深度订阅用户直接在微信内读完的场景。
   
   精简版的末尾引导格式：
   ```html
   <section style="background:#fafafa;border-left:4px solid #fa9704;padding:16px 0 16px 10px;margin:24px 0;">
     <p style="margin:0;font-size:15px;line-height:1.6;color:#555;">
       <strong style="color:#fa9704;">📖 深度解读</strong><br>
       本文为精简版。完整版本包含更多案例拆解、数据分析和对比维度。<br>
       <span style="color:#fa9704;font-weight:600;">点击下方「阅读原文」查看完整版本</span>
     </p>
   </section>
   ```
   > ⚠️ 公众号禁止外链，不要使用 `<a>` 标签，直接打出纯文本 URL。

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

### 导读块（左侧橙条 + 灰底）

```html
<section style="background:#fafafa;border-left:4px solid #fa9704;padding:4px 0 0 10px;margin:0 0 24px;">
  <p style="margin:0;font-size:16px;line-height:1.75;color:#555;">
    导语文字，一句话点明核心判断。
  </p>
</section>
```

### 正文段落

```html
<section style="margin:0 0 24px;">
  <p style="margin:0 0 14px;font-size:16px;line-height:1.75;color:#333;">
    正文内容。<strong style="color:#fa9704;">关键词</strong>用暖橙加粗。
  </p>
  <p style="margin:0;font-size:16px;line-height:1.75;color:#333;">
    同一章节内连续段落共享一个 section。
  </p>
</section>
```

同一章节内的标题 + 所有段落共享一个 `section`，内部 `<p>` 用 `margin-bottom:14px` 分割。

### 小标题（左侧橙条，无灰底）

```html
<section style="padding:0 0 0 14px;margin:0 0 14px;border-left:3px solid #fa9704;font-size:17px;font-weight:600;color:#18181B;line-height:1.5;">小标题文字</section>
```

小标题不是 `<h3>` 而是 `<section>`——公众号对标题标签支持不稳定。

### 引用块（浅灰底 + 左侧橙条）

```html
<blockquote style="margin:0 0 24px;padding:12px 0 12px 10px;background:#fafafa;border-left:4px solid #fa9704;font-size:15px;line-height:1.75;color:#555;">
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

### 总结框（上方橙线，无灰底）

```html
<section style="border-top:3px solid #fa9704;padding:24px 0 0;margin:0 0 24px;">
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
导读（灰底 + 橙条）
  → 章节 1：小标题 + 段落（无背景）
  → 章节 2：小标题 + 段落（无背景）
  → ……
  → 总结框（上橙线，无背景）
  → 分隔线 + 延展阅读
```

所有章节背景均为白色，靠小标题的橙色左边条和段落间距区分层次。

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
