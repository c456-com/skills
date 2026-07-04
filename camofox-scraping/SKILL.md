---
name: camofox-scraping
description: "Scrape Cloudflare-protected pages using CamoFox anti-detection browser via npx. No local clone needed. If a site blocks CamoFox, fall back to web_search."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [scraping, camofox, browser-automation, research, cloudflare]
---

# CamoFox Web Scraping

Scrape sites using CamoFox anti-detection browser — when it works. **Don't fight it when it doesn't.** Use the fallback.

## Setup (no clone needed)

```bash
# Start — no git clone, no local repo
npx @askjo/camofox-browser

# Headful mode (visible browser for login)
CAMOFOX_HEADLESS=false npx @askjo/camofox-browser

# Port 9377, verify: curl -s http://localhost:9377/
```

That's it. No `~/Codes/camofox-browser`, no local modifications.

## Philosophy: Accept what works, skip what doesn't

Camofox is a tool, not a project. If it can't access a site, don't patch it — use web_search instead.

| Situation | Response |
|-----------|----------|
| Camofox works | Use it |
| Camofox blocked (Reddit) | web_search for summaries; note the gap |
| Camofox crashes | Restart with same userId — persistence restores logins |
| Viewport/isMobile bug | Known upstream Camoufox issue. Don't patch Playwright. Wait or use fallback. |

## API Workflow

### Create a tab

```bash
curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"researcher","sessionKey":"<session-key>"}'
```

### Navigate + extract — standard steps

See `references/camofox-web-scraping.md` for full reference. Key parameter: `expression` (NOT `script`).

## Persistence (skip login troubles)

```bash
# Close session gracefully before restart
curl -s -X DELETE "http://localhost:9377/sessions/<userId>"

# Then pkill is safe
pkill -f "node server.js"
```

## Fallback pattern

When Camofox fails (Reddit, broken binary, etc.):

```python
from hermes_tools import web_search
results = web_search(query="site:reddit.com keyword")
```

Log the gap in the research report so it's transparent to the user.

## Pitfalls

- **npx only** — never clone the repo. `npx @askjo/camofox-browser` is the only supported method.
- **Don't patch Playwright** — if the Camoufox binary doesn't support a feature, accept it as a limitation.
- **Reddit blocks Camofox** — use web_search fallback.
- **Persistence needs DELETE /sessions/:userId before pkill** — without this, login state is lost.
