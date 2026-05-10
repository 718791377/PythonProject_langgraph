## MODIFIED Requirements

### Requirement: Profile launcher mapping SHALL be declarative and non-mutating

The Codex skills profile launcher mapping SHALL live in repository-local governance artifacts and SHALL NOT mutate user-level launcher wrappers, user-level `config.toml`, plugin cache files, or user-level skills.

A separate profile helper MAY apply plugin profile settings only through an explicit operator-run helper that backs up `config.toml`, edits only plugin `enabled` keys, and requires restart or resume for startup-visible plugin changes.

#### Scenario: Mapping is reviewed

- **WHEN** the operator reviews the profile launcher mapping
- **THEN** the mapping SHALL identify itself as declarative metadata
- **AND** it SHALL state that installed launcher aliases are future-optional until a separate approved launcher installation change exists

#### Scenario: Mapping validation runs

- **WHEN** the launcher mapping validation command runs
- **THEN** it SHALL read repository-local registry and documentation files
- **AND** it SHALL NOT write to user-level configuration or installed launcher locations

#### Scenario: Profile helper is used instead of launcher aliases

- **WHEN** a plugin module profile must be applied before physical launcher aliases exist
- **THEN** the helper SHALL preserve the declarative launcher mapping boundary
- **AND** it SHALL not install or mutate launcher aliases
