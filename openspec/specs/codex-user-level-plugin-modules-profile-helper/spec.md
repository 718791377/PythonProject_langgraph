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

The plugin modules skill SHALL include a JSON registry defining the initial module families `core-dev`, `web-saas`, `company-ops`, `market-research`, `customer-comms`, `creative-content`, `pyside6-gui`, and `full`.

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

### Requirement: Scenario-based profile routing metadata

The plugin-modules profile registry SHALL preserve existing top-level canonical profile IDs while allowing each non-`full` profile and each scenario profile to declare scenario routing metadata. The primary field name SHALL be `scene_description`; `scenario_description` MAY be retained as a compatibility alias for existing consumers.

#### Scenario: Non-full profile declares routing fields

- **GIVEN** a non-`full` top-level profile exists in `profiles.json`
- **WHEN** the profile routing checker validates the registry
- **THEN** the profile has `scene_description`, the compatibility alias `scenario_description`, positive routing terms or examples, negative examples, ranking signal notes, and at least one task module unless explicitly marked repo-local-only with a justified exception.

### Requirement: Task modules provide layered routing

The profile registry SHALL support task modules below top-level profiles so current-session soft-load can target a focused capability block.

#### Scenario: Task module can be soft-loaded

- **GIVEN** a registry entry defines `web-saas.mobile-app`
- **WHEN** `load_module.ps1 web-saas.mobile-app -Json` is executed
- **THEN** the output contains only the task module's focused plugin hints, skill document hints, load policy, and routing explanation.

### Requirement: Hard-load remains top-level only

The hard-load profile helper SHALL fail closed when a nested task module is provided as a hard-load target.

#### Scenario: Nested module hard-load is rejected

- **GIVEN** `web-saas.mobile-app` is a task module
- **WHEN** `set_plugin_profile.ps1 web-saas.mobile-app -Json` is executed
- **THEN** the command reports that task modules are soft-load guidance only and hard-load applies only to top-level profiles.

### Requirement: Profile suggestion is advisory and explainable

`skills2cli.py` SHALL provide an advisory profile suggestion command that explains profile matches, task module matches, excluded candidates, and soft/hard-load boundaries without mutating configuration.

#### Scenario: Ordinary task does not select full

- **GIVEN** the query is `Expo mobile build and Sentry observability`
- **WHEN** `skills2cli.py profile suggest --query ... --json` is executed
- **THEN** the top recommendation is not `full`, includes `web-saas`, includes profile-level `plugin_hints` and `skill_doc_hints`, includes `mobile-app` and `observability` task modules, and reports `mutates_config=false`.

### Requirement: Known plugins are not reachable only through full

The registry checker SHALL fail when a known plugin is reachable only through `full` without an explicit allowlist reason.

#### Scenario: Former only-full plugins have task routes

- **GIVEN** the known plugin list includes BioRender, ChatGPT Apps, Cloudinary, Expo, Fireflies, Linear, and Temporal
- **WHEN** the profile routing checker validates the registry
- **THEN** each plugin has a non-`full` top-level profile or task-module route, unless an explicit allowlist reason says it is troubleshooting-only.

### Requirement: Shared profile-routing contract remains centralized and bounded

The Python runtime and checker surfaces SHALL share stable registry paths, canonical profile IDs, required routing-field names, profile/task hint accessors, plugin-coverage collection, and explicit `full` troubleshooting trigger aliases through one shared contract module. That contract module SHALL NOT own scoring behavior, runtime ranking weights, or the checker black-box smoke matrix.

#### Scenario: Contract module does not couple scoring to checker smoke

- **GIVEN** the shared contract module is imported by `skills2cli.py`, `check_skills2cli_profile_routing.py`, and `check_plugin_modules_skill.py`
- **WHEN** profile suggestion scoring or checker smoke cases are changed
- **THEN** stable schema/path/accessor constants may be reused, but runtime scoring and checker expected examples remain separately reviewable.

### Requirement: Profile suggestion matrix covers ordinary profiles and explicit full troubleshooting

The profile routing checker SHALL run a black-box `skills2cli.py profile suggest` matrix that covers every ordinary profile family and explicit all-plugin troubleshooting requests. Matrix rows SHALL preserve preview-only safety flags and ordinary rows SHALL NOT select `full` as top recommendation.

#### Scenario: Matrix distinguishes ordinary routing from explicit full

- **GIVEN** the matrix includes ordinary tasks for repository development, browser verification, web/SaaS, customer communications, company operations, market research, creative content, and PySide6 GUI work
- **WHEN** the checker runs the profile suggestion matrix
- **THEN** ordinary rows select non-`full` target profiles, explicit English or Chinese all-plugin troubleshooting rows may select `full`, and every row reports `mutates_config=false`, `edits_plugin_cache=false`, `profile_apply_performed=false`, and `approval_required_for_apply=true`.


### Requirement: Checker JSON output is UTF-8 stable

Profile-routing checkers that emit JSON SHALL write UTF-8 bytes directly so Chinese queries and evidence text are machine-readable on Windows terminals without relying on the process default console encoding.

#### Scenario: Chinese full troubleshooting matrix row is JSON-decodable

- **GIVEN** the profile suggestion matrix includes the Chinese query `??????`
- **WHEN** `check_skills2cli_profile_routing.py --json` is executed on Windows
- **THEN** the JSON stream is UTF-8 decodable by downstream tests and includes the Chinese matrix row without mojibake or replacement characters.

### Requirement: Scenario profiles resolve to canonical target profiles

Scenario profiles SHALL be advisory recommendation entries that resolve to an existing canonical `target_profile`; they SHALL NOT replace audit candidate or hard-load target semantics.

#### Scenario: Scenario suggestion preserves target profile semantics

- **GIVEN** a scenario profile recommends security review for repository work
- **WHEN** `skills2cli.py profile suggest --query ... --json` is executed
- **THEN** the output includes both a scenario identifier and `target_profile=core-dev`, and reports that profile apply was not performed.
