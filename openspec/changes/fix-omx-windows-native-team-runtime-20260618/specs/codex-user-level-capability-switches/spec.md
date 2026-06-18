## ADDED Requirements

### Requirement: Capability readiness SHALL NOT be treated as operational launchability

Capability readiness records SHALL distinguish installed, enabled, selected, ready, and operational readiness.

#### Scenario: Native OMX is selected but runtime evidence is missing

- **GIVEN** `native_omx` is installed, enabled, and selected
- **AND** no launchable Windows runtime backend or explicit Unix/tmux runtime evidence is present
- **WHEN** readiness is projected
- **THEN** the projection SHALL NOT claim operational launchability
- **AND** it SHALL expose blockers such as `blocked:runtime_backend_unavailable`, `blocked:tmux_only_backend`, or `blocked:not_in_tmux_session`.

### Requirement: Readiness projection SHALL keep non-launch smoke evidence explicit

Readiness projection receipts SHALL identify whether a backend was only inspected or actually launched.

#### Scenario: Readiness refresh runs without launching a team

- **WHEN** the durable readiness projection is refreshed
- **THEN** the receipt SHALL preserve `durable_workflow_adopted=false` and `persistent_team_launched=false` unless a real launch occurred
- **AND** it SHALL NOT use wrapper generation or selector presence as a launch receipt.
