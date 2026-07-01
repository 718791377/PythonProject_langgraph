# Delta Spec: Harden Skills2CLI Profile Routing Contract

## MODIFIED Requirements

### Requirement: Scenario-based profile routing metadata

The plugin-modules profile registry SHALL preserve existing top-level canonical profile IDs while allowing each non-`full` profile, each scenario profile, and each task module to declare scenario routing metadata. The primary field name SHALL be `scene_description`; `scenario_description` MAY be retained as a compatibility alias for existing consumers.

Each routable entry SHALL fail closed unless it has at least one non-empty positive scenario source: `scene_description` plus either `route_when` or `positive_examples`. Negative examples are mandatory for ordinary routing entries and SHALL be used as exclusion or penalty evidence during suggestion.

#### Scenario: Non-full profile declares routing fields

- **GIVEN** a non-`full` top-level profile exists in `profiles.json`
- **WHEN** the profile routing checker validates the registry
- **THEN** the profile has `scene_description`, the compatibility alias `scenario_description`, positive routing terms or examples, negative examples, ranking signal notes, and at least one task module unless explicitly marked repo-local-only with a justified exception.

#### Scenario: Positive scenario quality fails closed

- **GIVEN** a top-level profile, scenario profile, or task module has no non-empty `scene_description` and no `route_when` or `positive_examples`
- **WHEN** `check_skills2cli_profile_routing.py --json` validates the registry
- **THEN** the checker fails and reports the qualified entry name and the missing positive scenario evidence.

### Requirement: Task modules provide layered routing

The profile registry SHALL support task modules below top-level profiles so current-session soft-load can target a focused capability block. A task module's canonical logical identifier SHALL be `qualified_name=<profile>.<task_module>`. The local task-module name SHALL be valid only within its owning top-level profile.

Task modules SHALL be soft-load guidance only. They SHALL NOT define independent hard-load behavior, SHALL NOT be accepted as hard-load targets, and SHALL inherit parent hints only when an explicit inheritance marker is present.

#### Scenario: Task module can be soft-loaded

- **GIVEN** a registry entry defines `web-saas.mobile-app`
- **WHEN** `load_module.ps1 web-saas.mobile-app -Json` is executed
- **THEN** the output contains the task module's focused plugin hints, skill document hints, load policy, routing explanation, `entry_kind=task_module`, `target_profile=web-saas`, and `task_module=mobile-app`.

#### Scenario: Task module identity is first class

- **GIVEN** two top-level profiles both define a local task module named `browser-verification`
- **WHEN** the registry contract collects task-module routes
- **THEN** each module is reported by its unique `qualified_name` and no route is keyed only by the local task-module name.

### Requirement: Hard-load remains top-level only

The hard-load profile helper SHALL fail closed when a nested task module or scenario profile is provided as a hard-load target.

#### Scenario: Nested module hard-load is rejected

- **GIVEN** `web-saas.mobile-app` is a task module
- **WHEN** `set_plugin_profile.ps1 web-saas.mobile-app -Json` is executed
- **THEN** the command reports that task modules are soft-load guidance only and hard-load applies only to top-level profiles.

#### Scenario: Scenario profile hard-load is rejected

- **GIVEN** `repo-dev` is a scenario alias that resolves to `core-dev`
- **WHEN** `set_plugin_profile.ps1 repo-dev -Json` is executed
- **THEN** the command fails closed and reports the canonical preview command for `core-dev` instead of applying or previewing a scenario alias as an independent profile.

### Requirement: Profile suggestion is advisory and explainable

`skills2cli.py` SHALL provide an advisory profile suggestion command that explains profile matches, task module matches, excluded candidates, and soft/hard-load boundaries without mutating configuration.

Suggestion output SHALL include behavior evidence flags showing `mutates_config=false`, `edits_plugin_cache=false`, `profile_apply_performed=false`, and `approval_required_for_apply=true`. These flags SHALL be backed by tests that snapshot relevant config/cache state before and after representative suggestion and soft-load commands.

#### Scenario: Ordinary task does not select full

- **GIVEN** the query is `Expo mobile build and Sentry observability`
- **WHEN** `skills2cli.py profile suggest --query ... --json` is executed
- **THEN** the top recommendation is not `full`, includes `web-saas`, includes profile-level `plugin_hints` and `skill_doc_hints`, includes `mobile-app` and `observability` task modules, and reports `mutates_config=false`.

#### Scenario: Suggestion and soft-load do not apply profiles

- **GIVEN** a test fixture contains a user-level `config.toml` and plugin cache marker files
- **WHEN** `skills2cli.py profile suggest --query ... --json` and `load_module.ps1 core-dev.security-review -Json` run against the fixture
- **THEN** the fixture hashes are unchanged and the outputs report that no profile apply, config edit, or plugin-cache edit occurred.

### Requirement: Known plugins are not reachable only through full

The registry checker SHALL fail when a known plugin is reachable only through `full` without an explicit allowlist reason.

#### Scenario: Former only-full plugins have task routes

- **GIVEN** the known plugin list includes BioRender, ChatGPT Apps, Cloudinary, Expo, Fireflies, Linear, and Temporal
- **WHEN** the profile routing checker validates the registry
- **THEN** each plugin has a non-`full` top-level profile or task-module route, unless an explicit allowlist reason says it is troubleshooting-only.

### Requirement: Shared profile-routing contract remains centralized and bounded

The Python runtime and checker surfaces SHALL share stable registry paths, canonical profile IDs, required routing-field names, profile/task hint accessors, plugin-coverage collection, and explicit `full` troubleshooting trigger aliases through one shared contract module. That contract module SHALL NOT own scoring behavior, runtime ranking weights, or the checker black-box smoke matrix.

The shared contract SHALL define orthogonal fields for `routing_scope`, `activation_scope`, `governance_scope`, and `evidence_scope`. Compatibility `load_policy` values SHALL map consistently to these orthogonal fields.

#### Scenario: Contract module does not couple scoring to checker smoke

- **GIVEN** the shared contract module is imported by `skills2cli.py`, `check_skills2cli_profile_routing.py`, and `check_plugin_modules_skill.py`
- **WHEN** profile suggestion scoring or checker smoke cases are changed
- **THEN** stable schema/path/accessor constants may be reused, but runtime scoring and checker expected examples remain separately reviewable.

#### Scenario: Orthogonal routing fields are present

- **GIVEN** a profile or task module declares compatibility `load_policy`
- **WHEN** the registry checker validates the entry
- **THEN** the entry also declares `routing_scope`, `activation_scope`, `governance_scope`, and `evidence_scope`, and the checker verifies the compatibility mapping.

#### Scenario: Installed skills2cli carries the shared contract module

- **GIVEN** the user-level `skills2cli` facade is installed or simulated under `CODEX_HOME/tools/skills2cli`
- **WHEN** the generated `skills2cli` wrapper runs `profile suggest --query ... --json`
- **THEN** the installed helper directory contains `skills2cli_profile_registry_contract.py`, install metadata lists it as a support file, and install checks report the support file presence so the smoke fails closed if it is missing.

### Requirement: Profile suggestion matrix covers ordinary profiles and explicit full troubleshooting

The profile routing checker SHALL run a black-box `skills2cli.py profile suggest` matrix that covers every ordinary profile family and explicit all-plugin troubleshooting requests. Matrix rows SHALL preserve preview-only safety flags and ordinary rows SHALL NOT select `full` as top recommendation.

`full` and the `troubleshooting` scenario SHALL be explicit-only. When `explicit_full_request=false`, `full` SHALL be absent from selected recommendations and SHALL appear only in `excluded_candidates` with an eligibility reason. When `explicit_full_request=true`, selecting `full` SHALL include `why_full_selected` with one of `explicit_all_plugins`, `explicit_broad_discovery`, or `explicit_missing_plugin_capability`.

#### Scenario: Matrix distinguishes ordinary routing from explicit full

- **GIVEN** the matrix includes ordinary tasks for repository development, browser verification, web/SaaS, customer communications, company operations, market research, creative content, and PySide6 GUI work
- **WHEN** the checker runs the profile suggestion matrix
- **THEN** ordinary rows select non-`full` target profiles, explicit English or Chinese all-plugin troubleshooting rows may select `full`, and every row reports `mutates_config=false`, `edits_plugin_cache=false`, `profile_apply_performed=false`, and `approval_required_for_apply=true`.

#### Scenario: Full is excluded unless explicitly requested

- **GIVEN** a query has broad wording but does not explicitly ask for all plugins, full profile, or missing-plugin troubleshooting
- **WHEN** `skills2cli.py profile suggest --query ... --json` runs
- **THEN** `full` is not selected, `explicit_full_request=false`, and `excluded_candidates` includes `full` with an explicit-only eligibility reason.

## ADDED Requirements

### Requirement: Recall/rerank is explainable and fail-closed

Profile suggestion SHALL separate recall from rerank. Recall MAY collect candidate top-level profiles, scenario profiles, and task modules from scenario fields, query terms, repository/task context, and audit strong evidence. Rerank MAY boost candidates with strong audit evidence and MAY penalize oversized or warning-pressure-heavy candidates, but it SHALL NOT override hard safety gates such as explicit-only `full` eligibility or profile apply approval.

#### Scenario: Rerank cannot bypass eligibility

- **GIVEN** audit evidence or broad plugin coverage would otherwise boost `full`
- **WHEN** `explicit_full_request=false`
- **THEN** rerank keeps `full` excluded, records the warning-pressure or eligibility reason, and selects the highest-ranked eligible non-`full` profile.

#### Scenario: Rerank evidence is visible

- **GIVEN** a candidate profile receives audit-evidence boost or warning-pressure penalty
- **WHEN** `skills2cli.py profile suggest --query ... --json` runs
- **THEN** the output includes sanitized evidence source labels, rank factors, excluded candidates when applicable, and no raw transcript or private path content.

## MODIFIED Requirements

### Requirement: Checker JSON output is UTF-8 stable

Profile-routing checkers that emit JSON SHALL write UTF-8 bytes directly so Chinese queries and evidence text are machine-readable on Windows terminals without relying on the process default console encoding.

#### Scenario: Chinese full troubleshooting matrix row is JSON-decodable

- **GIVEN** the profile suggestion matrix includes the Chinese query represented by codepoints `U+6392 U+969C U+6240 U+6709 U+63D2 U+4EF6`
- **WHEN** `check_skills2cli_profile_routing.py --json` is executed on Windows
- **THEN** the JSON stream is UTF-8 decodable by downstream tests and includes the Chinese matrix row without mojibake or replacement characters.

### Requirement: Scenario profiles resolve to canonical target profiles

Scenario profiles SHALL be advisory recommendation entries that resolve to an existing canonical `target_profile`; they SHALL NOT replace audit candidate or hard-load target semantics.

#### Scenario: Scenario suggestion preserves target profile semantics

- **GIVEN** a scenario profile recommends security review for repository work
- **WHEN** `skills2cli.py profile suggest --query ... --json` is executed
- **THEN** the output includes both a scenario identifier and `target_profile=core-dev`, and reports that profile apply was not performed.

## ADDED Requirements

### Requirement: Installed artifact drift reporting covers the full routing surface

The installed-copy checker SHALL report drift for every installed artifact needed by Skills2CLI profile routing, not only `profiles.json`. The report SHALL cover repository and installed copies of `skills2cli.py`, `skills2cli_profile_registry_contract.py`, and `profiles.json`.

#### Scenario: Installed artifact drift is visible

- **GIVEN** an installed user-level `skills2cli` helper is missing `skills2cli_profile_registry_contract.py` or has a different `profiles.json` hash from repo source
- **WHEN** `check_plugin_modules_skill.py --json` runs with installed-copy reporting enabled
- **THEN** the output names the drifting artifact, reports repo and installed paths, and does not treat the installed copy as the source of truth.
