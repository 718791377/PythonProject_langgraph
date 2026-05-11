# codex-user-level-plugin-modules-profile-helper Specification

## Purpose
Define the user-level `plugin-modules` skill and profile helper contract for task-scoped plugin soft-loading, backup-protected hard-load profile switching, and explicit installation into the Codex user skills directory.
## Requirements
### Requirement: Plugin modules skill SHALL provide a unified module entrypoint

The repository SHALL provide a `plugin-modules` skill source that can be installed into the user-level Codex skills directory.

The skill SHALL expose a concise metadata description and SHALL route the operator to module listing, soft-load, and hard-load helper scripts.

#### Scenario: Skill source is validated

- **WHEN** the plugin modules skill checker runs
- **THEN** it SHALL verify `SKILL.md`, `references/profiles.json`, `scripts/list_module.ps1`, `scripts/load_module.ps1`, and `scripts/set_plugin_profile.ps1`
- **AND** it SHALL verify the skill description remains within the repository skill description limit

#### Scenario: User-level install is requested

- **WHEN** the installer is run for the plugin modules skill
- **THEN** it SHALL copy the repository-source skill to the user-level Codex skills directory
- **AND** if an existing installed skill is present, the installer SHALL require explicit replacement and create a backup before replacing it
- **AND** the installer SHALL tell the operator that a restart or resume in a fresh `codex-ohmy` process is required

### Requirement: Plugin modules registry SHALL define task-scoped module families

The plugin modules skill SHALL include a JSON registry defining the initial module families `core-dev`, `web-saas`, `company-ops`, `market-research`, `customer-comms`, `creative-content`, and `full`.

Each module SHALL define a description, plugin family list, soft-load skill document hints, and hard-load plugin enablement behavior.

#### Scenario: Module list is requested

- **WHEN** `list_module.ps1` runs
- **THEN** it SHALL list the available module names, descriptions, plugin families, and soft-load hint counts

#### Scenario: Required module is missing

- **WHEN** the checker reads `profiles.json`
- **AND** one of the required initial module families is absent
- **THEN** the checker SHALL fail and name the missing module

### Requirement: Soft-load mode SHALL be non-mutating and current-session safe

Soft-load mode SHALL read only the selected module definition and resolve relevant local `SKILL.md` references.

Soft-load mode SHALL NOT edit `config.toml`, plugin cache files, user-level wrappers, direct Codex MCP entries, or oh-my-codex durable state.

#### Scenario: Current session soft-loads a module

- **WHEN** `load_module.ps1 <module> -Json` runs
- **THEN** it SHALL emit the selected module, plugin families, usage notes, and resolved `skill_docs`
- **AND** it SHALL explain that omitted skills cannot be added back to the startup-visible skills list without restart
- **AND** it SHALL not write to user-level configuration

### Requirement: Hard-load mode SHALL be preview-first and backup-protected

Hard-load mode SHALL preview profile changes by default and SHALL write user-level `config.toml` only when `-Apply` is supplied.

Before any `config.toml` write, hard-load mode SHALL create a backup under the user-level Codex backup directory.

Hard-load mode SHALL edit only `[plugins."..."] enabled` values and SHALL preserve direct MCP and oh-my-codex settings.

#### Scenario: Hard-load profile is previewed

- **WHEN** `set_plugin_profile.ps1 <module> -Json` runs without `-Apply`
- **THEN** it SHALL emit the target plugin enabled states
- **AND** it SHALL not write `config.toml`

#### Scenario: Hard-load profile is applied

- **WHEN** `set_plugin_profile.ps1 <module> -Apply` runs
- **THEN** it SHALL back up `config.toml`
- **AND** it SHALL update only plugin `enabled` settings for the selected module profile
- **AND** it SHALL print restart/resume instructions

#### Scenario: Latest profile backup is restored

- **WHEN** `set_plugin_profile.ps1 -RestoreLatest -Apply` runs
- **THEN** it SHALL restore the latest plugin-modules profile backup to `config.toml`
- **AND** it SHALL print restart/resume instructions
