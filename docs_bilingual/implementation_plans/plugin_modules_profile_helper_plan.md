# Plugin Modules Profile Helper Plan

Status: design note, requested by operator on 2026-05-10.

Goal: avoid keeping every plugin skill permanently visible in the 2% skills context budget while still supporting long-term use cases such as:

1. Codex CLI personal production-grade persistent developer team.
2. Personal one-person-company production operations.

Recommended approach: Option C - unified skill plus profile helper with soft/hard loading modes.

## Key constraints

- The model-visible skills list is computed at Codex startup and is effectively fixed for the current Codex process.
- A current session can soft-load module knowledge by reading selected SKILL.md or reference files on demand.
- A current session cannot reliably add omitted skills back into the automatic model-visible skills list without restarting or resuming under a different startup profile.
- Plugin/MCP tools that were not started at launch generally require a profile switch plus restart/resume.

## Proposed user-level skill

Skill name: plugin-modules

Location: C:\Users\lenovo\.codex\skills\plugin-modules\

Shape:

```text
plugin-modules/
  SKILL.md
  references/
    profiles.json
  scripts/
    list_module.ps1
    load_module.ps1
    set_plugin_profile.ps1
```

## Modes

### soft-load

Use inside the current session.

Behavior:

- Read a module definition from `references/profiles.json`.
- Load only the relevant skill docs/references for the current task.
- Do not edit `C:\Users\lenovo\.codex\config.toml`.
- Do not require restart.
- Best for planning, code generation, local docs, workflow guidance, and API usage order when direct plugin tools are not needed.

Example intents:

- `$plugin-modules load market-research` - soft-load market research plugin guidance for the current session.
- `$plugin-modules load company-ops` - soft-load company operations plugin guidance for the current session.

### hard-load

Use when actual plugin skills/tools must be present in startup-visible context or when MCP/app plugin tools are needed.

Behavior:

- Backup `C:\Users\lenovo\.codex\config.toml`.
- Toggle `[plugins."..."] enabled = true/false` according to the selected profile.
- Preserve critical MCP and orchestration settings.
- Print exact restart/resume instructions.
- Require a new `codex-ohmy` launch or `/resume` into the target thread.

Example intents:

- `$plugin-modules hard-load customer-comms` - switch the next startup profile to customer communication plugins.
- `$plugin-modules profile core-dev -Apply` - apply the core developer plugin profile after backing up config.
- `$plugin-modules restore` - restore the previous plugin profile from backup metadata.

## Initial module families

- core-dev: GitHub, CodeRabbit, Codex Security, OpenAI Developers, Browser/Chrome, Documents, Spreadsheets, Presentations.
- web-saas: Vercel, Cloudflare, Supabase, Sentry, Stripe, Figma, Browser, GitHub.
- company-ops: Gmail, Google Calendar, Google Drive, Slack, Notion, HubSpot, Documents, Spreadsheets.
- market-research: PitchBook, CB Insights, Dow Jones Factiva, Readwise, Zotero, Hugging Face.
- customer-comms: Twilio Developer Kit, Stripe, Slack, Gmail, relevant SendGrid/Twilio skills.
- creative-content: Canva, Figma, Remotion, HyperFrames, Presentations, Documents.
- full: restore all installed plugins.

## Safety rules

- Do not delete plugin cache.
- Do not bulk-edit plugin SKILL.md files to save budget.
- Treat disabled plugins as dormant, not removed.
- Keep `config.toml` backup-before-write mandatory.
- Keep direct Codex MCP entries and oh-my-codex orchestration settings outside profile toggles unless explicitly requested.

## Implementation note

This note only preserves the design. A future implementation should create the skill and scripts after a small reviewed change or explicit user-level operation request.
