---
name: c456-video
category: c456
tags: [c456, video, explainer, short-video, hyperframes, storyboard, gsap]
description: "讲解型短视频制作 — 教学主线、一场景一想法、固定机位、3:4 画幅、HyperFrames 渲染 MP4。当用户要把概念、文章或笔记做成科普动画/短视频，或需要产出视频号/抖音内容时触发。含开源字体、图标素材、Lottie 角色动画与渲染管线。"
version: 1.0.0
related_skills:
  - c456-wechat-layout
  - c456-wechat-cover
  - c456-gif
---

# 讲解型短视频（Explainer Video）

把一个概念、一篇文章、一堆笔记变成能看懂的短视频。技术底座是 HyperFrames（HTML + GSAP + 逐帧渲染成 MP4）。

## 前置条件

| 依赖 | 用途 | 安装 |
|---|---|---|
| Node ≥ 22 | 渲染 | — |
| HyperFrames CLI | HTML + GSAP → MP4 | 先装官方技能：`hermes skills install official/creative/hyperframes`；`npx hyperframes@latest doctor` 自检 |
| ffmpeg | MP4 → GIF、按秒抽帧 | `brew install ffmpeg` |
| playwright / playwright-core | 逐帧截屏、bbox 几何校验 | `npm i -D playwright`，或设 `PLAYWRIGHT_MODULE` 指向已装模块 |

字体 Noto Sans SC（OFL）不随技能打包，按下面「开局先定三件事」里的 `npm pack` 命令拉取。**PingFang SC 是苹果专有字体，不能用于对外发布。**

## When to Use

做科普动画、概念讲解、产品说明、流程演示视频时。要 GIF 短图用 `c456-gif`；要真正的视频文件用本技能 + `hyperframes`。

## 开局先定三件事（公众号/视频号场景）

| 项 | 定成什么 | 为什么 |
|---|---|---|
| 画幅 | **3:4（1080×1440）** | 公众号正文宽 677px，3:4 缩 0.63 倍，48px 说明字显示 30px；16:9 只缩 0.35 倍，同样字号显示 17px，全糊 |
| 字体 | **Noto Sans SC**（OFL） | PingFang SC 是苹果专有字体，不能用于对外发布。做法：`npm pack @fontsource-variable/noto-sans-sc`，把 `files/*.woff2`（101 分片）放 `assets/fonts/`，把包里的 index.css 改路径后内联进 `<style>` |
| 时长 | **≤300 帧** | 公众号 GIF 硬限制 300 帧。30s@10fps = 300，恰好卡上限 |

交付三件套：`xxx.mp4`（1080×1920 竖屏发视频号）、`xxx.gif`（810×1080 给公众号）、以及从视频按屏抽出的 **静态帧**（公众号传图更可靠，见下）。

## 一、官方标杆的六条规律（拆片得出，优先于下面所有细节）

拆了 HyperFrames 官方的 50 秒讲解片标杆（1280×720，`faceless-explainer-demo-v2.mp4`），每 5 秒抽一帧，规律如下——这是模板，不要自己发明：

1. **每屏只有三样东西**：一句核心文案 + 一个视觉主体（图/数字/色块）+ 一个底部字幕。多一个都是噪音。
2. **镜头绝对固定**。标杆里 10 个画面全部没有推拉摇移。**动效发生在画面内部**：数字变大、数据条生长、路径浮现、虚线绕一圈。用元素运动代替镜头运动。
3. **硬切为主**，不炫技转场。5 秒一个知识点，直接切。
4. **构图三种，轮着用**：居中（大字/大数字）、左右分栏（左边文字右边图）、顶天立地（主体占中）。边缘至少留 15–20% 安全边距，文字绝不顶死。
5. **配色极简**：浅米白底（`#F6F5F2` 类）+ 黑色文字 + **一个**强强调色（标杆用砖红 `#DF4B38`）。强调色只给动词、数字、结论。
6. **字重拉层级**：标题极粗，正文极细。不用颜色拉层级，用字重和字号。

底部字幕规格：黑底白字胶囊，小号，只放金句/总结，不是逐句台词。

### 拆参考片的方法（可复用）

想学一个标杆视频，不要逐帧看。每 5 秒抽一帧，拼成联络表，一次丢给视觉模型：

```bash
for t in 1 5 10 15 20 25 30 35 40 45; do ffmpeg -ss $t -i ref.mp4 -vframes 1 f$t.png; done
magick montage f*.png -tile 5x2 -geometry +4+4 -resize 380x sheet.png
python3 ~/.hermes/scripts/vision.py sheet.png "分析制作规律：场景怎么切、每屏几个元素、镜头有没有动、字幕怎么处理"
```

问“规律”不要问“好不好看”，一次能拿到六条可执行规则（见上）。片子看完就删，只留规则。

## 二、先找教学主线（最重要的一步）

**不要按段落切场景。** 找出观众唯一要记住的那个想法，删掉旁支，围绕它组织序列。

先回答三个问题，写进分镜表头部：

1. 观众看完要记住的**一句话**是什么
2. 他现在的误解是什么，哪一步会让他“哦”一下
3. 结尾落在哪（判断句 / 动作 / 复述）

四种落地方式，选一个，不要混：

| 方式 | 结构 | 适用 |
|---|---|---|
| 理解一个想法 | 有用的问题开场 → 一层层揭示机制 | 概念解释（“X 是什么”） |
| 跟随一个过程 | **一个固定舞台**，按观众需要的顺序展示每步 | 流程、操作、生产线 |
| 记住三个要点 | 平行、具体、视觉可区分 | 清单、方法、对比 |
| 通过故事 | 一个案例：设定 → 张力 → 普遍教训 | 案例、复盘、人物 |

## 三、一个场景一个想法（最大质量杠杆）

每个场景只承载一个想法，给一个**可动的焦点**（一张图、一个数字、一个动作）。

- 两个想法塞一个场景 → 没有焦点可动 → 读起来是文字倾倒
- 一个场景 3–6 秒；总长由旁白/字幕决定，**不要写死“60 秒”**，写“约 60 秒”
- 场景内部结构统一（同样的标题位置、同样的留白），观众才不用每屏重新学习

## 四、镜头：默认不动

这一条踩过坑，记住结论：

**默认固定机位。** 想强调某个东西，用画面内部的四招：

1. **聚光/压暗**：其余区域降亮度或降透明度（最平和，首选）
2. **元素放大**：主体 scale 1 → 1.08，其他元素退到 0.96
3. **数字/数据条生长**：让数量本身变化，而不是镜头推过去
4. **局部卡片**：在主体旁弹一张细节卡

镜头移动只服务于场景切换，且要有明确目的。**四个概念切四次镜头 = 观众晕**（辉哥原话）。

**场景边缘红线**：camera 一动就会露白。要么不动，要么把场景画布扩到 1.4 倍，让边界永远在画外。

## 五、转场：60–70% 用一种主转场

官方规则：**Pick ONE primary (60-70% of scene changes) plus 1-2 accents. Never use a different transition for every scene.**

按能量选：

| 能量 | 主转场 | 时长 | 缓动 |
|---|---|---|---|
| 平静（品牌、健康、克制） | 模糊交叉溶解、拉焦 | 0.5–0.8s | sine.inOut |
| 中等（企业、SaaS） | 推入滑移、分块入场 | 0.3–0.5s | power2/power3 |
| 高能（发布、运动、促销） | 穿透缩放、过曝 | 0.15–0.3s | power4/expo |

禁止跳切（jump cut）。每个场景的元素都要有入场动画，不要“已经在那了”。

## 六、素材：不要什么都自己画

| 要什么 | 从哪拿 | 说明 |
|---|---|---|
| 角色表演（走/指/说话） | **Lottie** | lottie-web + `window.__hfLottie.push(player)`，运行时会 seek；角色动作在 json 里，不用画 |
| 图标 | **Iconify API** | `https://api.iconify.design/solar/chef-hat-bold-duotone.svg?color=%23FA9704`；solar / ph 的 duotone 系列风格统一、质量高 |
| 现成动效 | **HyperFrames registry** | `npx hyperframes catalog` 看几百个 block；`npx hyperframes add <name>` 拉源码级可改 |
| 免费插画 | unDraw | `https://undraw.co/api/search?q=chef`；扁平单色，但人物无五官、抱胸，不适合当动态主角，只适合静态图示 |
| 场景插画 | AI 生成 | 需要 key（即梦/可灵/Nano Banana）；本机当前没有，要先用 `c456-gif` 里的纯矢量方案 |

## 七、技术要点（验过的写法）

### 虚拟相机要 seek 安全

GSAP 在 `tl.seek()` 时不触发 `onUpdate`，所以相机不能用回调驱动，要**属性 setter**：

```js
const camera = { _u:0, get u(){return this._u;}, set u(v){ this._u=v; applyCamera(v); } };
tl.to(camera, { u: 1, duration: 4, ease: "power2.inOut" }, 0);
```

### SVG 里 transformOrigin 用 bbox 相对值

GSAP 对 SVG 元素的 `transformOrigin` 是**相对元素 bbox 的**，不是用户坐标。手臂/腿的轴心：

- 从左上角开始的路径（右臂）→ `"0px 0px"`
- 从右上角开始的路径（左臂）→ `"100% 0px"`

写错的表现：整条手臂飞出去/脱节。用 `y` 位移代替旋转也不行——肩膀连接点会一起移走。

### 配件必须放进角色组

帽子、手里的道具如果是角色的兄弟节点，角色位移时它们不跟随（踩过：厨师走进来了，帽子和手臂留在原地）。配件要放进角色 `<g>` 内，用局部坐标。

### 缓动

- 入场：`power3.out` / `expo.out` / `back.out(1.4)`
- 出场：`power2.in` / `expo.in`
- 同一场景内至少 **3 种不同缓动**
- 落地要 squash（scaleY 压缩再回弹）、掉落到弹两下
- 不用 `repeat: -1`（破坏捕获引擎），要循环就算有限次数

### 时间统一

外面传 0–1 进度、内部按秒算，忘了乘 DURATION 会让动画停在第一帧且不报错。

### 字体必须是开源字体（硬性，不是建议）

PingFang SC、Songti SC 是苹果专有字体，不能用于对外发布的物料。**出片一律用 Noto Sans SC（思源黑体，SIL OFL）**，而且必须把字体文件放进项目，不靠系统字体。

```bash
npm pack @fontsource-variable/noto-sans-sc     # 4.4MB，variable 字重 100–900
mkdir -p assets/fonts && cp package/files/*.woff2 assets/fonts/   # 101 个 unicode-range 分片
```

把包里的 `index.css` 全量内联进 `<style>`，两处改写：

- `url(./files/` → `url(assets/fonts/`
- `'Noto Sans SC Variable'` → `'Noto Sans SC'`

CSS 栈写 `font-family: "Noto Sans SC", "Helvetica Neue", Arial, sans-serif;`

**不要用 `src: local("X")` 糊过 lint**：`local()` 只声明不嵌入，`check` 照样通过，但渲染机没有这个字体就直接 fallback，问题到别人机器上才炸。中文按 unicode-range 分 101 片是为了按需加载，不是体积问题——全量放进 assets 即可，渲染时浏览器自己只取用到的片。

### 元素默认不要写 opacity: 0

CSS 里 `.cap { opacity: 0 }` 配 `gsap.from("#cap", { opacity: 0 })` → `from` 的目标值取自 CSS 当前值（0），动画跑完还是透明。**元素永远不出现，`check` 也不报错**，只能靠抽帧看才发现。想让入场从透明开始，只用 `gsap.from`，CSS 保持默认（不写 opacity 或写 1）。

### 改画幅或屏数时，选择器必须跟着改

从竖屏版改横屏版、或从 8 屏砍到 6 屏时，样式里的 `#s8 .row` / `#s6 .row` 会对不上新 id。CSS 静默不生效、`check` 不报错，表现是整屏元素塌回左上角按文档流堆叠（图标变成一列小方块）。改完立刻跑一次 bbox，确认收尾屏的图标是水平排列、宽度铺满容器。

## 七、硬性验证流程（不要跳）

```bash
npm run check                                   # lint + layout + motion + contrast
npx hyperframes snapshot --at 1,3,5,8            # 抽帧
python3 ~/.hermes/scripts/vision.py frame.png "评价构图、主体、有没有切头切脚"
npm run render -- --output ../final.mp4
# 转公众号 GIF：10fps + 810 宽 + 160 色，恰好 ≤300 帧
ffmpeg -i final.mp4 -vf "fps=10,scale=810:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 out.gif
ffprobe -v error -show_entries stream=width,height,nb_frames -of csv=p=0 out.gif   # 确认 ≤300
```

## 八、公众号落地：GIF 不可靠时改静态帧

实测公众号上传 GIF 容易失败（体积/帧数/编码都可能卡）。可靠做法：**按屏抽帧，一屏一张静态图插到对应段落**，图随段落走。

```bash
ffmpeg -ss 7.5 -i final.mp4 -vframes 1 -q:v 3 frames/01-厨师.jpg
```

抽帧时：每屏取动画稳定后的时刻（入场动画结束后 0.5–1s），文件按文章出现顺序命名为 `01-xx.jpg … 10-xx.jpg`，方便在公众号后台按序上传。

check 会报的几类（都要修）：
- `font_family_without_font_face` → 按「字体必须是开源字体」装 Noto Sans SC，别用 PingFang 糊过去
- `multiple_root_compositions` → 备份的 html 不能留在项目目录
- `line_unread` → 结尾字幕停留 <2s，延长时长或提前出现
- `overlapping_gsap_tweens` → 两个 tween 抢同一个属性

**视觉模型看图**：本机 `vision_analyze` 工具走 gateway 的旧环境变量会 401，用 `~/.hermes/scripts/vision.py` 直连 deepseek-flash（它能看图）。审图时要给它具体问题（“帽子到脚是否都在画面内”），不要问“好不好看”。它也会把居中构图说成“重心偏左上”，描述位置可以信、审美判断要自己裁。

**静态 bbox 检查会误报**：不经过 HyperFrames 运行时直接打开页面时，所有 `.scene` 同时可见，测出来的重叠/出界全是假的。要测布局就先手动只显示当前屏：

```js
document.querySelectorAll('.scene').forEach(el => {
  el.style.display = (el.id === cur) ? 'block' : 'none';
});
```

## 九、分镜表模板

### 画幅先定：公众号一律 3:4

| 用途 | 画幅 | 设计尺寸 | 正文显示 | 缩放比 |
|---|---|---|---|---|
| **公众号正文（默认）** | **3:4** | 1080×1440 或 810×1080 | 677×903 | 0.63 |
| 视频号 / 抖音 | 9:16 | 1080×1920 | — | — |
| 纯图表/数据（少用） | 16:9 | 1920×1080 | 677×381 | 0.35 |

选 3:4 的硬理由是可读性，不是审美：

```
显示字号 = 设计字号 × 677 / 设计宽度
1920 宽 → 0.35 倍：48px 说明字显示成 17px，糊
1080 宽 → 0.63 倍：48px 说明字显示成 30px，清楚
```

3:4 字号下限（按 1080 宽设计）：主词 150–170px / 说明 46–50px / 字幕 38–42px / 英文与序号 26–30px。说明文字每行 **8–14 个汉字**，超了手机上会碎行拆词组。

### GIF 硬上限 300 帧

公众号上传动图只收 300 帧以下，超了直接传不上去。反推：

```
30s × 10fps = 300 帧   ← 卡在顶格
40s × 7fps  = 280 帧   ← 卡顿，不如压节奏
```

长内容**压节奏而不是降帧率**：八屏 × 3.75s = 30s，比八屏 × 5s 再降到 7fps 好看得多，短视频本来就该快。转完必须验：

```bash
ffprobe -v error -show_entries stream=width,height,nb_frames -of csv=p=0 out.gif
```

### 传不上去就降级成静态图

公众号对动图的上传限制不只帧数，实际常常直接传失败。别在一棵树上吊死：**视频是母版，GIF 和静态图都是从它派生的交付物**。

```bash
# 视频 → GIF（3:4，10fps 控在 300 帧内）
ffmpeg -i out.mp4 -vf "fps=10,scale=810:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle" -loop 0 out.gif

# 视频 → 每屏一张静态图（GIF 传不上去时的降级路径）
ffmpeg -ss <屏中段秒数> -i out.mp4 -vframes 1 -q:v 3 frames/01-xx.jpg
```

静态图交付时：按 `01-` `02-` 顺序命名（方便逐张上传素材库），按文章段落插入（一图一段，宽度 82%），**不要做左右滑动图集**——手机上滑不动，读者看不全。

公众号图文的层级/重点/配图规范见技能 `c456-wechat-layout`。

### 如果非要做 16:9（图表类）

横屏不能照搬竖屏的左右分栏——「左图标 + 右文字」会把内容挤在左半、右侧一大片死白。横屏改**垂直居中堆叠**：图标居中 → 英文注 → 中文大词 → 说明（居中，max-width ~1000）→ 底部字幕胶囊。

写代码前先填完，填不出就是还没想清：

```
片名 / 总时长 / 画幅
要记住的一句话：____
落地方式：理解想法 / 跟随过程 / 三个要点 / 故事

场景 1（0.0–4.0s）
  想法：____
  焦点：____（一个东西 + 一个动作）
  字幕：____（≤14 字）
  入场：____（缓动）

场景 2（4.0–8.0s）
  ...

转场：主 ____（用 70%）+ 点缀 ____（用 30%）
配色：底色 ____ / 主色 ____ / 强调 ____
```

## 十、反面清单

- ✗ 公众号动图用 16:9（字号腰斩）或 9:16（超过一屏）——一律 3:4
- ✗ GIF 超过 300 帧（公众号传不上去）
- ✗ 字幕元素 CSS 写 `opacity:0` 再 `gsap.from`（永远不出现）
- ✗ 一个场景塞四个概念，靠镜头切换逐个点名
- ✗ 用 PingFang / Songti 等系统专有字体出片（见「字体必须是开源字体」）
- ✗ 公众号正文放竖屏动图（超过一屏，读者看不全）
- ✗ 横屏照抄竖屏的左右分栏（右侧一大片死白）
- ✗ 每个场景换一种转场
- ✗ 机位乱飞导致画面边缘露白
- ✗ 手画所有素材（角色用 Lottie，图标用 Iconify）
- ✗ 只有“东西飞进来”，没有剧情节奏（每屏要有一句字幕说清这一屏在讲什么）
- ✗ 结尾字幕停留太短（少于 2 秒）
