## Overview

Implement Option C from `docs_bilingual/implementation_plans/plugin_modules_profile_helper_plan.md`: keep a small always-visible skill as the entrypoint and move detailed plugin/module knowledge into `references/profiles.json` plus deterministic PowerShell helpers.

## Design decisions

### Repository source, user-level install target

The source skill lives under `tools/skill_sources/plugin-modules/` because `.codex/skills` is reserved for repository-discovered OpenSpec skills and may be ACL-protected in wrapped sessions. The installer copies the source into the user-level Codex skills root:

```text
C:\Users\lenovo\.codex\skills\plugin-modules
```

This keeps the repository as source of truth while still making the skill available cross-project after installation and restart.

### Soft-load mode

`scripts/load_module.ps1` reads the module registry, resolves only the selected module's `SKILL.md` path hints under `CODEX_HOME` or `~/.codex`, and emits a small set of files to read. It never edits `config.toml`, plugin cache files, wrappers, or MCP settings.

### Hard-load mode

`scripts/set_plugin_profile.ps1` previews by default. With `-Apply`, it:

1. Builds the selected module's plugin enable/disable map.
2. Backs up `config.toml` under `backups\plugin-modules-profile`.
3. Rewrites only `enabled = true/false` keys inside `[plugins."..."]` TOML sections, adding missing plugin sections when needed.
4. Prints restart/resume instructions because startup-visible skills and plugin tools are determined at process start.

`-RestoreLatest -Apply` restores the latest backup.

### Module registry

The initial modules mirror the approved plan:

- `core-dev` - daily developer work, review, security, browser verification, and artifacts.
- `web-saas` - frontend, SaaS, deployment, payments, database, and observability work.
- `company-ops` - one-person-company mail, calendar, drive, Slack, Notion, CRM, and office operations.
- `market-research` - market, company, investment, news, library, and model/dataset research.
- `customer-comms` - Twilio, SendGrid, Slack, Gmail, Stripe-adjacent customer messaging.
- `creative-content` - Canva, Figma, Remotion, HyperFrames, presentations, and documents.
- `full` - temporary troubleshooting profile that enables every known plugin family.

The `full` profile is troubleshooting-only and can re-enable every known plugin family.

## Safety properties

- No repository checker mutates user-level files.
- The installer mutates only the user-level `skills\plugin-modules` destination and backs up an existing skill before replacement.
- Hard-load config writes require `-Apply`; preview is the default.
- Hard-load edits do not touch `[mcp_servers]`, oh-my-codex state, plugin cache files, or wrapper scripts.
- Rollback uses either the skill installer backup or the profile backup.

## Alternatives considered

- Disable plugin bundles directly: rejected because it would be too blunt and could break future one-person-company workflows.
- Bulk-shorten plugin SKILL.md files: rejected because plugin cache is vendor-managed and updates can overwrite changes.
- Create many always-on module skills: rejected because it recreates skills-budget pressure.
