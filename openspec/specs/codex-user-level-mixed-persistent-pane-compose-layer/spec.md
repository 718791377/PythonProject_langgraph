# codex-user-level-mixed-persistent-pane-compose-layer Specification

## Purpose

Define the advanced opt-in manifest-driven compose layer for mixed persistent panes in user-level Codex / oh-my-codex team mode.

## Requirements

### Requirement: The user-level installation SHALL define a manifest-driven mixed persistent pane compose layer

The user-level installation SHALL define an advanced manifest-driven compose layer for mixed persistent panes.

That compose layer SHALL remain explicitly outside the default operating mode.

At minimum the compose asset set SHALL include:

- a user-level compose entrypoint such as `omx-team-compose.ps1`
- a user-level compose manifest schema under the user-level asset root

#### Scenario: Operator enables the advanced compose layer explicitly

- **WHEN** the operator chooses the mixed persistent pane compose mode explicitly
- **THEN** the user-level installation SHALL expose a manifest-driven compose path
- **AND** it SHALL not require the operator to assemble the pane topology only through ad hoc pane creation

### Requirement: The compose manifest SHALL declare pane topology and ownership boundaries

The compose manifest SHALL declare at minimum:

- pane identities
- role bindings
- worktree allocation
- mailbox routing
- ownership boundaries
- checkpoint policy

#### Scenario: Operator prepares a heterogeneous persistent pane topology

- **WHEN** the operator prepares a compose manifest for mixed persistent panes
- **THEN** the manifest SHALL describe pane identity, worktree, mailbox, and ownership boundaries explicitly
- **AND** it SHALL not leave write scope or checkpoint responsibilities implicit

### Requirement: Mixed persistent pane compose SHALL remain an advanced opt-in mode

The mixed persistent pane compose layer SHALL remain explicitly opt-in.

It SHALL NOT become the default result of ordinary routing thresholds.

#### Scenario: Ordinary automatic routing evaluates a normal heterogeneous task

- **WHEN** the current task is handled by the normal user-level routing thresholds without explicit compose invocation
- **THEN** the workflow SHALL stay on the default operating model
- **AND** it SHALL not silently escalate into mixed persistent panes

### Requirement: The leader SHALL remain outside the pane roster

The current main Codex CLI session SHALL remain the leader lane even when mixed persistent panes are enabled.

The compose layer SHALL NOT redefine the leader as a persistent worker pane.

#### Scenario: Operator launches compose mode

- **WHEN** the operator launches mixed persistent pane compose mode
- **THEN** the current main Codex CLI session SHALL remain outside the pane roster
- **AND** final routing, conflict handling, and integration ownership SHALL remain with that main session

### Requirement: The advanced compose layer SHALL allow controlled supported-pane launch without becoming the default path

The advanced mixed persistent pane compose layer SHALL allow controlled real launch for supported pane roles when the operator explicitly applies compose mode.

It SHALL continue to preserve the default-path boundary and SHALL NOT become the result of ordinary routing thresholds.

#### Scenario: Operator explicitly applies compose mode for a supported pane topology

- **WHEN** the operator explicitly applies mixed persistent pane compose for a manifest that includes supported pane roles
- **THEN** the compose layer SHALL permit controlled launch for those supported panes
- **AND** it SHALL not change the rule that compose remains outside the default operating mode
