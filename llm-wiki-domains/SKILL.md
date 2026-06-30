---
name: llm-wiki-domains
description: >-
  Multi-domain knowledge base navigator on top of Karpathy's LLM Wiki.
  Each domain is an independent llm-wiki instance; a root index provides
  cross-domain navigation. Use when building multi-topic knowledge bases
  with isolated domains under a common index.
tags:
  - wiki
  - knowledge-base
  - domains
  - multi-domain
  - meta-wiki
  - llm-wiki
related_skills:
  - llm-wiki
---

# LLM Wiki Domains — Multi-Domain Knowledge Base Navigator

> **Build a cross-domain knowledge base where each domain is an independent [llm-wiki](https://hermes-agent.nousresearch.com/docs/skills/research/llm-wiki) instance, connected by a root index.**

This skill adds a **multi-domain container layer** on top of the standard llm-wiki pattern. Instead of a single flat knowledge base, you get:

```
my-brain/
├── AGENTS.md                    ← Root schema
├── wiki/index.md                ← Global index + domain registry
├── wiki/log.md                  ← Global action log
├── raw/                         ← Cross-domain fragments
├── domains/
│   ├── stock-trading/           ← Independent llm-wiki instance
│   │   ├── AGENTS.md
│   │   ├── raw/  wiki/  output/
│   ├── ai-research/             ← Independent llm-wiki instance
│   │   ├── AGENTS.md
│   │   ├── raw/  wiki/  output/
└── shared/wiki/                 ← Optional cross-domain summaries
```

## Prerequisites

- **`llm-wiki`** Hermes skill must be installed. This skill handles the multi-domain
  navigation layer; the actual ingest/query/lint operations delegate to llm-wiki
  within each domain.
- **Obsidian** (optional) — the wiki directory works as an Obsidian vault out of the box.
  `[[wikilinks]]` render as clickable links, Graph View works, YAML frontmatter
  powers Dataview queries.

## Architecture

### Two-Layer Structure

| Layer | Path | Responsibility |
|-------|------|----------------|
| **Root** | `./` | Cross-domain fragments, tools research, domain registry |
| **Domain** | `domains/<name>/` | Self-contained llm-wiki instance (raw + wiki + output) |

The root layer holds a **domain registry** in `wiki/index.md` that maps domain
names to their paths. Each domain is a fully independent knowledge base that
follows the standard llm-wiki three-layer architecture (raw → wiki → schema).

### Directory Layout

```
{{PROJECT_NAME}}/
├── AGENTS.md                    ← Root schema (this navigation layer)
├── .gitignore                   ← With .config/ entries
├── .config/                     ← Skill-specific config (gitignored)
├── raw/                         ← Cross-domain source material
│   ├── articles/  books/  papers/  courses/
│   ├── resources/  quotes/  tools/  work/
├── wiki/                        ← Global knowledge (root level)
│   ├── index.md                 ← Global index + domain registry
│   ├── log.md                   ← Append-only action log
│   ├── entities/  concepts/  threads/  sources/  agents/
├── shared/wiki/                 ← Cross-domain compilations (optional)
│   ├── index.md
│   └── log.md
├── domains/                     ← Domain containers
│   └── <domain-name>/
│       ├── AGENTS.md            ← Domain-specific schema
│       ├── raw/                 ← Domain source material
│       │   ├── articles/  books/  papers/  courses/
│       │   ├── resources/  quotes/  tools/  work/
│       ├── wiki/                ← Domain wiki (llm-wiki standard)
│       │   ├── index.md  log.md
│       │   ├── entities/  concepts/  threads/  sources/
│       └── output/              ← Domain output artifacts
├── output/                      ← Global output artifacts (optional)
└── .tmp/                        ← Temporary files
```

### Cross-Domain Retrieval Protocol

1. **Root first**: Read `wiki/index.md` for the domain registry
2. **Locate domain**: Find the relevant `domains/<name>/` path from the registry
3. **Domain search**: Read that domain's `wiki/index.md` for its content catalog
4. **Cross-domain search**: `rg -l "keyword" domains/` across all domains
5. **Scope isolation**: Ingest/Query/Lint default to the current domain

## Initialization (Init)

### Step 1 — Confirm Requirements

- Ask the user for the project path (default: current working directory)
- Ask for the project name (kebab-case, e.g., `my-brain`)
- Ask for the initial list of domains: each needs a name (kebab-case),
  display name (Chinese or English), and one-line description

### Step 2 — Scan Existing State

```bash
ls -la <path>                    # Check if directory exists
git rev-parse --is-inside-work-tree  # Check if inside a repo
```

- Empty directory → `fresh` mode (create everything)
- Partially existing → `merge` mode (create missing, skip existing content)

### Step 3 — Show Preview Table

| Category | Path | Action |
|----------|------|--------|
| New dir | `raw/articles/` etc. | create |
| New file | `AGENTS.md` | create from template |
| New file | `wiki/index.md` | create from template |
| Skip | `wiki/log.md` | skip if exists |
| New dir | `domains/<name>/` | create |
| New file | `domains/<name>/AGENTS.md` | create from template |

End with: *"Please confirm above changes. Reply 'confirm' to proceed,
'cancel' to abort, or modify domain names/paths."*

### Step 4 — Create Scaffolding

Create files from the templates in `references/`. Replace placeholders:
- `{{PROJECT_NAME}}` — project directory name
- `{{DATE}}` — today's date (YYYY-MM-DD)
- `{{DOMAIN_NAME}}` — kebab-case domain name
- `{{DOMAIN_DISPLAY_NAME}}` — human-readable domain name
- `{{DOMAIN_DESCRIPTION}}` — one-line domain description
- `{{DOMAIN_ROWS}}` — registry table rows (`| name | path | description |`)

Create directories first, then files. For each domain, create the full
domain scaffolding including AGENTS.md + raw/ + wiki/ + output/.

### Step 5 — Git Detection

If the project is in a git repo, ask if the user wants to commit the initial scaffold.
If not a git repo, offer to `git init` (don't auto-execute).

See [Git Workflow](#git-workflow) below for commit message conventions.

### Add a New Domain (add-domain)

Same flow as init but scoped:
1. Ask domain name, display name, description
2. Scan for existing (skip if already exists)
3. Show preview (single domain scaffold)
4. Confirm → create → update root `wiki/index.md` registry → append to `wiki/log.md`

## Operations Within a Domain

This skill delegates to **`llm-wiki`** for per-domain operations.
Within any domain directory, the standard llm-wiki operations apply:

### Ingest (per domain)

1. Read source material
2. Create/update source summary page
3. Extract entities (new or append to existing)
4. Extract concepts (new or merge with existing)
5. Update thread pages
6. Update `wiki/index.md`
7. Append to `wiki/log.md`

Cross-domain material goes to root `raw/work/` first, then routed to the
appropriate domain during ingest.

### Query (per domain)

1. Read domain `wiki/index.md`
2. Locate relevant pages
3. Read and synthesize
4. Cite sources with `[[wikilinks]]`
5. If the user confirms the answer is valuable, save to wiki

For cross-domain queries: check the root registry, then search domains.

### Lint (per domain or cross-domain)

1. Find orphan pages (no inbound wikilinks)
2. Find broken wikilinks (links to non-existent pages)
3. Check index completeness (every wiki file in index.md)
4. Validate frontmatter
5. Check stale content
6. Flag contradictions
7. Output Markdown report

## Git Workflow

### Commit Suggestions After Major Milestones

After init, a full book ingest, or a large batch of updates:

1. Check `git rev-parse --is-inside-work-tree`
2. If in a git repo, offer to commit with a suggested message
3. Default commit scope: `wiki/`, `AGENTS.md`, `domains/*/wiki/`
4. **Ask before staging** `raw/` (may be large) — suggest gitignore if >50MB

### Suggested Commit Format

```
ingest: <domain> <topic> — N concepts, M sources

- wiki/index.md, wiki/log.md updated
- raw: included / gitignored (local only)
```

### .gitignore

```gitignore
.config/
.tmp/
```

Config directory is gitignored by default (contains skill-specific config,
API keys, etc.).

## Template Files

This skill ships the following templates in `references/`:

| Template | Purpose |
|----------|---------|
| `root-AGENTS.md` | Root schema defining directory structure, domain registry, cross-domain protocol |
| `domain-AGENTS.md` | Per-domain schema (name, content types, scope rules) |
| `root-index.md` | Root index template with domain registry table |
| `domain-index.md` | Domain-level index template |
| `log-entry.md` | Standard log entry format |
| `gitignore-snippet.md` | .gitignore content for wiki projects |

## Pitfalls

- **One domain per instance**: Do not create overlapping domains for the same topic.
  If two domains would cover the same ground, consider merging them or establishing
  a clear boundary in the registry.
- **Registry accuracy**: The root `wiki/index.md` domain registry must be updated
  every time a domain is added. Stale registries cause blind spots.
- **Cross-domain wikilinks**: `[[domain-page]]` links are only valid within the
  same domain. Use the registry to navigate between domains.
- **Don't nest domains**: `domains/<name>/domains/` is not supported. Each domain
  is a leaf.
- **Root is for fragments**: The root `raw/` and `wiki/` are for cross-domain
  or uncategorized material. If something clearly belongs to a domain, put it there.
- **Init preview is mandatory**: Never create files without showing the preview
  table and getting user confirmation.
