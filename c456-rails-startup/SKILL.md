---
name: c456-rails-startup
description: "Rails startup / Rails + Inertia + React：当用户要从零创建 Rails 全栈应用、安装 Ruby/asdf、集成 Inertia.js、React、TypeScript、Vite、shadcn/ui、Tailwind CSS v4 或验证 hello-world 时触发；用于脚手架和环境搭建。"
version: 1.0.1
---

# Rails + Inertia + React + shadcn 从零搭建

从零到运行 hello-world 应用的分步指南。

## 检查清单

```text
- [ ] 0. 安装系统依赖、asdf、Ruby、Node
- [ ] 1. 创建项目目录
- [ ] 2. rails new
- [ ] 3. 安装 Inertia + Vite + React + TypeScript + Tailwind
- [ ] 4. 配置 @ 路径别名（shadcn 之前必须完成）
- [ ] 5. 初始化 shadcn/ui
- [ ] 6. 启动开发服务器并验证
- [ ] 7. Hello world 页面
```

---

## 0. 环境搭建

### 0.1 系统包（Ubuntu/Debian）

```bash
sudo apt update
sudo apt install -y git curl build-essential libssl-dev libreadline-dev \
  zlib1g-dev libyaml-dev libffi-dev libgdbm-dev libncurses5-dev
```

### 0.2 安装 asdf

```bash
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1
# bash: echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
# zsh:
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.zshrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.zshrc
source ~/.zshrc
```

### 0.3 通过 asdf 安装 Ruby

```bash
asdf plugin add ruby https://github.com/asdf-vm/asdf-ruby.git
asdf install ruby 4.0.5
asdf global ruby 4.0.5

ruby -v
gem install rails bundler
rails -v
```

项目 `.tool-versions`：

```text
ruby 4.0.5
```

### 0.4 Node.js（Vite 和 shadcn 需要）

使用 Node 20 或更新版本：

```bash
# 方式 A：asdf
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf install nodejs 22.14.0
asdf local nodejs 22.14.0

# 方式 B：系统 Node 或 nvm
node -v && npm -v
```

### 0.5 bin/dev 所需的进程管理器

`bin/dev` 需要 **foreman**、**overmind** 或 **hivemind**：

```bash
gem install foreman
# macOS: brew install overmind
```

---

## 1. 创建项目目录

```bash
mkdir -p ~/projects/my-rails-app
cd ~/projects/my-rails-app
git init
```

---

## 2. 初始化 Rails

在空目录（或只有 README / `.git` 的目录）中运行：

```bash
cd ~/projects/my-rails-app

rails new . \
  --database=sqlite3 \
  --css=tailwind \
  --skip-jbuilder \
  --name=MyRailsApp

bundle install
```

| 参数 | 用途 |
|------|------|
| `--database=sqlite3` | 简单的本地开发默认值 |
| `--css=tailwind` | Rails Tailwind 入口（Inertia 后续接管前端 CSS） |
| `.` | 在当前目录初始化 |

**不要**在此手动安装 Inertia——使用下一步的官方生成器。

---

## 3. 集成 Inertia + Vite + React + TypeScript + Tailwind

```bash
bundle add inertia_rails
bundle add vite_rails

bin/rails generate inertia:install \
  --framework=react \
  --typescript \
  --vite \
  --tailwind \
  --no-interactive
```

生成器将会：

- 安装 `vite_rails`、`@inertiajs/react`、`@inertiajs/vite`、`react`、`@vitejs/plugin-react` 等。
- 创建 `app/frontend/entrypoints/inertia.tsx`
- 配置 `Procfile.dev`（`web` + `vite`）
- 添加 `config/initializers/inertia_rails.rb`
- 提供 `inertia_example` 演示页面

确认 `app/views/layouts/application.html.erb` 包含：

```erb
<%= vite_react_refresh_tag %>
<%= vite_client_tag %>
<%= vite_javascript_tag "inertia.tsx" %>
<%= inertia_ssr_head %>
```

Inertia 页面的控制器继承 `InertiaController`：

```ruby
class PagesController < InertiaController
  def home
    render inertia: "Home", props: { message: "Hello, World!" }
  end
end
```

---

## 4. 路径别名（shadcn 之前必须完成）

shadcn 需要**两个** tsconfig 条目。参见 [Inertia Rails Cookbook](https://inertia-rails.dev/cookbook/integrating-shadcn-ui)。

**`tsconfig.app.json`**（Vite 构建）：

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./app/frontend/*"]
    }
  },
  "include": ["app/frontend/**/*.ts", "app/frontend/**/*.tsx", "vite.config.ts"]
}
```

**`tsconfig.json`**（shadcn CLI）：

```json
{
  "compilerOptions": {
    "baseUrl": "./app/frontend",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "references": [{ "path": "./tsconfig.app.json" }]
}
```

**`vite.config.ts`**（运行时解析）：

```typescript
import path from "path"
import react from "@vitejs/plugin-react"
import inertia from "@inertiajs/vite"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "vite"
import RubyPlugin from "vite-plugin-ruby"

export default defineConfig({
  plugins: [tailwindcss(), RubyPlugin(), inertia(), react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./app/frontend"),
    },
  },
})
```

---

## 5. 集成 shadcn/ui

### 5.1 初始化

```bash
npx shadcn@latest init
```

建议选项：

| 提示 | 选择 |
|------|------|
| 风格 | New York 或 base-nova |
| 基础色 | neutral |
| CSS 变量 | yes |
| Tailwind CSS 文件 | `app/frontend/entrypoints/application.css` |

成功标志：出现 `components.json`、`app/frontend/lib/utils.ts`，以及 `application.css` 中的 `@import "shadcn/tailwind.css"`。

### 5.2 添加组件

```bash
npx shadcn@latest add button card
```

组件存放在 `app/frontend/components/ui/`。

---

## 6. 启动并验证

### 6.1 安装依赖

```bash
bin/setup
# 或手动：
bundle install
npm install
bin/rails db:prepare
```

### 6.2 运行开发服务器

```bash
bin/dev
```

`Procfile.dev`：

```text
vite: bin/vite dev
web: bin/rails s
```

### 6.3 冒烟测试

| # | 检查项 | 预期结果 |
|---|--------|----------|
| S1 | 打开 `http://localhost:3000/inertia-example` | Inertia 演示页面正常渲染 |
| S2 | 浏览器控制台 | 无致命的 Vite / React 错误 |
| S3 | `GET /up` | 200 |

**localhost vs 127.0.0.1**：Vite HMR 需要一致的主机名。优先使用 `localhost`。可在 `config/routes.rb` 中将 `127.0.0.1` 重定向到 `localhost`。

---

## 7. Hello world

**路由和控制器：**

```ruby
# config/routes.rb
root "pages#home"

# app/controllers/pages_controller.rb
class PagesController < InertiaController
  def home
    render inertia: "Home", props: { message: "Hello, World!" }
  end
end
```

**Inertia 页面：**

```tsx
// app/frontend/pages/Home.tsx
import { Button } from "@/components/ui/button"

export default function Home({ message }: { message: string }) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
      <h1 className="text-3xl font-bold">{message}</h1>
      <Button>Get started</Button>
    </main>
  )
}
```

重启 `bin/dev`，打开 `http://localhost:3000/`——你应该能看到标题和带样式的按钮。

---

## 8. 推荐的前端目录结构

```text
app/frontend/
├── entrypoints/
│   ├── application.css
│   └── inertia.tsx
├── pages/              # Inertia 页面
├── components/
│   └── ui/             # shadcn 组件
├── layouts/
└── lib/
    └── utils.ts        # cn() 辅助函数
```

---

## 9. 故障排除

| 症状 | 修复方法 |
|------|----------|
| `No Tailwind CSS configuration found` | 确保 `application.css` 中有 `@import 'tailwindcss'`（v4）或 shadcn init 已完成 |
| `@/` 导入失败 | 检查 §4 中两个 tsconfig 和 `vite.config.ts` 的别名配置；重启 Vite |
| 空白页面 | 检查布局中是否有 `vite_javascript_tag "inertia.tsx"` 和 `yield` |
| HMR 失效 | 使用 `localhost`，不要用 `127.0.0.1` |
| `foreman: command not found` | 执行 `gem install foreman` 或安装 overmind |
| shadcn init 失败 | 先完成 §3（Inertia + Vite） |

---

## 10. 快速参考（全部步骤）

```bash
mkdir -p ~/projects/my-app && cd ~/projects/my-app
rails new . --database=sqlite3 --css=tailwind --skip-jbuilder
bundle add inertia_rails vite_rails
bin/rails generate inertia:install --framework=react --typescript --vite --tailwind --no-interactive
# 配置 §4 路径别名 + vite.config.ts
npx shadcn@latest init
npx shadcn@latest add button
bin/setup
bin/dev
```

---

## 参考资料

- [Inertia Rails · 服务端设置](https://inertia-rails.dev/guide/server-side-setup)
- [Inertia Rails · 集成 shadcn/ui](https://inertia-rails.dev/cookbook/integrating-shadcn-ui)
- [Inertia Rails Starter Kits](https://inertia-rails.dev/guide/starter-kits)
- [shadcn/ui](https://ui.shadcn.com)
- [Vite Ruby](https://vite-ruby.netlify.app/guide/rails)
