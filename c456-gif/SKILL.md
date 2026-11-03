---
name: c456-gif
category: c456
tags: [c456, gif, ffmpeg, animation, wechat, short-video]
description: "GIF 动图制作 — 从视频转 GIF（≤300 帧，公众号可用），或手写 SVG 逐帧做小动图。当用户要做公众号配图动效、把视频转 GIF、或需要几秒钟的示意图动画时触发。视频侧见 c456-video。"
version: 1.0.0
related_skills:
  - c456-video
  - c456-wechat-layout
---

# GIF 动图制作

> **路径说明**：主路径是「HyperFrames 出 MP4 → ffmpeg 转 GIF」，视频侧的做法见 `c456-video`。本技能下半部分「手写 SVG 逐帧」是**备用方案**，只在没装 HyperFrames、或只要三五秒小动图时用。
>
> **公众号硬限制：GIF ≤ 300 帧。** 30s@10fps 恰好 300；超了只能降帧率或压叙事，不能硬生生截断。另外公众号上传 GIF 经常失败，稳妥做法是改成静态图按段落配（见 `c456-wechat-layout`）。

## 视频转 GIF（公众号参数）

```bash
ffmpeg -i in.mp4 -vf "fps=10,scale=810:-1:flags=lanczos,split[a][b];\
  [a]palettegen=max_colors=160:stats_mode=diff[p];\
  [b]paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 out.gif
ffprobe -v error -show_entries stream=width,height,nb_frames -of csv=p=0 out.gif
```

- 宽度取 **810**（3:4 源）而不是 720：公众号正文 677px，810 留一点余量，不糊
- 帧率 **10fps** + 时长 ≤30s = ≤300 帧
- 颜色 **160**、`diff_mode=rectangle` 只重绘变化区域，体积能砍一半

## 备用：手写 SVG 逐帧短片

## 短片式动效（辉哥定标准，默认做法，2026-11-03）

**判据：静态元素淡入、图标变个色、整体挪一下 —— 不合格。** 辉哥原话：「有动画跟没动画是一回事，就是几个文字」。他要的不是把静态 HTML 加一点抖动，而是当短视频做。

### 硬指标

| 项 | 标准 |
|---|---|
| 时长 | 15–25 秒（几秒内撑不起一个叙事）；一个概念一个镜头组 |
| 帧率 | 10–12 fps（GIF 足够，体积友好） |
| 帧数 | **≤300 帧**（公众号上传上限，超了传不上去） |
| 尺寸 | 公众号 3:4（810×1080 或 1080×1440），演示类可 720 宽 |
| 素材 | 纯 SVG 矢量图形，禁 emoji、禁位图（缩放不糊、可逐帧改）；图标优先取 Iconify（`api.iconify.design/solar/<name>.svg?color=%23FA9704`），不要手画 |
| 叙事 | 场景从空地开始搭起来 → 角色入场 → 道具飞入落位 → 开始动作 → 收尾 |

### 第二种范式：流程型（一个传送物走完全程）

适合「步骤 / 流程 / 流水线」类内容。不堆场景，用一个传送物走完全程，每到一个节点变一次形。

```
0.0–1.6s   承载结构展开（传送带 / 管道 / 进度轴）
1.5–2.6s   六个节点从下方依次升起（错峰 0.16s，outBack 回弹）
2.6–4.2s   传送物从左侧进入，停在节点 1
4.2–5.2s   节点 1 点亮，传送物第一次变形（纸上出现字迹）
5.2–6.0s   移动到节点 2（inOut，移动中带 sin 上下颠）
…… 每段 2.4s＝0.8s 移动 + 1.6s 停靠变形
17.0–19.5s 收尾：光晕 + 两行标题（第二行晚 0.7s）
```

三条要点：

1. **传送物必须变形，而且要变好几次**。一颗光点从甲走到乙不是动画，只是位移。纸→三视图→九宫格→画面框→波形→成品卡，每站换一个形态。
2. **节点在传送物到达时才亮**，不能一起亮。到达时刻单独一张表（`HIT = [4.2, 6.0, 8.4, 10.8, 13.2, 15.6]`）。
3. **承载结构分两层**：底稿（灰）+ 高亮层（橙）随进度延伸；节点牌子放在带子**下方**、传送物放在带子**上方**，否则两者静帧会重叠（踩过）。

参考实现：`templates/pipeline-svg.html`（20 秒「六道工序」传送带动画）。

### 分镜模板（写代码前先填这张表）

```
0.0–1.4s   空地：地面线从中心向两侧拉开（场景地基）
1.3–3.6s   角色从画面外滑入，落地时 squash 挤压（有重量）
2.0–3.1s   角色配件从天上落下，扣上（旋转回弹）
3.7s       角色做第一个动作（抬手/示意），标签这时才浮出
4.2–5.6s   主体结构从地底升起（案台/传送带/工作区）
5.6–7.0s   道具 A 从天上掉下，落在结构上，弹两下才停
6.8–7.7s   道具 B 从侧边滑入
7.4–8.5s   道具 C 从画外飞入，边飞边转，落定
8.8–11.0s  道具 D 飘落（旋转下落），落位后“打开/展开”
11.3–13.3s 多个小物件依次掉落堆叠（错峰 0.25s）
14.2–15.8s 角色移动到工作位（inOut 缓动，不是瞬移）
15.6–17.2s 开始动作：冒热气/打字/流水转动，物件跟着动
17.4–19.5s 收尾：光晕亮起，主标题浮出
```

### 六条动效纪律

1. **每个物件都要有出场方式**，且各不相同：滑入、掉落、飞入、飘落、升上来。统一淡入 = 死。
2. **要有物理感**：落地 squash（scale 反向补偿）、落位 outBack 回弹、飞行中带 rotate。
3. **先在空地上建主体，再放东西**。物件必须“落在”某个东西上（台面、传送带、地面），不能飘在半空。
4. **落位不是结束**。东西放好后得有“活起来”的动作（锅冒热气、纸会变、灯在闪），否则就是静态图。
5. **文字后置**。标签、旁白、标题都在对应动作完成之后出现，不跟元素同时淡入。
6. **缓动用对**：入场 outC、落位 outBack、位移 inOut、循环用 sin。禁用线性。

### 实现骨架（纯函数 + 逐元素时间轴）

```js
const seg=(t,s,e)=>Math.max(0,Math.min(1,(t-s)/(e-s)));  // t 单位：秒
const outC=t=>1-Math.pow(1-t,3);
const outBack=t=>{const c=1.7;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2);};

const DURATION = 20;                       // 秒
window.render=function(t){
  t*=DURATION;                              // 外部传 0–1，内部转秒
  const cx = -150 + 300*outC(seg(t,1.3,3.6));   // 厨师入场
  el.setAttribute('transform', `translate(${cx},310) scale(...) rotate(...)`);
};
```

每个元素一段独立时间轴，互不依赖。全部用 `setAttribute('transform')` 控 SVG `<g>`，不用 CSS animation（逐帧截图不认时钟）。

### 坑（踩过）

1. **时间单位必须统一**。render 内部用秒、外部传 0–1 比例，忘了乘 `DURATION` 会让整个动画停在初始帧，而且不报错，排查很费时。
2. **掉落的目标坐标要算物件底边**。锅底在 path 的 y=+39，要落在台面 y=240，translate 得给 201，不是 240（锅会插进台面），更不是 0（锅掉到画外）。
3. **先跑几何校验再渲染全片**。渲染 240 帧要几十秒，抽 6–9 个时间点，用 `getBBox()+getCTM()` 算每个元素的屏幕包围盒，检查有没有出框、有没有跟别的元素重叠，比渲完再看便宜得多。
4. **新角色会不会撞旧物件**（硬币堆撞到厨师腿、标签盖住道具）以 bbox 坐标判断，不靠感觉。

### 验证（我这边视觉模型可能不可用时的替代方案）

- `getBBox()` + `getCTM()` 逐时间点输出元素包围盒，断言在 0–750 / 0–420 内
- 无 `pageerror` / console error
- 抽帧像素统计：橙色占比、文字区 ink ratio（>1% = 文字已渲染）
- 最终一定给人看，视觉判断不代劳

### 参考实现

`templates/short-film-svg.html` — 20 秒「一间后厨」分镜式动效完整可跑代码（厨师入场/帽子掉落/锅弹跳/菜谱飘落翻开/硬币堆叠/冒热气/标题浮出）。改内容时只换图形和文案，时间轴结构照用。

---

做公众号配图、流程图示意、数据动画、视频转 GIF 的完整管线。核心原则：**HTML 逐帧渲染 > CSS 动画录屏**，因为确定性、可重跑、零掉帧。

## 本机能力（已验证）

| 工具 | 路径 | 用途 |
|------|------|------|
| ffmpeg 8.x | `/opt/homebrew/bin/ffmpeg` | 编码 GIF（palettegen/paletteuse） |
| ImageMagick 7 | `magick` / `convert` | 帧处理、尺寸批改 |
| Pillow 11 | python3 | 程序化画帧 / 像素校验 |
| playwright-core | `/Users/xiaohui/.local/lib/node_modules/@askjo/camofox-browser/node_modules/playwright-core` | 逐帧截屏（直接 require，不必再装） |
| Chrome | `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` | headless 渲染 |

## 先选路线（动手前按这个判断）

| 需求 | 走哪条 |
|------|--------|
| 一张示意图/流程/数据动起来，公众号配图，几秒循环 | 路线 A/B（本技能）—— 直出 GIF，一版 200KB 级 |
| 讲一个概念/一篇文章的科普短片（一屏一个想法、有字幕、像样片） | **`c456-video` 技能** —— 用 HyperFrames 出 MP4，再走路线 C 转 GIF |
| 宣传片质感：多镜头、转场、文字有重量、音轨字幕 | `hyperframes` 技能（HTML→MP4/WebM）渲完再走路线 C 转 GIF |

判据：**要一张会动的图 → 本技能；要一段能看的片子 → c456-video。**
hyperframes 输出 MP4/WebM，微信只吃 GIF/PNG/JPG，所以末尾必须补 ffmpeg 转码 + 压体积（见「公众号尺寸与体积红线」）。

## 路线 A：HTML 逐帧渲染（默认，视觉质量最高）

1. 写 `index.html`，动画状态由**纯函数** `window.render(t)` 控制（t∈[0,1]），用内联 style 赋值，**不要用 CSS animation / 时间轴**——逐帧截图时 CSS 时钟不可控。
2. `grab.js`：playwright-core 打开页面 → 循环 `page.evaluate(t => render(t))` → `page.screenshot()`，`deviceScaleFactor: 2` 取高清帧，末尾多截 4-6 帧静帧让循环回环不突兀。**直接用 `scripts/grab.js`**（参数化，一份脚本跑多个动画）：
   ```bash
   node grab.js 01-kitchen.html frames1 4 15        # html / 输出目录 / 秒 / fps
   node grab.js 02-pipeline.html frames2 5 15
   ```
3. 编码见下方命令。

示例：`~/.hermes/cache/scratch/gif-demo/`（index.html + grab.js，暖橙 #fa9704 卡片流水线动图，720x405/15fps/214KB）。

## 路线 B：Pillow 直接画帧

纯几何/文字动画、需要逐像素控制时用。中文字体用开源的 Noto Sans SC（见下方「字体」），**不要用 `/System/Library/Fonts/PingFang.ttc`**（苹果专有字体，不能用于对外物料）。适合图表增长、数字滚动、进度类。

## 路线 C：视频/素材转 GIF

- 视频：`ffmpeg -ss 0 -t 5 -i in.mp4 -vf "fps=12,scale=720:-1:flags=lanczos,..." out.gif`
- 网络 GIF：用 `gif-search` 技能搜 Tenor
- 视频转 ASCII 动图：用 `ascii-video` 技能

## 高质量编码命令（关键）

两遍调色板，不要直接 `-i %d.png out.gif`（会掉色、有噪点）：

```bash
ffmpeg -framerate 15 -i frames/f%04d.png -vf \
 "scale=720:-1:flags=lanczos,split[a][b];\
  [a]palettegen=max_colors=192:stats_mode=diff[p];\
  [b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" \
 -loop 0 -y out.gif
```

`diff_mode=rectangle` 让 ffmpeg 只重绘变化区域，体积能砍 30-50%。

## 公众号尺寸与体积红线

- **画幅：公众号正文一律 3:4**（810×1080 或 1080×1440），正文里渲染成 677×903，一屏内能看全。
- **选 3:4 是因为字号可读性**：显示字号 = 设计字号 × 677 / 设计宽度。1920 宽只有 0.35 倍（48px 说明字变 17px，糊）；1080 宽有 0.63 倍（变 30px，清楚）。16:9 只适合纯图表。
- 3:4 字号下限（按 1080 宽）：主词 150–170px / 说明 46–50px / 字幕 38–42px；说明文字每行 8–14 个汉字，超了手机上会碎行拆词组。
- **GIF ≤300 帧**（公众号硬上限）。30s×10fps = 300 帧卡顶格；长内容压节奏而不是降帧率（八屏×3.75s 比八屏×5s 后再降到 7fps 好看）。转完必须 `ffprobe` 验帧数。
- 宽 720–1080；GIF 源文件比显示宽度大一点，缩放时更清晰。
- 帧率 10–12fps（低于 10 会卡，高于 15 体积暴涨收益低）。
- 色数 160-192；如需更小降到 128 + `dither=bayer:bayer_scale=3`。
- **体积 ≤5MB 稳妥，微信硬上限 10MB**。超限就降分辨率（600px）→ 降帧率（12）→ 降色数（128）→ 减时长。
- 时长：几张示意图 2.5–4s 循环；讲一件事的分镜式短片 15–40s（见「短片式动效」）。长片体积靠降帧率和色数控，不靠拉长时长。

## 公众号配图的交付约定（辉哥口径）

- **先文章，后动画。** 动画是为文中某个论点服务的，不是先做完动画再凑文案。
- 正文里留位点：`［动画 N：主题一句话］`，不要写成图注或草稿旁注。
- 文末附「动画设计稿」：每张写清时长、尺寸、分镜顺序、配色、收尾字 —— 这份稿子给制作环节看，不进正文。
- 动画严格按位点的叙事任务做，不做与论点无关的恕技动效。
- 微信只吃 GIF/PNG/JPG，不吃 MP4。
- **GIF 传不上去就降级成静态图**：公众号动图除了 300 帧上限，实际上传还常失败。降级路：从成品视频按屏抽帧（`ffmpeg -ss <屏中段> -i out.mp4 -vframes 1 -q:v 3`），按 `01-` `02-` 顺序命名，插在**对应的那段之后**（宽度 82%），**不要做左右滑动图集**——手机上滑不动。
- 文章本体的层级、重点、配图规范见技能 `c456-wechat-layout`；视频母版制作见 `c456-video`。

## 验证（必须做，不要只凭"应该没问题"）

```bash
ffprobe -v error -show_entries stream=width,height,nb_frames,avg_frame_rate -of default=nw=1 out.gif
ffmpeg -y -i out.gif -vf "select=eq(n\,40)" -vframes 1 check.png   # 抽中间帧看
```

一张文章配多张动画时，拼一张对照表一次看完（比逐张开省事）：

```bash
magick montage chk1-mid.png chk1.png chk2.png -tile 3x1 -geometry +6+6 -background '#dddddd' preview-sheet.png
```

**验收默认走程序化像素校验**（确定性、可重跑）：Pillow 抽样统计品牌色占比、深色占比、标题区域 ink ratio —— 文字区 ink>1% 说明字形已渲染、不是空白帧。

要判断整体观感（构图、留白、气质）就用视觉模型，但走**直连脚本**：`python3 ~/.hermes/scripts/vision.py frame.png "具体问题"`（`vision_analyze` 工具可能走 gateway 的旧环境变量拿到 401；脚本直接连 deepseek-flash，能看图）。问具体问题（“文字有没有溢出、帽子到脚是否都在画面内”），不要问“好不好看”。视模型会给出错的审美评价，描述位置可靠、结论自己裁。

### 字体（硬性）

**只能用开源字体：Noto Sans SC（思源黑体，SIL OFL）。** PingFang SC / Songti SC 是苹果专有字体，不能用于对外物料。

- HTML 路线：`npm pack @fontsource-variable/noto-sans-sc`，把 `package/files/*.woff2` 拷进项目，`@font-face` 指向本地文件（完整做法见 `c456-video` 技能「字体必须是开源字体」）。
- Pillow 路线：用 Noto Sans SC 的 ttf/otf，不用 `/System/Library/Fonts/PingFang.ttc`。
- **不要用 `src: local("X")` 糊过 lint**：只声明不嵌入，renders 机上 fallback，问题到别人机器才炸。

## 坑

- 开始截帧前先 `await page.evaluate(() => document.fonts.ready)` 并 `render(0)` 截一帧验字体 —— 字体没加载完就开截，前几帧是回退字体，GIF 开头会跳一下。
- 交付时用 `open out.gif` 直接让辉哥看到效果，不要只报路径 —— 他的习惯是先看效果再提意见。
- 先报帧数再报体积：公众号只收 300 帧以下，体积过关但帧数超了照样传不上去。
- 文件、脚本、文案跟正文同目录交付，不要散落在 `_archive` 里让人找不到成品。
- `deviceScaleFactor:2` 得到 1440px 帧，编码前必须 `scale=720`，否则体积翻 4 倍。
- 帧文件名补零（`f%04d`），否则 ffmpeg 排序错乱。
- 别用 `convert -delay 6 -loop 0 *.png` 出 GIF：抖色质量差、体积大。
- GIF 只有 256 色，避免大面积平滑渐变（会出带状），改用纯色/点阵/细分层。
