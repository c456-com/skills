---
name: c456-wechat-cover
category: c456
tags: [c456, wechat, cover, thumbnail, design-system, style-preset]
description: "公众号封面 — 2.35:1 封面图，带风格库（presets/），同一栏目长期视觉统一。当用户要出公众号封面、做头图、或要求封面风格统一时触发。支持按文章主题自动匹配风格，以及在用户调整后自动沉淀新风格。"
version: 1.0.0
related_skills:
  - c456-wechat-layout
  - c456-video
---

# 公众号封面

给文章出封面图（2.35:1）。核心不是“做一张好看的图”，是**连发十期后读者在信息流里一眼认出来**——固定的是版式和位置，变的只有内容。

## When to Use

- 文章要发公众号，需要封面图
- 用户说“出个封面 / 做张头图 / 封面风格统一一下”
- 发布流程里，排版完成后、上传前

不用于：正文内插图（那是 `c456-video` 抽帧或 `c456-wechat-layout` 配图）、视频封面。

## 前置条件（首次使用跑一次）

```bash
npm i -D playwright && npx playwright install chromium   # 截图引擎
bash scripts/setup-fonts.sh                              # 字体（Noto Sans SC，OFL）
```

字体**不入库**（全量 4.5MB），由 setup 脚本从 npm 拉取。不跑也能出图，但中文会 fallback 到系统字体（可能不是开源字体，不能对外发布）。

## 规格（写死，不要每次重想）

| 项 | 值 |
|---|---|
| 比例 | **2.35:1**（微信信息流封面的完整显示比例，不被裁切）|
| 画布 | 1080×460，导出 deviceScaleFactor 2 → 2160×920 |
| 微信显示 | 900×383 |
| 字体 | Noto Sans SC（OFL）。**不打包**，跑 `scripts/setup-fonts.sh` 从 npm 拉 101 个 woff2 分片到 `assets/fonts/` |

## 风格库（presets/）

每个风格是一个 JSON，存在 `presets/` 下。新增风格就是新增一个 JSON + 一个模板变体。

```json
{
  "id": "editorial-01",
  "name": "编辑风 · 米底橙点",
  "layout": "left-text-right-art",
  "palette": {"bg": "#F6F3ED", "ink": "#1A1A1A", "accent": "#FA9704", "muted": "#6B6154"},
  "decor": {"dots": true, "blob": true, "brandline": true, "boxed_label": true},
  "type": {"title": 58, "sub": 22, "label": 17, "vol": 15, "title_lines": 2},
  "use_when": ["概念解释", "工具拆解", "科普", "方法论"]
}
```

`use_when` 是自动匹配用的关键词。`layout` 决定版式，`palette`/`type` 决定观感，`decor` 控制装饰开关。

## 工作流

### 1. 选风格（自动匹配 → 不确定才问）

1. 读 `presets/*.json`
2. 拿文章标题 + 主题，与每个 preset 的 `use_when` 比对
3. **命中一个** → 直接用，并在回复里说明“用 editorial-01”
4. **命中多个或零个** → 问用户，给出候选（带一句话描述）
5. 用户说“随便/你定” → 选 `use_when` 匹配度最高的，或默认 editorial-01

### 2. 填内容

固定六件东西，每期只换内层：

| 位置 | 内容 | 约束 |
|---|---|---|
| 左上序号块 | 01 / 02 / 03 | 两位数 |
| 左上栏目标签 | 如「AI 拆解」 | 全系列固定，不每期换 |
| 右上期数 | VOL.001 | 递增 |
| 主标题 | 文章核心矛盾 | **最多两行**，每行 ≤ 12 字；可有一处橙色强调 |
| 副标题 | 一句补充 | 两行，每行 ≤ 14 字 |
| 右侧主图 | 一个语义图标 | Iconify duotone，或文章里的主视觉 |

主标题宁可短不要满。标题太长就拆成主标题 + 副标题，不要缩字号。

### 3. 渲染

```bash
node scripts/render.cjs \
  --preset presets/editorial-01.json \
  --data '{"no":"01","label":"AI 拆解","vol":"VOL.001","title":"朋友问我 Harness<br>是什么，我说：<em>后厨</em>","sub":"厨师、菜谱、厨具、工资<br>四样东西说清 AI 怎么干活","art":"assets/chefhat.svg"}' \
  --out cover-01.png
```

### 4. 验收（必做）

- `ffprobe` 确认尺寸 2160×920
- 用视觉模型看一遍：`python3 ~/.hermes/scripts/vision.py cover-01.png "封面第一眼能抓人吗；文字有没有溢出；左右比例舒服吗"`
- 缩到 900×383 再看一次（微信实际显示尺寸，小图上字还认得出才算过）

## 自动沉淀新风格

用户对生成的封面做了调整（换配色、改版式、加/减装饰）并且表示满意时，**不要只改这一张图**，把差异沉淀成 preset：

1. 把当前生效的参数写成 `presets/<新 id>.json`（id 用 `风格名-序号`，如 `editorial-02`）
2. `use_when` 写清楚“这种风格适合什么内容”
3. 在回复里告诉用户“已存为 xx 风格，下次这类内容会自动用”

判断是否需要新 preset：改动涉及**配色或版式**就是新风格；只改文案/图/期数不算。

## 已有的风格

见 `presets/` 目录。当前：

- `editorial-01` — 米底 + 点阵 + 左边文字/右边圆形色斑托图标。适合概念解释、工具拆解、科普。
- `editorial-02-dark` — 同一版式，墨黑底 + 暖白字。适合行业判断、尖锐观点、趋势分析。两套交替用会形成节奏。

新增风格 = 新增一个 `presets/xxx.json`（配色 + 字号 + 装饰开关），同一套 `templates/base.html` 自动生效，不用改 HTML。

## 坑

1. **封面不是海报**：信息流里只有 900×383，字少于 12px 等于不存在
2. **标题不要满**：两行、每行 ≤12 字。塞不下就改文案，不缩字号
3. **橙色只给一处**：标题里的关键词、或序号块，二选一。两处都在抢注意力
4. **主图不要抢戏**：图标区宽不超 32%，颜色比标题淡一档
5. **字体必须开源**：PingFang SC 是苹果专有，不能用于对外发布
6. **别用 1:1 或 16:9 画布**：微信按 2.35:1 裁，其他比例会被切头切脚
7. **字体占位符不能包在 CSS 注释里**：`/* __FONT_FACES__ */` 会被字体 CSS 自带的 `*/` 提前闭合，把紧随其后的 `:root` 整块吞掉——背景变白、字体 fallback，看起来像“设计变丑了”，实际是 CSS 解析失败。模板里写裸占位符
8. **改完要看背景色**：`magick x.png -format "%[pixel:p{8,8}]" info:` 应等于 preset 的 `bg`，是 `srgb(255,255,255)` 就说明变量没生效
