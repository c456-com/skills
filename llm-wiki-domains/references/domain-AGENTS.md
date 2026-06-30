# {{DOMAIN_DISPLAY_NAME}} Knowledge Base

This directory is an independent knowledge base at `domains/{{DOMAIN_NAME}}/`.

## Domain Focus

{{DOMAIN_DESCRIPTION}}

## Content Types

| Type | Description | Location |
|------|-------------|----------|
| Articles | External articles, reports, news | `raw/articles/` |
| Books | Book chapter markdown | `raw/books/` |
| Papers | Academic papers | `raw/papers/` |
| Courses | Course notes, video transcripts | `raw/courses/` |
| Resources | Link collections, references | `raw/resources/` |
| Quotes | Quotes, snippets | `raw/quotes/` |
| Tools | Tool research material | `raw/tools/` |
| Work notes | Ideas, fragments, unprocessed | `raw/work/` |

## Domain Conventions

- Ingest / Query / Lint default **scope is this directory**
- Cross-domain material goes to root `raw/work/` first, then routed here
- Update `wiki/index.md` and `wiki/log.md` on every change
- When adding new material, sync the domain registry in root `wiki/index.md`

## Naming

- Page files: lowercase kebab-case
- Wikilinks: `[[page-name]]` without `.md` suffix
