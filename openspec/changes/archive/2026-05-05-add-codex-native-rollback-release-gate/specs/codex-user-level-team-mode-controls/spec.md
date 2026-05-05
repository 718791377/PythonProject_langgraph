## ADDED Requirements

### Requirement: Release gates SHALL prove native Codex preservation and rollback evidence before production marking

Before a user-level team-mode installer, launcher, or publication slice is marked production-ready, the repository SHALL provide a release gate that requires evidence for native Codex preservation, backup snapshots, rollback behavior, and config rewrite sentinel status.

The release gate SHALL remain read-only by default and SHALL NOT install into the real user Codex home unless a separate reviewed change and explicit operator consent allow it.

The release gate SHALL protect these native Codex entrypoint names:

- `codex` - native Codex base command name.
- `codex.cmd` - Windows npm shim name for native Codex.
- `codex.ps1` - PowerShell shim name that must not be replaced by this repository.

#### Scenario: A release candidate lacks rollback evidence

- **WHEN** a release candidate changes user-level team-mode installer or launcher behavior
- **AND** no release-gate evidence records backup snapshot and rollback validation
- **THEN** the release SHALL NOT be marked production-ready
- **AND** the operator SHALL keep using the stable native Codex or raw bypass entrypoints

#### Scenario: A release gate is checked in CI

- **WHEN** the aggregate OpenSpec guard runs in CI or local verification
- **THEN** it SHALL validate the release-gate template and static repository evidence
- **AND** it SHALL NOT mutate `C:\Users\lenovo\.codex\config.toml` or any real user-level Codex asset

### Requirement: Release gates SHALL keep manual rollback evidence explicit

The release gate SHALL include a manual rollback path field that points to backup snapshot evidence or documented restore steps.

It SHALL distinguish automatic rollback-on-error evidence from manual version rollback evidence.

#### Scenario: Backup snapshots exist but manual rollback is undocumented

- **WHEN** backup snapshot behavior exists in the installer
- **AND** the release gate lacks a manual rollback path or restore evidence
- **THEN** the release SHALL remain blocked from production marking
- **AND** the gap SHALL be recorded as a release hardening task rather than silently accepted
