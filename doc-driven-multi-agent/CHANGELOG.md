# Changelog

## 1.1.0 (2026-07-03)

- Team onboarding: interactive interview protocol for first-time users (7 phases)
- Config persistence: team structure saved to `~/.config/skills/doc-driven-multi-agent/team-config.yaml`, auto-loaded on subsequent sessions
- Per-project override: `.skills/team-config.local.yaml` in project root for project-specific config
- Stability detection: session End checklist prompts to save team config when roles stabilize
- New references: `team-config-schema.md`, `onboarding-interview.md`
- New template: `team-config.yaml` starter config
- SKILL.md: new "Team Onboarding & Configuration" section, updated triggers, updated adaptation guide

## 1.0.0 (2026-06-30)

- Initial release
- Protocol: document chain, handoff protocol (三要素), gates G0–G4, session protocol, boundary enforcement
- 5 role SOPs: PM, PO, Arch, Dev, Analyst
- Handoff chat templates for all role directions
- Document templates: spec, plan, comm entry, arch review, analyst review
- Related skills: cursor-agent-orchestration, opencode, hermes-agent
