# codex-user-level-mixed-persistent-pane-compose-runtime Specification

## Purpose

Define the controlled advanced compose runtime for launching supported persistent pane roles from an explicit manifest while preserving the default hybrid operating model.

## Requirements

### Requirement: Compose apply SHALL launch supported persistent pane roles from an explicit manifest

When the operator explicitly applies advanced compose mode, the compose runtime SHALL launch manifest panes whose roles are in the supported persistent-pane set for the current rollout.

The first supported runtime set SHALL remain limited to worker-centric roles that map to the existing native durable-team lifecycle.

#### Scenario: Operator applies a manifest with only supported pane roles

- **WHEN** the operator runs the compose entrypoint with `-Apply` against a manifest whose panes all use supported roles
- **THEN** the compose runtime SHALL launch those panes through the supported durable execution path
- **AND** it SHALL not leave the apply action in plan-persistence-only mode

### Requirement: Unsupported panes SHALL remain explicit planned-only entries during compose apply

When a compose manifest mixes supported and unsupported pane roles, the runtime SHALL preserve unsupported panes as explicit planned-only entries instead of pretending they launched.

#### Scenario: Operator applies a mixed manifest with supported and unsupported panes

- **WHEN** the operator applies a compose manifest that contains both supported worker panes and unsupported expert panes
- **THEN** the compose runtime SHALL launch the supported panes
- **AND** it SHALL report the unsupported panes as planned-only rather than as launched panes

### Requirement: Compose runtime SHALL persist tracked runtime state and per-pane launch results

The compose runtime SHALL persist repo-local runtime state under the compose state root separately from the declared compose plan.

That runtime state SHALL record at minimum:

- which panes launched successfully
- which panes remained planned-only
- which tracked identities were created
- which launch failures occurred

#### Scenario: Operator inspects a repository after compose apply

- **WHEN** the operator inspects repo-local compose state after a compose apply action
- **THEN** the runtime state SHALL distinguish declared topology from actual launch results
- **AND** it SHALL expose enough information to identify launched panes, planned-only panes, and tracked identities

### Requirement: Tracked compose runtime SHALL expose lifecycle metadata for shutdown and reattach guidance

Tracked compose runtime state SHALL expose enough lifecycle metadata to support compose shutdown and pane-level reattach guidance.

At minimum it SHALL distinguish launched panes, planned-only panes, failed panes, and tracked pane identities.

#### Scenario: Operator inspects tracked compose runtime before later lifecycle actions

- **WHEN** tracked compose runtime state exists for the current repository
- **THEN** that runtime state SHALL include lifecycle metadata needed for shutdown targeting and pane-level reattach guidance
- **AND** it SHALL not require the operator to infer launched versus planned-only panes from raw state fragments alone

### Requirement: Tracked compose runtime SHALL classify partial-shutdown and partial-health state explicitly

Tracked compose runtime SHALL classify partial-shutdown and partial-health state explicitly when launched pane teams no longer all share the same lifecycle outcome.

#### Scenario: Some launched pane teams are present and some are missing

- **WHEN** tracked compose runtime references launched pane teams and only a subset of those teams still exist
- **THEN** the runtime SHALL classify itself as partial rather than fully active or fully shut down
- **AND** it SHALL preserve enough pane-level metadata for later await, shutdown, or reconcile decisions

### Requirement: Tracked compose runtime SHALL distinguish resumable and manual-intervention-required recovery posture

Tracked compose runtime SHALL distinguish between resumable and manual-intervention-required recovery posture when launched pane teams no longer all share the same lifecycle outcome.

#### Scenario: Only a subset of launched panes remain resumable

- **WHEN** tracked compose runtime includes pane-level resume candidates but also missing or otherwise non-resumable launched panes
- **THEN** the runtime SHALL classify whether the overall compose runtime remains resumable or requires manual intervention
- **AND** it SHALL preserve enough pane-level metadata to justify that classification
