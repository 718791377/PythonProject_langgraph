## ADDED Requirements

### Requirement: The repository SHALL provide a repeatable Windows native_omx bootstrap repair path

The repository SHALL provide a repeatable repair or verification path for the globally installed `oh-my-codex` runtime so Windows native_omx prompt-worker bootstrap no longer depends on `powershell.exe`.

#### Scenario: Operator reapplies the Windows bootstrap fix after an upgrade

- **WHEN** the globally installed `oh-my-codex` runtime has been upgraded or reinstalled
- **THEN** the repository SHALL provide a repeatable way to verify or reapply the Windows bootstrap fix
- **AND** that process SHALL remain auditable and reversible
