# {{PROJECT_NAME}} Wiki Schema (Meta-Wiki Root)

## 1. Directory Structure

This repository uses a **two-layer architecture**: the root is the global index,
each `domains/` subdirectory is a fully independent llm-wiki instance.

```
{{PROJECT_NAME}}/
├── AGENTS.md                       ← This file (root schema)
├── raw/                            ← Cross-domain source material (read-only for AI)
│   ├── articles/  books/  papers/  courses/
│   ├── resources/  quotes/  tools/  work/
├── wiki/                           ← Global knowledge layer (AI-generated)
│   ├── index.md                    ← Global index + domain registry
│   ├── log.md                      ← Global action log
│   ├── entities/  concepts/  threads/  sources/  agents/
├── shared/wiki/                    ← Cross-domain compilations (optional)
│   ├── index.md
│   └── log.md
├── domains/                        ← Domain knowledge containers
│   └── <domain-name>/              ← Each is a self-contained llm-wiki
│       ├── AGENTS.md
│       ├── raw/  wiki/  output/
├── output/                         ← Global output artifacts (optional)
└── .tmp/                           ← Temporary files
```

### 1.1 Layer Responsibilities

| Layer | What it holds | Search scope |
|-------|--------------|--------------|
| **Root** | Cross-domain fragments, tool research, global index | Root-level grep |
| **domains/<name>/** | Self-contained 3-layer wiki, independently shareable | Domain-local |
| **shared/wiki/** | Cross-domain thread compilations | Global navigation |

### 1.2 Retrieval Protocol

1. **Global**: Read `wiki/index.md` (and optional `shared/wiki/index.md`)
2. **Locate**: Find the relevant domain path from the registry table
3. **Domain**: Read that domain's `wiki/index.md`; default scope for ingest/query/lint
4. **Cross-domain**: `rg -l "keyword" domains/` or root-level grep

## 2. Page Types

### Entity Pages `wiki/entities/`
- Naming: lowercase kebab-case
- Frontmatter: `type: entity` + `tags: [...]`

### Concept Pages `wiki/concepts/`
- Naming: lowercase kebab-case

### Thread Pages `wiki/threads/`
- Naming: lowercase kebab-case

### Source Summary Pages `wiki/sources/`
- Naming: matches raw filename
- Frontmatter: `type: source` + `date: YYYY-MM-DD` + `raw: raw/.../xxx.md`

## 3. Linking

- Obsidian Wikilinks: `[[page-name]]`
- No `.md` extension in links
- Page titles use `# Title` (H1)

## 4. Operations

### Ingest
1. Read source → 2. Create/update source summary → 3. Extract entities →
4. Extract concepts → 5. Update threads → 6. Update `index.md` → 7. Append `log.md`

### Query
1. Read `index.md` → 2. Locate pages → 3. Read + synthesize → 4. Cite sources →
5. Save valuable answers to wiki

### Lint
1. Scan contradictions → 2. Find orphan pages → 3. Check missing pages →
4. Evaluate data gaps → 5. Output report

## 5. Special Files

### `wiki/index.md`
Content catalog. One line per page (wikilink + summary). Root index must include
a "Domain Registry" section listing all domains.

### `wiki/log.md`
Append-only chronological log. Format: `## [YYYY-MM-DD] action | Title`
Actions: `ingest`, `query`, `lint`, `update`, `create`, `init`
