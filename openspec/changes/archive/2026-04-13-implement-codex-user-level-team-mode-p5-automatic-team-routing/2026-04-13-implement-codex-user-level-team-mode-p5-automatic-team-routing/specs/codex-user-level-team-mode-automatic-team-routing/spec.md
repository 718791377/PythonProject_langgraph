## ADDED Requirements

### Requirement: The installer SHALL generate an automatic durable-team routing helper

The installer SHALL generate an additive user-level durable-team routing helper into the target Codex home.

The generated asset set SHALL include:

- `bin/omx-team-auto.ps1`

The helper SHALL remain additive-only and SHALL call the resolved native `omx` command path rather than replacing the native executable.

#### Scenario: Generate the P5 helper into a temporary Codex home

- **WHEN** the installer is run against an explicit target Codex home
- **THEN** it SHALL generate `bin/omx-team-auto.ps1`
- **AND** it SHALL keep the helper inside the existing backup and rollback transaction

### Requirement: The helper SHALL emit an inspectable automatic durable-team routing plan

`omx-team-auto.ps1` SHALL output a structured routing plan before mutating state.

At minimum the plan SHALL include:

- current mode and capability flags
- requested phase
- the desired durable team shape, if any
- the tracked team record, if any
- the decision: `no-team`, `launch`, `reuse`, `switch`, `shutdown`, or `manual-inspection-required`

#### Scenario: Execute-parallel planning chooses the conservative worker swarm

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Task "implement rollout X" -Json`
- **THEN** it SHALL report a durable-team decision
- **AND** it SHALL derive the equivalent of `2:team-executor`

#### Scenario: Verify-accept planning does not keep a durable team alive

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase verify-accept -Task "final sign-off" -Json`
- **THEN** it SHALL return a no-team or shutdown-class decision
- **AND** it SHALL not derive a new durable worker launch

### Requirement: Automatic routing SHALL only manage tracked repo-local teams

The helper SHALL use a repo-local tracked-team record at:

- `.omx/state/team/codex-auto-managed-team.json`

The helper SHALL only auto-manage a team when the tracked record exists and the recorded team still exists in the current repository team state root.

The helper SHALL NOT auto-adopt an unmanaged existing team by default.

#### Scenario: Existing unmanaged team does not get auto-adopted

- **WHEN** the repository contains a latest team directory but no tracked-team record
- **THEN** the helper SHALL return `manual-inspection-required` or an equivalent safe non-mutating decision
- **AND** it SHALL not automatically shut down, reuse, or switch that unmanaged team

### Requirement: Apply mode SHALL support launch, reuse, switch, and shutdown

When `-Apply` is provided, the helper SHALL execute the planned durable-team mutation through the native `omx` CLI.

At minimum:

- `launch` SHALL call `omx team <workerspec> "<task>"`
- `reuse` SHALL call `omx team api create-task`
- `switch` SHALL shut down the tracked team and launch the new desired team
- `shutdown` SHALL shut down the tracked team and clear the tracked-team record

#### Scenario: Reuse dispatches work into the tracked team

- **WHEN** a tracked team matches the desired worker role and worker count
- **AND** the operator runs `omx-team-auto.ps1 -Apply`
- **THEN** the helper SHALL route the new task through `omx team api create-task`
- **AND** it SHALL preserve the tracked-team record

#### Scenario: Phase change triggers a debug-team switch

- **WHEN** the tracked team is a development swarm
- **AND** the operator runs `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 2 -Apply`
- **THEN** the helper SHALL shut down the tracked development swarm
- **AND** it SHALL launch the equivalent of `omx team 2:debugger "<task>"`
- **AND** it SHALL update the tracked-team record
