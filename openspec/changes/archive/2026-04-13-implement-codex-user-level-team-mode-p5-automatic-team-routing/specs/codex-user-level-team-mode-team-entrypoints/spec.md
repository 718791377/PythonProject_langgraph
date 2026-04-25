## MODIFIED Requirements

### Requirement: The installer SHALL generate user-level OMX team entrypoint assets

The installer SHALL generate additive user-level team entrypoint assets into the target Codex home.

The generated asset set SHALL include at least:

- `bin/omx-team-dev.ps1`
- `bin/omx-team-debug.ps1`
- `bin/omx-team-verify.ps1`
- `bin/omx-team-ops.ps1`
- `bin/omx-team-hybrid.ps1`
- `bin/omx-team-auto.ps1`
- `docs/team-mode-playbook.md`

#### Scenario: Generate the P2 plus P5 entrypoint layer into a temporary Codex home

- **WHEN** the installer is run against an explicit target Codex home
- **THEN** it SHALL generate the manual and automatic team entrypoint wrappers there
- **AND** it SHALL keep the new assets additive-only

## ADDED Requirements

### Requirement: The automatic team helper SHALL map phase and workload signals to the approved durable-team presets

`omx-team-auto.ps1` SHALL accept explicit phase and workload signals and interpret them by:

- keeping early and final phases subagent-only
- mapping execution and integration phases to a conservative `team-executor` swarm when the parallel-slice threshold is met
- mapping stabilization to a `debugger` swarm when the blocking-issue threshold is met

It MAY optionally apply the planned action.

It SHALL NOT claim that every automatic decision becomes a mixed persistent pane topology.

#### Scenario: Automatic helper chooses `3:team-executor` for broader parallel execution

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 3 -Task "ship rollout X" -Json`
- **THEN** it SHALL derive the equivalent of `omx team 3:team-executor "ship rollout X"`

#### Scenario: Automatic helper chooses `2:debugger` for stabilization

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 1 -Task "stabilize regression X" -Json`
- **THEN** it SHALL derive the equivalent of `omx team 2:debugger "stabilize regression X"`
