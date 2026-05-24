# codex-user-level-comet-controlled-openspec-superpowers Specification Delta

## ADDED Requirements

### Requirement: Comet runtime adoption SHALL be explicit, backed up, and reversible

When this repository moves from Comet governance into actual runtime installation or user-level Codex mutation, the adoption SHALL record explicit operator approval, backup paths, write scope, validation evidence, and rollback instructions before the change is treated as complete.

#### Scenario: Operator approves runtime adoption
- **WHEN** the operator asks to install `@rpamis/comet`, run `comet init`, or edit user-level Codex configuration
- **THEN** the workflow SHALL record that request in an OpenSpec change or equivalent durable evidence
- **AND** it SHALL define the allowed write scope before mutation

#### Scenario: User-level Codex configuration is edited
- **WHEN** `C:\Users\lenovo\.codex\config.toml` is changed for Comet adoption
- **THEN** a timestamped backup SHALL exist before the edit
- **AND** the evidence SHALL describe the exact intended config delta and rollback source

#### Scenario: Comet initialization writes skills or scripts
- **WHEN** `comet init` installs or updates Codex/OpenSpec/Superpowers/Comet skills
- **THEN** the workflow SHALL capture the generated or changed paths when available
- **AND** existing skills SHALL be skipped or backed up before overwrite

#### Scenario: Runtime adoption is verified
- **WHEN** installation and initialization complete
- **THEN** the workflow SHALL run Comet status or doctor checks when available
- **AND** repository OpenSpec validation SHALL still pass
