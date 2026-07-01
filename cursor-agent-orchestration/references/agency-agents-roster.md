# Agency Agents — Expert Roster for Roundtable Invitations

Source: https://github.com/msitarzewski/agency-agents (MIT, 121K stars)
Hermes plugin: `agency-agents-router` (installed via `scripts/install.sh --tool hermes`)

## What It Is

233 AI specialists across 16 divisions, each with personality, workflow, and deliverable templates. Useful as a **role directory** — when planning a roundtable, search the roster for relevant specialists instead of hand-writing role definitions.

## Installation

```bash
git clone https://github.com/msitarzewski/agency-agents.git
cd agency-agents
./scripts/convert.sh --tool hermes
./scripts/install.sh --tool hermes
# Plugin installed to ~/.hermes/plugins/agency-agents-router
# 233 agents stored in data/agents.json
```

## Plugin Tools (require Hermes restart)

- `agency_agents_search` — find matching specialists by query/division
- `agency_agents_inspect` — inspect one specialist's metadata or full body
- `agency_agents_load` — compose specialist prompt for current task
- `agency_agents_delegate` — delegate via delegate_task

## Divisions Quick Reference

| Division | Count | Best for Roundtable |
|----------|-------|---------------------|
| product | 5 | PM, trend research, sprint prioritization |
| engineering | 34 | Architect, Dev, Multi-Agent, Security, SRE |
| design | 9 | UX, UI, Brand, Whimsy |
| marketing | 36 | Growth, SEO, Social, China platforms |
| paid-media | 7 | PPC, ad creative, tracking |
| sales | 9 | Outbound, deal strategy, pipeline |
| security | 10 | AppSec, Cloud Security, Threat Intel |
| specialized | 53 | Business strategy, MCP, culture, compliance |
| testing | 8 | QA, accessibility, reality check |
| support | 6 | Analytics, compliance, finance tracker |
| finance | 5 | FP&A, investment, tax |
| academic | 5 | Anthropology, psychology, history |
| game-dev | ? | Game-specific |
| gis | ? | Geospatial |
| spatial-computing | ? | AR/VR |
| project-management | ? | Sprint, scrum |

## Accessing Without Plugin Restart

If the Hermes session hasn't restarted and plugin tools aren't available:

```python
import json
data = json.load(open(os.path.expanduser('~/.hermes/plugins/agency-agents-router/data/agents.json')))
# Filter: agents with 'division' matching target
# Search: text in 'name', 'summary', 'role'
```

## Roundtable Use

When planning a roundtable, search by keywords relevant to the topic (e.g. "platform", "knowledge", "growth", "monetization", "multi-agent") to find specialists whose personality files can serve as role definitions. Their YAML frontmatter contains persona, rules, and example workflows that inform the role prompt you send to cursor-agent.
