# codex-user-level-helper-mirror-source-truth Specification

## Purpose
Define user-level helper mirrors as generated install artifacts while keeping repository-local source and each consumer repository's `.omx/state/` durable-state tree authoritative.
## Requirements
### Requirement: Generated Helpers Identify Install Artifact Status
Generated user-level helper mirrors SHALL expose that they are install artifacts generated from repository source, not the primary implementation source.

#### Scenario: Durable status exposes install artifact metadata
- **WHEN** the generated `codex-durable-state-status.ps1` helper emits JSON output
- **THEN** the output SHALL include helper mirror metadata declaring the helper copy as a generated install artifact

### Requirement: Repository Source Remains Authoritative
Generated user-level helper mirrors SHALL identify repository-local source as the development authority for helper behavior.

#### Scenario: Durable status points back to repository source
- **WHEN** a cold-start session inspects durable-state status JSON
- **THEN** the helper mirror metadata SHALL identify `tools/install-codex-user-level-team-mode.ps1` as the repository source script for generated helper behavior

### Requirement: Consumer Project Durable Truth Remains Local
Generated user-level helper mirrors SHALL state that each consumer repository keeps durable truth under its own repo-local `.omx/state/` tree.

#### Scenario: Durable status preserves consumer isolation
- **WHEN** the durable-state status helper is invoked for a consumer project repository
- **THEN** the helper mirror metadata SHALL state that the target repository's own `.omx/state/` tree remains the durable truth and SHALL NOT describe `D:\PythonProject_langgraph` as a global durable-state root
