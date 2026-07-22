---
name: cli-doc-landing
tags: [cli, landing-page, html, documentation, website]
description: "CLI 文档介绍页 / CLI landing page generator：当用户要为 CLI 工具生成产品介绍页面、创建命令参考文档、做工具官网、或展示 CLI 的安装/特性/工作流/FAQ 时触发；输出单文件自包含 HTML 页面，结构源自 yixiaoer.cn/cli，独立配色风格。"
version: "1.0.0"
related_skills: []
---

# CLI Documentation Landing Page Generator

> Generate a self-contained, production-quality HTML page that introduces a CLI tool. The structure is distilled from [yixiaoer.cn/cli](https://www.yixiaoer.cn/cli) — a proven landing page pattern for CLI tools aimed at AI Agent/developer audiences.

---

## Trigger

Use this skill when the user wants to:
- "Create a landing page for my CLI tool"
- "Generate a CLI documentation website"
- "Make a beautiful HTML page for my command-line tool"
- "Distill a CLI page design into a reusable template"

## Input Data

You need to collect or be provided with:

| Field | Required | Description |
|-------|----------|-------------|
| `cli_name` | ✅ | The CLI command name (e.g. `yxer`, `c456`, `hermes`) |
| `cli_subtitle` | ✅ | One-line value proposition |
| `cli_description` | ✅ | 1-2 sentence description of what the CLI does |
| `badge_text` | ✅ | Badge label (e.g. "蚁小二 CLI for Agent", "c456 CLI") |
| `install_code` | ✅ | The primary install command to show in the terminal window |
| `install_instructions` | ✅ | Text explaining how/when to install |
| `links` | ✅ | Array of `{label, url}` — e.g. API Key, Download, Source |
| `features` | ✅ | Array of `{icon: 'lucide-icon-name', title, description}` (4 recommended) |
| `agent_tools` | ✅ | Array of tool names (e.g. Codex, Cursor, Claude Code) |
| `domains` | ✅ | Array of `{icon, title, description}` — business domain cards (9 recommended) |
| `steps` | ✅ | Array of `{number, command}` — the numbered workflow steps (7 recommended) |
| `commands` | ✅ | Array of `{label, command}` — command reference table |
| `faq` | ✅ | Array of `{question, answer}` — FAQ items |
| `cta_heading` | ✅ | CTA section heading |
| `cta_description` | ✅ | CTA section description |
| `cta_buttons` | ✅ | Array of `{label, url, primary: bool}` |
| `color_theme` | Optional | Override color scheme (see §Color Theme) |

## Output

A **single self-contained HTML file** with:
- All CSS inlined (via Tailwind CDN + custom styles)
- All icons from Lucide CDN
- No external dependencies beyond CDN scripts
- Responsive design (mobile-first)
- Dark/light awareness via inline `style` blocks

---

## §1 Page Structure

The page follows this section order (all optional — omit empty sections):

```
1. NAV (sticky top bar with logo + nav links)
2. HERO (badge → heading → description → install card → action links)
3. VIDEO (optional — section with video player)
4. FEATURES (4-column grid of value prop cards)
5. AGENT TOOLS (grid of supported agent tool logos)
6. BUSINESS DOMAINS (3-column grid of capability cards)
7. STANDARD WORKFLOW (numbered steps: left text + right command list)
8. AGENT EXAMPLE (one-sentence skill → automated execution trace)
9. COMMAND REFERENCE (grid of label+command pairs)
10. PUBLISHING DISCIPLINE (sidebar with rules list — optional)
11. FAQ (2-column grid of Q&A cards)
12. CTA (dark background, heading + buttons)
13. FOOTER (copyright, links)
```

### 1.1 Hero Section

```html
<section id="top" class="relative overflow-hidden">
  <div class="absolute inset-x-0 top-0 h-[520px] bg-[linear-gradient(180deg,#eef2ff_0%,#ffffff_100%)]"></div>
  <div class="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-6 pb-16 pt-20 lg:grid-cols-[1fr_560px] lg:px-0 lg:pt-24">
    <!-- Left: text -->
    <div>
      <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-[#dfe3ff] bg-white px-4 py-2 text-sm font-medium text-[#4F46E5] shadow-sm">
        <svg><!-- sparkles icon --></svg>
        {badge_text}
      </div>
      <h1 class="max-w-3xl text-[42px] font-extrabold leading-[1.12] text-[#101828] md:text-[58px]">{cli_subtitle}</h1>
      <p class="mt-6 max-w-2xl text-lg leading-8 text-[#5f6675]">{cli_description}</p>
    </div>
    <!-- Right: Install card -->
    <div id="install" class="rounded-[8px] border border-[#dfe4f2] bg-white p-4 shadow-[0_30px_80px_rgba(16,24,40,0.14)]">
      ...
    </div>
  </div>
</section>
```

### 1.2 Install Card

The install card looks like a terminal window:

```html
<div class="rounded-[8px] border border-[#dfe4f2] bg-white p-4 shadow-[0_30px_80px_rgba(16,24,40,0.14)]">
  <div class="inline-flex w-fit items-center rounded-full bg-sky-50 px-3 py-1 text-xs font-medium text-sky-700">
    Install Badge
  </div>
  <p class="mt-5 text-sm leading-6 text-[#667085]">{install_instructions}</p>
  <div class="mt-4 rounded-[8px] bg-[#101828] p-4">
    <div class="mb-4 flex items-center justify-between border-b border-white/10 pb-4">
      <div class="flex items-center gap-2">
        <span class="h-3 w-3 rounded-full bg-[#ff5f57]"></span>
        <span class="h-3 w-3 rounded-full bg-[#ffbd2e]"></span>
        <span class="h-3 w-3 rounded-full bg-[#28c840]"></span>
        <span class="ml-3 text-sm text-white/54">Terminal Title</span>
      </div>
      <button class="...">复制</button>
    </div>
    <pre class="overflow-x-auto whitespace-pre-wrap text-sm leading-7 text-[#d6e2ff]"><code>{install_code}</code></pre>
  </div>
  <div class="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-sm text-[#667085]">
    {action_links}
  </div>
</div>
```

### 1.3 Feature Cards

4-column grid with icon + title + description:

```html
<section class="bg-white pb-20">
  <div class="mx-auto max-w-7xl px-6 lg:px-0">
    <div class="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
      <!-- repeat for each feature -->
      <div class="rounded-[8px] border border-[#e7eaf3] bg-white p-6 shadow-[0_10px_30px_rgba(16,24,40,0.04)]">
        <div class="mb-5 flex h-11 w-11 items-center justify-center rounded-[8px] bg-[#eef2ff] text-[#4F46E5]">
          {lucide_icon}
        </div>
        <h2 class="text-lg font-bold text-[#151b2d]">{title}</h2>
        <p class="mt-3 text-sm leading-6 text-[#667085]">{description}</p>
      </div>
    </div>
  </div>
</section>
```

### 1.4 Command Reference Table

Label + command code pairs in a grid:

```html
<div class="overflow-hidden rounded-[8px] border border-[#e3e8f5] bg-white">
  <!-- repeat for each command -->
  <div class="grid grid-cols-1 gap-2 border-b border-[#eef1f7] px-5 py-4 last:border-b-0 md:grid-cols-[150px_1fr]">
    <span class="text-sm font-semibold text-[#4b5565]">{label}</span>
    <code class="min-w-0 break-words text-sm text-[#101828]">{command}</code>
  </div>
</div>
```

### 1.5 Standard Workflow

Numbered steps:

```html
<div class="grid gap-3">
  <!-- repeat for each step -->
  <div class="flex items-center gap-4 rounded-[8px] bg-[#f8faff] p-4">
    <span class="flex h-8 w-8 flex-none items-center justify-center rounded-full bg-[#4F46E5] text-sm font-bold text-white">{number}</span>
    <code class="min-w-0 break-words text-sm font-semibold text-[#273044]">{command}</code>
  </div>
</div>
```

### 1.6 FAQ Cards

2-column grid:

```html
<div class="grid grid-cols-1 gap-5 lg:grid-cols-2">
  <!-- repeat for each FAQ -->
  <div class="rounded-[8px] border border-[#e3e8f5] bg-white p-6">
    <h3 class="text-lg font-bold text-[#151b2d]">{question}</h3>
    <p class="mt-3 text-sm leading-6 text-[#667085]">{answer}</p>
  </div>
</div>
```

### 1.7 CTA Section

```html
<section class="bg-[#101828] py-16 text-white">
  <div class="mx-auto flex max-w-7xl flex-col items-start justify-between gap-8 px-6 lg:flex-row lg:items-center lg:px-0">
    <div>
      <h2 class="text-3xl font-extrabold">{cta_heading}</h2>
      <p class="mt-3 max-w-2xl text-base leading-7 text-white/68">{cta_description}</p>
    </div>
    <div class="flex flex-col gap-3 sm:flex-row">
      <!-- primary button -->
      <a href="{url}" class="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-white px-6 text-base font-semibold text-[#101828] transition hover:bg-[#eef2ff]">{label}</a>
      <!-- secondary button -->
      <a href="{url}" class="inline-flex h-12 items-center justify-center rounded-lg border border-white/24 px-6 text-base font-semibold text-white transition hover:bg-white/10">{label}</a>
    </div>
  </div>
</section>
```

---

## §2 Color Theme

Default theme (蚁小二 style):

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#4F46E5` (indigo-600) | Icons, badges, step numbers, buttons |
| `primary-light` | `#eef2ff` | Icon backgrounds, section backgrounds |
| `primary-border` | `#dfe3ff` | Badge border |
| `text-dark` | `#101828` | Headings |
| `text-body` | `#171923` | Body text |
| `text-muted` | `#667085` | Secondary text |
| `bg-light` | `#f6f8fc` | Alternating section background |
| `card-border` | `#e7eaf3` | Card borders |
| `code-bg` | `#101828` | Code block background |
| `code-text` | `#d6e2ff` | Code block text |
| `section-alt-bg` | `#fbfcff` | Alternate card background |
| `step-bg` | `#f8faff` | Step item background |

To customize, pass `color_theme` with overrides:

```json
{
  "color_theme": {
    "primary": "#059669",
    "primary-light": "#ecfdf5",
    "primary-border": "#a7f3d0",
    "text-dark": "#111827"
  }
}
```

---

## §3 Lucide Icon Mapping

The page uses Lucide icons. Common icons used in CLI landing pages:

| Use Case | Icon Name |
|----------|-----------|
| Hero badge | `sparkles` |
| AI Agent | `bot` |
| Validation | `clipboard-check` |
| Cloud/Upload | `cloud-upload` |
| Sync | `refresh-cw` |
| Code | `code-xml` |
| Users | `users-round` |
| Monitor | `monitor-check` |
| Layers | `layers` |
| File JSON | `file-json-2` |
| Library | `library` |
| Search | `search-check` |
| Help | `circle-help` |
| Package | `package-check` |
| Shield | `shield-check` |
| Terminal | `terminal` |
| Calendar | `calendar-check` |
| Copy | `copy` |
| Check circle | `circle-check` |

Usage: `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">{paths}</svg>`

---

## §4 Complete HTML Template

This is the full HTML template structure. Generate a complete, self-contained HTML file:

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{cli_name} CLI — {tagline}</title>
  <meta name="description" content="{cli_description}"/>
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Lucide icons (lazy-load at end of body) -->
  <style>
    /* Any custom overrides */
    html { scroll-behavior: smooth; }
  </style>
</head>
<body class="bg-[#f6f8fc] text-[#171923]">
  <!-- NAV (optional) -->
  <nav class="sticky top-0 z-50 border-b border-[#e7eaf3] bg-white/90 backdrop-blur-sm">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-0">
      <span class="text-lg font-bold text-[#101828]">{cli_name}</span>
      <div class="flex items-center gap-6 text-sm text-[#667085]">
        <a href="#install" class="hover:text-[#4F46E5]">安装</a>
        <a href="#features" class="hover:text-[#4F46E5]">特性</a>
        <a href="#commands" class="hover:text-[#4F46E5]">命令</a>
        <a href="#faq" class="hover:text-[#4F46E5]">FAQ</a>
      </div>
    </div>
  </nav>

  <!-- HERO -->
  <!-- (full hero section as described in §1.1-1.2) -->

  <!-- VIDEO (optional) -->
  <!-- (video section with player) -->

  <!-- FEATURES -->
  <!-- (4-column feature cards as §1.3) -->

  <!-- AGENT TOOLS -->
  <!-- (supported agent tools grid) -->

  <!-- BUSINESS DOMAINS -->
  <!-- (9-card capability grid) -->

  <!-- STANDARD WORKFLOW -->
  <!-- (numbered steps section) -->

  <!-- COMMAND REFERENCE -->
  <!-- (label+command table) -->

  <!-- PUBLISHING DISCIPLINE (optional) -->
  <!-- (rules list sidebar) -->

  <!-- FAQ -->
  <!-- (Q&A cards grid) -->

  <!-- CTA -->
  <!-- (dark section with buttons) -->

  <!-- FOOTER -->
  <footer class="border-t border-[#e7eaf3] bg-white py-8 text-center text-sm text-[#667085]">
    <p>&copy; {year} {cli_name}. All rights reserved.</p>
  </footer>

  <!-- Lucide icons script (loads icons via data-lucide attributes) -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>lucide.createIcons();</script>
</body>
</html>
```

---

## §5 Implementation Workflow

When asked to generate a CLI landing page:

1. **Collect input data** — ask the user for the data fields listed in §Input Data, or use defaults if the user provides minimal info.

2. **Map features to icons** — choose appropriate Lucide icons for each feature/domain.

3. **Assemble the HTML** — follow the template structure in §4, replacing placeholders with actual data.

4. **Verify output** — the page should be:
   - Self-contained (single file, no broken links)
   - Responsive (test at mobile, tablet, desktop widths)
   - Accessible (proper heading hierarchy, alt text)
   - Visually polished (consistent spacing, rounded corners, shadows)

5. **Write to file** — save as `{cli_name}-cli-landing.html` in the current working directory or a dedicated `output/` folder.

---

## §6 Example

For an example of the final output style, see [yixiaoer.cn/cli](https://www.yixiaoer.cn/cli) — this skill's structural pattern is directly extracted from that page.

Generated example: [c456 CLI landing page](https://c456.com/cli) — the c456 CLI's own landing page built with this skill.

---

## §7 Pitfalls

| Issue | Solution |
|-------|----------|
| Lucide icons not rendering | Ensure `lucide.createIcons()` runs after the DOM is ready; place the script at the end of `<body>` |
| Tailwind classes not working | Use `@tailwindcss/cdn` or include the CDN script; avoid custom config that CDN can't handle |
| Copy button on install code | The copy button in the template is a UI element; for a static HTML page, either omit it or make it non-functional with a disabled appearance |
| Dark mode | Current design is light-mode optimized; if dark mode needed, add `prefers-color-scheme` media query overrides |
| Too many CDN requests | Tailwind + Lucide = 2 CDN requests; acceptable for a landing page but pre-bundle if used in production |
