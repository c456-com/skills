# CamoFox fork v1.17.0 运行契约

## 1. 来源与目录

唯一允许的 GitHub fork：

- HTTPS：<https://github.com/xiaohui-zhangxh/camofox-browser>
- SSH：`git@github.com:xiaohui-zhangxh/camofox-browser.git`

本机固定目录：`/Users/xiaohui/Codes/camofox-browser-fork`。

其他机器可以使用自己的绝对目录，但必须把它写入
`~/.camofox/camofox-local-root.txt`。记录文件是本机运行约定，不提交到任何仓库：

```bash
CAMOFOX_REPO_URL="git@github.com:xiaohui-zhangxh/camofox-browser.git"
CAMOFOX_LOCAL_ROOT="/absolute/path/to/camofox-browser-fork"
CAMOFOX_LOCAL_ROOT_RECORD="$HOME/.camofox/camofox-local-root.txt"

set -euo pipefail
mkdir -p "$(dirname "$CAMOFOX_LOCAL_ROOT_RECORD")"
printf '%s\n' "$CAMOFOX_LOCAL_ROOT" > "$CAMOFOX_LOCAL_ROOT_RECORD"

if [ -e "$CAMOFOX_LOCAL_ROOT" ]; then
  printf 'clone path already exists; choose a fresh directory or have the user remove it: %s\n' "$CAMOFOX_LOCAL_ROOT" >&2
  exit 1
fi

git clone "$CAMOFOX_REPO_URL" "$CAMOFOX_LOCAL_ROOT"

cd "$CAMOFOX_LOCAL_ROOT"
test "$(pwd -P)" = "$(cd "$CAMOFOX_LOCAL_ROOT" && pwd -P)"
test "$(git remote get-url origin)" = "$CAMOFOX_REPO_URL"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
node -e 'const p=require("./package.json"); if (p.version !== "1.17.0") process.exit(1)'
```

本机把上面的 `CAMOFOX_LOCAL_ROOT` 替换为固定路径；其他机器也必须使用
同一个已记录值，不能在不同步骤切换目录。

## 2. 锁依赖、严格编译、构建

全新 clone 后，以下命令必须在仓根执行，并要求每条命令退出码为 `0`：

```bash
cd "$CAMOFOX_LOCAL_ROOT"
npm ci
npx tsc -p .
npm run build
test -f dist/plugin.js
```

`npx tsc -p .` 是独立门禁。必须先看到该命令的真实成功退出码，再运行
build；build 的退出码不能替代严格 TypeScript 编译结果。任一步失败都停止，
不启动服务。

## 3. 从仓根启动

```bash
cd "$CAMOFOX_LOCAL_ROOT"
export CAMOFOX_INTERACTIVE=desktop
export CAMOFOX_WINDOW_SIZE=1280,800
export CAMOFOX_DEVICE_SCALE_FACTOR=2
export CAMOFOX_HUMANIZE=0.5
export CAMOFOX_SHOWCURSOR=1
npm start
```

| 配置 | 作用 |
| --- | --- |
| `CAMOFOX_INTERACTIVE=desktop` | 在本机桌面显示真实 Camoufox 窗口，供用户完成可见登录。 |
| `CAMOFOX_WINDOW_SIZE=1280,800` | 设置外层窗口尺寸；每维范围为 `100..4000`。 |
| `CAMOFOX_DEVICE_SCALE_FACTOR=2` | 设置截图 DPR；改变物理像素，不改变 CSS 布局。 |
| `CAMOFOX_HUMANIZE=0.5` | 将 Camoufox 输入时长限制为正数秒；只影响交互节奏。 |
| `CAMOFOX_SHOWCURSOR=1` | 显示 Camoufox 合成光标。 |

这些配置只在进程启动时读取。修改窗口、DPR 或交互参数后要完整重启服务。

## 4. 健康门禁

服务启动后，使用 `/health`，不要用根路径代替：

```bash
for attempt in $(seq 1 60); do
  body_file="$(mktemp)"
  status=$(curl -sS --max-time 3 -o "$body_file" -w '%{http_code}' \
    http://127.0.0.1:9377/health || true)
  if [ "$status" = "200" ] && \
     node -e 'const fs=require("fs"); const x=JSON.parse(fs.readFileSync(process.argv[1], "utf8")); process.exit(x.ok === true && x.browserConnected === true ? 0 : 1)' "$body_file"; then
    rm -f "$body_file"
    printf '%s\n' 'ready: HTTP 200, ok=true, browserConnected=true'
    exit 0
  fi
  rm -f "$body_file"
  [ "$attempt" -eq 60 ] && {
    printf '%s\n' 'CamoFox readiness gate failed' >&2
    exit 1
  }
  sleep 1
done
```

只有 HTTP `200`、JSON `ok: true`、JSON `browserConnected: true` 三项
同时成立才可继续。端口可连接或只返回 `ok: true` 都不够。

## 5. v1.17 viewport 事实

v1.17 创建 session context 时使用 `viewport: null`；页面布局服从外层
Camoufox/Firefox 窗口。`CAMOFOX_WINDOW_SIZE` 控制外层窗口，DPR 通过
Firefox 的 `layout.css.devPixelsPerPx` 偏好设置生效。工具栏会使内部页面高度
小于外层窗口高度，这是正常现象；需要改变尺寸时改配置并重启，不在已有进程上
做临时修补。
