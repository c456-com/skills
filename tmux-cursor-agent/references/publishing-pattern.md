# Skill Publishing Pattern (c456-com/skills)

Standard workflow for adding/modifying a skill in the c456-com/skills monorepo.

## Adding a New Skill

1. Create skill directory with `SKILL.md` + `references/` + applicable scripts/templates
2. Register in `registry.json` — add entry with name, description, tags, version
3. Add to `README.md` — add row to the skill table
4. Update downstream dependencies — any file referencing the old name
5. Push: `git add -A && git commit -m "feat: add <skill>" && git push`

## Renaming/Removing

1. Create new skill directory
2. Update `registry.json` (add new entry, remove old)
3. Update `README.md` skill table
4. **grep every .md and .json in the repo** for old name — update docs, commands, constants
5. Delete old skill directory
6. Push to GitHub
7. For downstream projects (like c456-cli), update source code and rebuild (`npm run build`)
