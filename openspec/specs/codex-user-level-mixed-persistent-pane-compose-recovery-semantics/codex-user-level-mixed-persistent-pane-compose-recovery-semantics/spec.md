# codex-user-level-mixed-persistent-pane-compose-recovery-semantics Specification

## Purpose

Define the explicit multi-pane recovery posture and recovery helper surface for tracked advanced compose runtime.

## Requirements

### Requirement: Tracked compose runtime SHALL expose explicit multi-pane recovery posture

Tracked compose runtime SHALL expose explicit multi-pane recovery posture rather than leaving recovery decisions implicit in raw pane state.

At minimum the first rollout SHALL distinguish:

- `resumable` - compose-recovery state meaning the pane or run can continue safely.
- `degraded_recoverable` - compose-recovery state meaning recovery is possible with degraded context or capability.
- `manual_intervention_required` - compose-recovery state meaning operator action is required before continuing.

#### Scenario: Operator inspects a partially surviving compose runtime

- **WHEN** tracked compose runtime contains launched panes with mixed current availability
- **THEN** the runtime SHALL classify its recovery posture explicitly
- **AND** it SHALL not require the operator to infer recovery eligibility only from raw pane directories

### Requirement: The user-level installation SHALL generate a compose recovery helper surface

The user-level installation SHALL generate a compose-scoped recovery or resume helper surface for tracked compose runtime.

#### Scenario: Operator inspects generated compose recovery helper assets

- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate the compose recovery helper entrypoint there
- **AND** that helper SHALL remain additive to the existing compose lifecycle helper set
