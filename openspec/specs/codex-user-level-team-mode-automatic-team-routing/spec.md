# codex-user-level-team-mode-automatic-team-routing Specification

## Purpose
TBD - created by archiving change implement-codex-user-level-team-mode-p5-automatic-team-routing. Update Purpose after archive.
## Requirements
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

On native Windows, this SHALL mean a supported native Windows backend rather than a hard Unix `tmux` dependency.

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

#### Scenario: `omx-team-auto.ps1 -Apply` launches a team on native Windows after P6

- **WHEN** the operator runs `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Apply` on native Windows
- **THEN** the helper SHALL be able to execute the launch through the Windows backend
- **AND** it SHALL still preserve the tracked-team record contract

### Requirement: Automatic durable routing SHALL honor the selected durable orchestration backend

The automatic durable routing layer SHALL honor the selected durable orchestration backend instead of assuming that every durable decision launches directly through the current native `omx team` path.

When the selected backend is `langgraph`, the planned durable execution result SHALL identify the LangGraph backend as the target durable path.

#### Scenario: Automatic routing plans LangGraph durable execution

- **WHEN** the durable orchestration backend selector is `langgraph`
- **AND** the task meets durable execution thresholds
- **THEN** the automatic durable routing plan SHALL identify LangGraph as the selected backend
- **AND** it SHALL not misreport the decision as a direct `omx team` launch

### Requirement: Automatic durable routing SHALL choose the effective lane per task flow from enabled capabilities
Automatic durable routing SHALL choose the effective lane per task flow from the enabled orchestration capability set.

It SHALL not require a global backend-family switch every time the task flow is better suited to another enabled lane.

When scoped durable activation exists, it SHALL use that scoped activation as the authoritative activation source for future-session durable decisions.

Legacy repo-local durable artifacts MAY remain inspectable, but they SHALL NOT dominate future-session lane selection only because a legacy tracked record or `thread_id` exists.

#### Scenario: Worker-centric task flow uses native_omx while LangGraph remains enabled

- **WHEN** the layered capability set enables both oh-my-codex durable features and LangGraph
- **AND** the current task flow is better suited to worker-centric durable execution
- **THEN** the automatic durable routing layer SHALL choose `native_omx` as the effective lane
- **AND** it SHALL not require LangGraph capability to be globally disabled first

#### Scenario: Preserved legacy LangGraph backend record does not dominate a future unrelated task flow

- **WHEN** a repository contains a preserved legacy LangGraph backend record
- **AND** no scoped activation selector declares that record active for the current future session
- **THEN** automatic durable routing SHALL treat that record as inspectable legacy state rather than as the authoritative effective lane
- **AND** it SHALL not auto-resume or auto-select LangGraph only because the legacy tracked record exists

### Requirement: Automatic durable routing SHALL honor cleanup and reconciliation classification
Automatic durable-team routing SHALL honor cleanup and reconciliation classification instead of silently treating stale or unmanaged residue as active tracked durable state.

At minimum:

- safe empty residue MAY be ignored or cleaned through the approved reconciliation path
- empty unmanaged native residue SHALL NOT by itself force `manual-inspection-required`
- unmanaged residue SHALL NOT be auto-adopted as tracked state
- protected or ambiguous residue SHALL force a manual-inspection-required or equivalent safe decision

#### Scenario: Empty unmanaged native residue exists beside a tracked durable backend
- **WHEN** a tracked durable backend exists
- **AND** empty unmanaged native team residue is also present
- **THEN** automatic durable routing SHALL not auto-adopt that residue as tracked state
- **AND** it SHALL preserve a safe routing decision that treats the residue as cleanup or reconciliation context rather than as the active durable backend

#### Scenario: Empty unmanaged native residue does not block future native launch
- **WHEN** a repository contains empty unmanaged native team directories but no non-empty unmanaged native residue
- **AND** the desired future-session durable decision is a native launch, reuse, or switch
- **THEN** automatic durable routing SHALL ignore that empty residue as a blocker
- **AND** it SHALL not force `manual-inspection-required` only because those unmanaged directories exist
