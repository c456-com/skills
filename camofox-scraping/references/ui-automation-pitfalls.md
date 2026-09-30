# UI 自动化实测坑（浏览器驱动现代 Web 应用）

> 这些坑是在真实前端（React + Radix/shadcn 组件库）上驱动浏览器时踩出来的，
> 与具体站点无关。用 CamoFox 的 `/click`、`/type`、`/evaluate` 或任何 CDP 驱动时都适用。

## 坑 1：CLI 的参数顺序 —— 子命令专属参数必须放在子命令**之后**

`camofox.py` 把 `--base` / `--user` / `--tab` 注册在**各个子命令**的 parser 上
（源码 `add_common(p)`），不是全局参数。放前面会报
`invalid choice: 'http://127.0.0.1:9377'`。

```bash
# ✗ 错
python3 camofox.py --base http://127.0.0.1:9377 --user cto --tab $TAB click --ref e4
# ✓ 对
python3 camofox.py click --base http://127.0.0.1:9377 --user cto --tab $TAB --ref e4
```

包个壳就能少踩：

```bash
cf() { python3 camofox.py "$1" --base "$B" --user "$U" --tab "$TAB" "${@:2}"; }
```

## 坑 2：`element.click()` 对 Radix / shadcn 组件无效 —— 必须真实指针事件

**这是最贵的一个坑。** Radix 的 Tabs / Sheet / DropdownMenu 走 **pointer 事件**，
在 `evaluate` 里跑 `el.click()` 只会触发 React 合成 click，**组件不响应** ——
表现为「点了没反应」，或「弹出了另一个面板」（实测：点「系统管理」弹出的是
另一个调试面板，误以为进错地方）。

正确做法两条：

1. 有 `coordinates` 支持的 click 端点 ⇒ 先 `evaluate` 取 `getBoundingClientRect()`
   中心坐标，再按坐标点；
2. 或先 `hover`（鼠标真实移动过去）再点击 —— 用户能在有头窗口里看见鼠标轨迹。

**⛔ 别用「点了没反应」推断「路径/元素不存在」** —— 先怀疑 JS click 无效，
改用坐标或 hover 再试。

## 坑 3：可见操作 = 先 hover 再 click

需要让人眼跟上时，坐标直点会「啪」地跳过去，看不出点了哪里。
先 `POST /act {"kind":"hover","selector":...}` → 停 ~0.4s → 取中心坐标 → 停 ~0.45s →
按坐标 click。停顿是为了让操作可跟随，不影响任何判据。

## 坑 4：登录态不能用 `document.cookie` 判断

会话 cookie 是 **HttpOnly**，`document.cookie` 读不到它（只能看到 CSRF 之类的
非 HttpOnly cookie），据此判「没登录」是**错的**。

正确判据任选其一：

- 页面内带凭据请求接口：`fetch('/api/...').then(r => r.status)` ⇒ 200 才算真登录；
- UI 上有「退出登录 / 当前用户」；
- 驱动服务端日志里有对应的成功请求（`Completed 200`）。

## 坑 5：权限菜单可能不在侧栏 —— 先读接口返回，别只盯 DOM

一些前端把 admin-only 的菜单组**从侧栏主列表里扁平化**到接口返回的独立字段
（如 `admin_items`），DOM 侧栏根本查不到。

⛔ 判据：先看接口返回里有没有那个字段与分组，不要在侧栏主列表里反复找。
展开入口通常在**左下角用户菜单**，而不是侧栏。

## 坑 6：窄容器 / 响应式场景 —— 改容器 CSS，别缩浏览器窗口

缩窗口会连带改掉同一批其它截图的版式。正确做法：在 `evaluate` 里把**目标容器**
的 CSS 宽度调到 480–560px 触发布局变化，并在对照文档里写明造法。

验收自查：截图物理像素宽高不变（= 窗口没动过），只有容器变窄。

## 坑 7：每张截图必须真的打开看

DOM 断言、测试绿灯、无报错 —— **都不等于看过**。每张拍完用视觉工具实际打开核：
文字大小是否正常、关键字段是否在、要证明「已消失」的元素是否真的没有。

⛔ 视觉服务连接失败时**报「未核」**，不要默认合格。
