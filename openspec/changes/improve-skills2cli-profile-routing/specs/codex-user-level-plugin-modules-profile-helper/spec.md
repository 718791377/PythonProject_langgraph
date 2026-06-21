# Delta Spec: Codex User-Level Plugin Modules Profile Helper

## ADDED Requirements

### Requirement: Scenario-based profile routing metadata

The plugin-modules profile registry SHALL preserve existing top-level canonical profile IDs while allowing each non-`full` profile and each scenario profile to declare scenario routing metadata.

#### Scenario: Non-full profile declares routing fields

- **GIVEN** a non-`full` top-level profile exists in `profiles.json`
- **WHEN** the profile routing checker validates the registry
- **THEN** the profile has a scenario description, positive routing terms or examples, negative examples, ranking signal notes, and at least one task module unless explicitly marked repo-local-only with a justified exception.

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
- **THEN** the top recommendation is not `full`, includes `web-saas`, includes `mobile-app` and `observability` task modules, and reports `mutates_config=false`.

### Requirement: Known plugins are not reachable only through full

The registry checker SHALL fail when a known plugin is reachable only through `full` without an explicit allowlist reason.

#### Scenario: Former only-full plugins have task routes

- **GIVEN** the known plugin list includes BioRender, ChatGPT Apps, Cloudinary, Expo, Fireflies, Linear, and Temporal
- **WHEN** the profile routing checker validates the registry
- **THEN** each plugin has a non-`full` top-level profile or task-module route, unless an explicit allowlist reason says it is troubleshooting-only.

### Requirement: Scenario profiles resolve to canonical target profiles

Scenario profiles SHALL be advisory recommendation entries that resolve to an existing canonical `target_profile`; they SHALL NOT replace audit candidate or hard-load target semantics.

#### Scenario: Scenario suggestion preserves target profile semantics

- **GIVEN** a scenario profile recommends security review for repository work
- **WHEN** `skills2cli.py profile suggest --query ... --json` is executed
- **THEN** the output includes both a scenario identifier and `target_profile=core-dev`, and reports that profile apply was not performed.
