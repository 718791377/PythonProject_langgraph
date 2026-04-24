# codex-user-level-mixed-persistent-pane-compose-lifecycle-helpers Specification

## Purpose

Define the compose-scoped lifecycle helper surfaces for tracked advanced compose runtime, including inspect, shutdown, and compose-specific reconcile flows.

## Requirements

### Requirement: The user-level installation SHALL generate compose lifecycle helper surfaces

The user-level installation SHALL generate compose-specific lifecycle helper surfaces for tracked compose runtime.

At minimum the generated compose lifecycle-helper set SHALL include:

- a read-oriented compose status or inspect helper
- a compose shutdown helper
- a compose reconcile helper

#### Scenario: Operator inspects generated compose lifecycle helper assets

- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate the compose lifecycle helper entrypoints there
- **AND** those entrypoints SHALL remain additive to the existing team and compose launch surfaces

### Requirement: Compose status or inspect SHALL expose pane-level lifecycle state and helper pointers

The compose status or inspect helper SHALL expose tracked compose runtime state including launched panes, planned-only panes, failed panes, and pane-level helper pointers for further operations.

#### Scenario: Operator inspects a tracked compose runtime

- **WHEN** the current repository has tracked compose runtime state
- **THEN** the compose status or inspect helper SHALL expose pane-level launch outcomes and tracked identities
- **AND** it SHALL provide explicit helper pointers for per-pane reattach or lifecycle operations

### Requirement: Compose shutdown SHALL only target launched panes recorded in tracked compose runtime state

The compose shutdown helper SHALL only shut down pane teams that are recorded as launched in the tracked compose runtime state for the current repository.

It SHALL NOT guess unmanaged team directories or treat planned-only panes as launched pane resources.

#### Scenario: Operator shuts down a tracked compose runtime

- **WHEN** the operator requests compose shutdown for a repository with tracked launched compose panes
- **THEN** the helper SHALL target only those launched pane teams
- **AND** it SHALL not shut down unmanaged native durable-team residue outside the tracked compose runtime

### Requirement: Compose reconcile SHALL classify stale compose runtime residue conservatively

The compose reconcile helper SHALL classify compose-specific residue conservatively and SHALL keep safe cleanup narrow in the first rollout.

#### Scenario: Compose runtime record exists but no launched pane teams remain

- **WHEN** tracked compose runtime state exists but the launched pane teams it references no longer exist
- **THEN** the compose reconcile helper SHALL classify that runtime record as stale compose residue
- **AND** it MAY expose it as a safe cleanup candidate if no protected residue remains

### Requirement: The compose lifecycle helper set SHALL include a compose await helper

When compose lifecycle helpers are installed, the user-level helper set SHALL include a compose-scoped await helper for tracked compose runtime.

#### Scenario: Operator inspects generated compose await helper assets

- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate a compose await helper entrypoint there
- **AND** that helper SHALL remain additive to the existing compose inspect, shutdown, and reconcile surfaces

### Requirement: Compose await SHALL expose aggregate compose runtime wait state

The compose await helper SHALL report aggregate wait state for the tracked compose runtime instead of forcing the operator to infer it only from pane-by-pane helpers.

#### Scenario: Operator awaits a partially active compose runtime

- **WHEN** tracked compose runtime exists and only some launched panes still remain active
- **THEN** the compose await helper SHALL classify the runtime as partial rather than fully healthy or fully shut down
- **AND** it SHALL expose which launched panes are still present versus missing

### Requirement: Compose lifecycle helpers SHALL expose compose-scoped recovery guidance

When tracked compose runtime exists, the compose lifecycle helper layer SHALL expose compose-scoped recovery guidance in addition to inspect, await, shutdown, and reconcile.

#### Scenario: Operator inspects tracked compose runtime for recovery decisions

- **WHEN** the current repository has tracked compose runtime
- **THEN** the compose lifecycle helper layer SHALL expose a compose recovery or resume helper pointer
- **AND** it SHALL relate pane-level resume candidates to the aggregate compose recovery posture
