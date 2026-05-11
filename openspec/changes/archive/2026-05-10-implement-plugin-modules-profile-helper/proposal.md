## Why

The enabled plugin catalog can exceed the Codex skills context budget, causing descriptions to be removed or plugin skills to be omitted from the startup-visible list. The operator approved the Option C design: a unified `plugin-modules` skill plus profile helper that supports task-scoped soft-loading now and startup profile switching when live plugin capabilities are needed.

## What Changes

- Add a repository-source `plugin-modules` skill with concise trigger metadata, module registry, and three helper scripts.
- Add soft-load support that prints only the module-specific plugin skill docs a current session should read.
- Add hard-load support that previews or applies `[plugins."..."] enabled` settings in user-level `config.toml`, with mandatory backup before write and restart instructions.
- Add a user-level installer for copying the repository-source skill into `C:\Users\lenovo\.codex\skills\plugin-modules`.
- Add a script-backed checker and tests so the helper remains safe, profile-backed, and non-mutating unless `-Apply` is used.
- No breaking changes.

## Capabilities

### New Capabilities

- `codex-user-level-plugin-modules-profile-helper`: Defines the unified plugin module skill, soft-load behavior, hard-load config profile behavior, installer, and validation contract.

### Modified Capabilities

- `codex-user-level-skills-governance-lifecycle`: The lifecycle gains an accepted implementation path for the previously deferred launcher/profile integration phase via an explicit skill/profile helper.
- `codex-skills-profile-launcher-mapping`: The declarative launcher mapping is complemented by an explicit helper that can apply plugin profiles without installing new launcher aliases.

## Impact

- Adds source files under `tools/skill_sources/plugin-modules/`.
- Adds `tools/install-plugin-modules-skill.ps1` and `tools/check_plugin_modules_skill.py`.
- Updates local guard/test surfaces so the new helper is validated.
- Writes to user-level `C:\Users\lenovo\.codex\skills\plugin-modules` only when the installer is explicitly run; repository validation does not mutate user-level config, plugin cache, or installed wrappers.
- Hard-load profile application edits only `[plugins."..."] enabled` keys in `config.toml` and backs up the file first.

## Governance fields

- `impact_scope`: user-level skill source, explicit installer, profile-helper scripts, validation checks, and OpenSpec specs.
- `explicit_non_goals`: no plugin cache edits; no bulk plugin SKILL.md rewrites; no launcher alias installation; no direct Codex MCP entry changes; no automatic `config.toml` mutation during repository validation.
- `rollout_sequence`: commit repository source and tests; validate locally; install user-level skill with explicit operator-approved script run; restart/resume with `codex-ohmy` when the operator wants the skill visible.
- `rollback_plan`: remove or restore `C:\Users\lenovo\.codex\skills\plugin-modules` from the installer backup; restore `config.toml` from `backups\plugin-modules-profile`; revert the repository commit if needed.
- `validation_path`: `tools/check_plugin_modules_skill.py`, the new unit test, skill quick validation, helper script smoke tests, OpenSpec validation, and local CI gate.
- `mainline_classification`: existing skills-governance/profile integration follow-up under the Codex user-level orchestration mainline.
