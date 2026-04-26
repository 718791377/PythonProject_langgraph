# codex-skills-profile-launcher-mapping Specification

## Purpose
Define the repository-governed, non-mutating Codex skills profile-to-launcher mapping contract and its validation behavior.
## Requirements
### Requirement: Profile launcher mapping SHALL be declarative and non-mutating

The Codex skills profile launcher mapping SHALL live in repository-local governance artifacts and SHALL NOT mutate user-level launcher wrappers, user-level `config.toml`, plugin cache files, or user-level skills.

#### Scenario: Mapping is reviewed
- **WHEN** the operator reviews the profile launcher mapping
- **THEN** the mapping SHALL identify itself as declarative metadata
- **AND** it SHALL state that installed launcher aliases are future-optional until a separate approved launcher installation change exists

#### Scenario: Mapping validation runs
- **WHEN** the launcher mapping validation command runs
- **THEN** it SHALL read repository-local registry and documentation files
- **AND** it SHALL NOT write to user-level configuration or installed launcher locations

### Requirement: Profile launcher mapping SHALL define required profile aliases

The profile launcher mapping SHALL define launcher-facing entries for at least `core`, `browser`, `web`, `github`, and `full`.

Each mapping entry SHALL include:

- profile name,
- intended alias,
- base command,
- lifecycle status,
- plugin policy,
- short purpose.

#### Scenario: Required profiles are present
- **WHEN** the mapping checker validates the registry
- **THEN** it SHALL pass only if `core`, `browser`, `web`, `github`, and `full` have launcher mapping entries
- **AND** each mapped profile SHALL also exist in the profile registry

#### Scenario: Future alias is documented
- **WHEN** a future optional alias such as `codex-ohmy-browser` is listed
- **THEN** the mapping SHALL identify the alias as not installed by this repository change
- **AND** it SHALL keep the base command compatible with the stable `codex-ohmy` entrypoint

### Requirement: Profile launcher mapping SHALL preserve browser and web capabilities

The profile launcher mapping SHALL preserve browser automation and web deployment capability by keeping browser and web profiles associated with the required plugin capabilities until fine-grained plugin-skill filtering exists.

#### Scenario: Browser profile is validated
- **WHEN** the mapping checker validates the `browser` profile mapping
- **THEN** it SHALL require the mapping to preserve browser verification capabilities
- **AND** it SHALL reject mappings that disable the Vercel plugin bundle while browser plugin capabilities are still required

#### Scenario: Web profile is validated
- **WHEN** the mapping checker validates the `web` profile mapping
- **THEN** it SHALL require the mapping to preserve Vercel, frontend, and deployment capability
- **AND** it SHALL keep plugin handling compatible with bundle-level loading until finer filtering exists

### Requirement: Default launcher mapping SHALL reduce default skill scope

The profile launcher mapping SHALL define the `core` launcher profile as the default reduced-scope profile for non-web work.

The `core` profile SHALL NOT require Vercel, Next.js, React, or broad plugin discovery skills. The `full` profile SHALL be marked temporary and troubleshooting-only.

#### Scenario: Core profile is validated
- **WHEN** the mapping checker validates the `core` profile mapping
- **THEN** it SHALL require a reduced-scope default designation
- **AND** it SHALL reject a `core` mapping that requires Vercel or broad plugin discovery

#### Scenario: Full profile is validated
- **WHEN** the mapping checker validates the `full` profile mapping
- **THEN** it SHALL require a temporary troubleshooting designation
- **AND** it SHALL reject `full` as a long-term default

### Requirement: Launcher mapping validation SHALL be automatable

The repository SHALL provide a validation command that emits JSON and can be used in MR checks.

The validation output SHALL include:

- schema version,
- check name,
- ok flag,
- errors,
- warnings,
- summary counts,
- mapping entries checked.

#### Scenario: Mapping is valid
- **WHEN** the mapping satisfies all required profile, alias, plugin, and non-mutation constraints
- **THEN** the validation command SHALL return exit code 0
- **AND** the JSON output SHALL contain `ok: true`

#### Scenario: Mapping is invalid
- **WHEN** a required mapping entry is missing or violates plugin/config safety rules
- **THEN** the validation command SHALL return non-zero
- **AND** the JSON output SHALL identify the failing rule
