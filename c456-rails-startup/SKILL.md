---
name: c456-rails-startup
description: >-
  Bootstrap a Rails app with Inertia.js, React, TypeScript, Vite, shadcn/ui, and Tailwind CSS v4
  from scratch. Use when setting up a new Rails full-stack project, installing Ruby via asdf,
  integrating Inertia or shadcn/ui, or scaffolding a hello-world page.
---

# Rails + Inertia + React + shadcn Startup

Step-by-step guide to go from zero to a running hello-world app.

## Checklist

```text
- [ ] 0. Install system deps, asdf, Ruby, Node
- [ ] 1. Create project directory
- [ ] 2. rails new
- [ ] 3. Install Inertia + Vite + React + TypeScript + Tailwind
- [ ] 4. Configure @ path aliases (required before shadcn)
- [ ] 5. Initialize shadcn/ui
- [ ] 6. Start dev server and verify
- [ ] 7. Hello world page
```

---

## 0. Environment setup

### 0.1 System packages (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y git curl build-essential libssl-dev libreadline-dev \
  zlib1g-dev libyaml-dev libffi-dev libgdbm-dev libncurses5-dev
```

### 0.2 Install asdf

```bash
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.14.1
# bash: echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
# zsh:
echo '. "$HOME/.asdf/asdf.sh"' >> ~/.zshrc
echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.zshrc
source ~/.zshrc
```

### 0.3 Install Ruby with asdf

```bash
asdf plugin add ruby https://github.com/asdf-vm/asdf-ruby.git
asdf install ruby 4.0.5
asdf global ruby 4.0.5

ruby -v
gem install rails bundler
rails -v
```

Project `.tool-versions`:

```text
ruby 4.0.5
```

### 0.4 Node.js (required for Vite and shadcn)

Use Node 20 or newer:

```bash
# Option A: asdf
asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git
asdf install nodejs 22.14.0
asdf local nodejs 22.14.0

# Option B: system Node or nvm
node -v && npm -v
```

### 0.5 Process manager for bin/dev

`bin/dev` needs **foreman**, **overmind**, or **hivemind**:

```bash
gem install foreman
# macOS: brew install overmind
```

---

## 1. Create project directory

```bash
mkdir -p ~/projects/my-rails-app
cd ~/projects/my-rails-app
git init
```

---

## 2. Initialize Rails

Run in an empty directory (or one with only README / `.git`):

```bash
cd ~/projects/my-rails-app

rails new . \
  --database=sqlite3 \
  --css=tailwind \
  --skip-jbuilder \
  --name=MyRailsApp

bundle install
```

| Flag | Purpose |
|------|---------|
| `--database=sqlite3` | Simple local dev default |
| `--css=tailwind` | Rails Tailwind entry (Inertia takes over frontend CSS later) |
| `.` | Initialize in the current directory |

Do **not** install Inertia manually here — use the official generator in the next step.

---

## 3. Integrate Inertia + Vite + React + TypeScript + Tailwind

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

The generator will:

- Install `vite_rails`, `@inertiajs/react`, `@inertiajs/vite`, `react`, `@vitejs/plugin-react`, etc.
- Create `app/frontend/entrypoints/inertia.tsx`
- Configure `Procfile.dev` (`web` + `vite`)
- Add `config/initializers/inertia_rails.rb`
- Provide an `inertia_example` demo page

Confirm `app/views/layouts/application.html.erb` includes:

```erb
<%= vite_react_refresh_tag %>
<%= vite_client_tag %>
<%= vite_javascript_tag "inertia.tsx" %>
<%= inertia_ssr_head %>
```

Controllers for Inertia pages inherit `InertiaController`:

```ruby
class PagesController < InertiaController
  def home
    render inertia: "Home", props: { message: "Hello, World!" }
  end
end
```

---

## 4. Path aliases (required before shadcn)

shadcn needs **two** tsconfig entries. See [Inertia Rails Cookbook](https://inertia-rails.dev/cookbook/integrating-shadcn-ui).

**`tsconfig.app.json`** (Vite build):

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

**`tsconfig.json`** (shadcn CLI):

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

**`vite.config.ts`** (runtime resolution):

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

## 5. Integrate shadcn/ui

### 5.1 Initialize

```bash
npx shadcn@latest init
```

Suggested prompts:

| Prompt | Choice |
|--------|--------|
| Style | New York or base-nova |
| Base color | neutral |
| CSS variables | yes |
| Tailwind CSS file | `app/frontend/entrypoints/application.css` |

Success: `components.json`, `app/frontend/lib/utils.ts`, and `@import "shadcn/tailwind.css"` in `application.css`.

### 5.2 Add components

```bash
npx shadcn@latest add button card
```

Components land in `app/frontend/components/ui/`.

---

## 6. Start and verify

### 6.1 Install dependencies

```bash
bin/setup
# or manually:
bundle install
npm install
bin/rails db:prepare
```

### 6.2 Run dev server

```bash
bin/dev
```

`Procfile.dev`:

```text
vite: bin/vite dev
web: bin/rails s
```

### 6.3 Smoke checks

| # | Check | Expected |
|---|-------|----------|
| S1 | Open `http://localhost:3000/inertia-example` | Inertia demo page renders |
| S2 | Browser console | No fatal Vite / React errors |
| S3 | `GET /up` | 200 |

**localhost vs 127.0.0.1:** Vite HMR needs a consistent host. Prefer `localhost`. Optionally redirect `127.0.0.1` to `localhost` in `config/routes.rb`.

---

## 7. Hello world

**Route and controller:**

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

**Inertia page:**

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

Restart `bin/dev`, open `http://localhost:3000/` — you should see the heading and styled button.

---

## 8. Recommended frontend layout

```text
app/frontend/
├── entrypoints/
│   ├── application.css
│   └── inertia.tsx
├── pages/              # Inertia pages
├── components/
│   └── ui/             # shadcn components
├── layouts/
└── lib/
    └── utils.ts        # cn() helper
```

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `No Tailwind CSS configuration found` | Ensure `application.css` has `@import 'tailwindcss'` (v4) or shadcn init completed |
| `@/` imports fail | Verify §4 aliases in both tsconfigs and `vite.config.ts`; restart Vite |
| Blank page | Check layout has `vite_javascript_tag "inertia.tsx"` and `yield` |
| HMR broken | Use `localhost`, not `127.0.0.1` |
| `foreman: command not found` | `gem install foreman` or install overmind |
| shadcn init fails | Complete §3 (Inertia + Vite) first |

---

## 10. Quick reference (all steps)

```bash
mkdir -p ~/projects/my-app && cd ~/projects/my-app
rails new . --database=sqlite3 --css=tailwind --skip-jbuilder
bundle add inertia_rails vite_rails
bin/rails generate inertia:install --framework=react --typescript --vite --tailwind --no-interactive
# configure §4 path aliases + vite.config.ts
npx shadcn@latest init
npx shadcn@latest add button
bin/setup
bin/dev
```

---

## References

- [Inertia Rails · Server-Side Setup](https://inertia-rails.dev/guide/server-side-setup)
- [Inertia Rails · Integrating shadcn/ui](https://inertia-rails.dev/cookbook/integrating-shadcn-ui)
- [Inertia Rails Starter Kits](https://inertia-rails.dev/guide/starter-kits)
- [shadcn/ui](https://ui.shadcn.com)
- [Vite Ruby](https://vite-ruby.netlify.app/guide/rails)
