# codex-user-level-team-mode-team-entrypoints Specification

## Purpose
TBD - created by archiving change implement-codex-user-level-team-mode-p2-team-entrypoints. Update Purpose after archive.
## Requirements
### Requirement: The installer SHALL generate user-level OMX team entrypoint assets

The installer SHALL generate additive user-level team entrypoint assets into the target Codex home.

The generated wrappers SHALL remain usable on native Windows and SHALL NOT assume that Unix `tmux` is the only supported execution backend.

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

#### Scenario: Use a generated team entrypoint on native Windows after P6

- **WHEN** the operator runs a generated wrapper such as `omx-team-dev.ps1` on native Windows
- **THEN** the wrapper SHALL remain valid
- **AND** it SHALL route into a supported native Windows execution backend when the runtime provides one

### Requirement: Generated wrappers SHALL call a resolved native OMX command path

The installer SHALL resolve the native `omx` command path, or accept an explicit override, and generated wrappers SHALL call that resolved path directly.

The installer SHALL NOT replace or overwrite the native `omx` executable.

#### Scenario: A test install uses a fake OMX target

- **WHEN** the installer is run with an explicit fake `omx` command path
- **THEN** the generated wrappers SHALL call that fake command path
- **AND** wrapper behavior SHALL remain testable without modifying the real user install

### Requirement: Development and debug wrappers SHALL encode approved durable-team defaults

`omx-team-dev.ps1` SHALL encode a durable development-team preset.

At minimum:

- default worker count: `2`
- default worker role: `team-executor`
- optional override to `executor`

`omx-team-debug.ps1` SHALL encode a durable debug-team preset.

At minimum:

- default worker count: `2`
- default worker role: `debugger`

#### Scenario: Development wrapper launches a conservative worker swarm

- **WHEN** the operator runs `omx-team-dev.ps1 -Task "ship feature X"`
- **THEN** it SHALL invoke the equivalent of `omx team 2:team-executor "ship feature X"`

#### Scenario: Debug wrapper launches a debugger swarm

- **WHEN** the operator runs `omx-team-debug.ps1 -Task "stabilize regression X"`
- **THEN** it SHALL invoke the equivalent of `omx team 2:debugger "stabilize regression X"`

### Requirement: The ops wrapper SHALL expose the supported team lifecycle and safe read-only team inspection surface

`omx-team-ops.ps1` SHALL wrap the supported lifecycle commands:

- `status`
- `await`
- `resume`
- `shutdown`

It SHALL also support safe read-only team API operations such as:

- `list-tasks`
- `mailbox-list`
- `get-summary`
- `read-manifest`

#### Scenario: Ops wrapper shows team status

- **WHEN** the operator runs `omx-team-ops.ps1 -Action status -TeamName my-team`
- **THEN** it SHALL invoke the equivalent of `omx team status my-team`

#### Scenario: Ops wrapper uses read-only team API inspection

- **WHEN** the operator runs `omx-team-ops.ps1 -Action list-tasks -TeamName my-team`
- **THEN** it SHALL invoke the corresponding `omx team api` read-only operation
- **AND** it SHALL provide the team name as API input

### Requirement: The hybrid wrapper SHALL map heterogeneous staffing to leader-side experts plus one homogeneous durable worker team

`omx-team-hybrid.ps1` SHALL accept staffing counts such as architect, planner, executor, and verifier.

It SHALL interpret them by:

- keeping expert roles as leader-side native subagents
- mapping executor count to one homogeneous durable worker swarm
- emitting a structured plan that states the expert counts, the durable worker launch shape, and the expected checkpoints for expert use

It MAY optionally launch the durable worker swarm.

It SHALL NOT claim that every requested role becomes a persistent pane by default.

#### Scenario: Hybrid wrapper interprets expert counts without creating mixed persistent panes

- **WHEN** the operator runs `omx-team-hybrid.ps1 -Architect 1 -Planner 1 -Executor 2 -Verifier 1 -Task "implement rollout X"`
- **THEN** it SHALL report that architect, planner, and verifier remain leader-side native roles
- **AND** it SHALL derive one durable worker swarm from the executor count

### Requirement: The verify wrapper SHALL reinforce leader-side native verification roles

`omx-team-verify.ps1` SHALL output a verification plan for leader-side native roles instead of defaulting to a persistent verifier swarm.

At minimum it SHALL be able to plan use of:

- `verifier`
- `test-engineer`
- `security-reviewer`
- `writer`

#### Scenario: Verification wrapper plans final sign-off without launching a verifier pane

- **WHEN** the operator runs `omx-team-verify.ps1` for a behavior-changing multi-file change
- **THEN** it SHALL recommend leader-side native verification roles
- **AND** it SHALL not require a persistent verifier pane as the default path

### Requirement: The installer SHALL generate a reusable playbook for cross-repository operation

The installer SHALL generate a user-level playbook that documents:

- team-mode state meanings
- wrapper usage
- team lifecycle commands
- hybrid staffing interpretation
- the separation between open-ended research roles and implementation roles

#### Scenario: A user reads the generated playbook from another repository

- **WHEN** the user opens the generated playbook outside this repository
- **THEN** it SHALL still describe a reusable operator workflow
- **AND** it SHALL not depend on downstream application-specific runtime commands

#### Scenario: Generated playbook explains the user-level backend policy surface

- **WHEN** the operator reads the generated playbook from another repository
- **THEN** it SHALL identify the primary backend-policy surface and the supporting backend-policy views
- **AND** it SHALL explain the stable default backend, preferred backend use cases, and backend-family switching rules
- **AND** it SHALL state that repository-local specs and bilingual implementation plans remain the development source of truth for backend-policy evolution

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

### Requirement: The installer SHALL generate LangGraph durable orchestration entrypoints

The installer SHALL generate additive LangGraph-oriented durable orchestration entrypoints into the target Codex home.

The generated LangGraph asset set SHALL include operator surfaces for at least:

- run or start
- status or inspect
- resume
- interrupt inspection

The generated playbook SHALL document how these LangGraph entrypoints relate to the existing `omx team` entrypoints.

#### Scenario: Operator inspects generated LangGraph entrypoints

- **WHEN** the installer renders user-level team-mode assets into a target Codex home
- **THEN** it SHALL generate additive LangGraph entrypoint assets there
- **AND** the generated playbook SHALL explain how they coexist with the existing `omx team` wrappers

### Requirement: The generated playbook SHALL document orchestration activation and retrofit rules

The generated user-level playbook SHALL document:

- the mandatory orchestration re-check triggers
- that explicit requests to use `omx` or `LangGraph` are hard routing directives
- that existing projects with new sessions automatically follow the current user-level policy
- that existing live sessions retrofit on reload, restart, explicit user directive, or tracked durable-state detection

#### Scenario: Operator reads the generated playbook for an existing repository

- **WHEN** the operator reads the generated playbook while working in an existing repository or continuing an existing workstream
- **THEN** the playbook SHALL describe how orchestration activation is re-checked and retrofitted
- **AND** it SHALL not imply that orchestration rules apply only to brand-new repositories or brand-new sessions

### Requirement: Generated team entrypoints SHALL participate in the canonical inspectable durable-state surface
The generated user-level team entrypoint layer SHALL participate in the canonical inspectable durable-state surface instead of leaving durable-team inspection split into unrelated wrapper descriptions only.

At minimum:

- the generated read-only team inspection paths SHALL expose enough information to derive the shared summary fields for tracked native durable-team state
- the generated playbook SHALL explain how the canonical inspectable state surface relates to `omx-team-ops.ps1` and other backend-specific helpers

#### Scenario: Operator inspects current native durable-team state from generated entrypoints
- **WHEN** the operator uses the approved read-only team inspection entrypoints for a tracked native durable team
- **THEN** those entrypoints SHALL provide or feed the data needed for the canonical inspectable durable-state summary
- **AND** the operator SHALL not need to infer current worker shape, tracked identity, and next inspection path only from scattered wrapper prose

### Requirement: The generated playbook SHALL link to a quick-reference companion
The generated user-level playbook SHALL link to a concise quick-reference companion for the most common operator commands.

That companion SHALL live in the user-level docs layer and SHALL remain aligned with the actually installed user-level command surface.

#### Scenario: Operator starts from the full playbook but only needs common commands
- **WHEN** the operator opens the generated playbook and only needs the most common commands
- **THEN** the playbook SHALL point to the quick-reference companion
- **AND** the operator SHALL not need to scan the full playbook to find the most common command entrypoints

### Requirement: The generated team entrypoint layer SHALL include an advanced compose entrypoint when mixed persistent pane compose is enabled

When the advanced mixed persistent pane compose layer is enabled, the generated user-level team entrypoint layer SHALL include a user-level compose entrypoint and manifest guidance.

The generated playbook SHALL describe that compose mode as an advanced opt-in path rather than as the default workflow.

The generated entrypoint guidance SHALL also distinguish:

- preview or validation behavior
- real launch behavior for supported pane roles
- planned-only behavior for unsupported pane roles in the first runtime rollout

#### Scenario: Operator reads generated entrypoint guidance for advanced compose mode
- **WHEN** the operator reads the generated user-level playbook after compose assets are installed
- **THEN** the playbook SHALL identify the compose entrypoint and its manifest requirement
- **AND** it SHALL describe mixed persistent pane compose as an advanced opt-in mode

#### Scenario: Operator applies a mixed manifest through the generated compose entrypoint
- **WHEN** the operator uses the generated compose entrypoint with `-Apply` for a manifest that includes both supported and unsupported pane roles
- **THEN** the entrypoint guidance SHALL describe that supported panes may launch for real
- **AND** it SHALL describe unsupported panes as planned-only rather than as fully launched panes

### Requirement: The generated team entrypoint layer SHALL include compose lifecycle helper entrypoints

When advanced compose runtime is available, the generated user-level team entrypoint layer SHALL include compose lifecycle helper entrypoints and related operator guidance.

At minimum that guidance SHALL distinguish compose launch, compose inspect, compose shutdown, and compose reconcile surfaces.

#### Scenario: Operator reads generated compose helper guidance

- **WHEN** the operator reads the generated user-level playbook after compose lifecycle helpers are installed
- **THEN** the playbook SHALL identify the compose lifecycle helper entrypoints
- **AND** it SHALL explain how they relate to `omx-team-compose.ps1`, `omx-team-ops.ps1`, and the canonical durable-state summary

### Requirement: The generated team entrypoint layer SHALL include compose await guidance and partial-state guidance

When compose runtime lifecycle helpers are installed, the generated team entrypoint layer SHALL include compose await guidance and partial compose lifecycle state guidance.

#### Scenario: Operator reads generated playbook for compose partial lifecycle state

- **WHEN** the operator reads the generated playbook after compose await support is installed
- **THEN** the playbook SHALL identify the compose await helper
- **AND** it SHALL explain how partial compose runtime state differs from fully active or fully shut down runtime

### Requirement: The generated team entrypoint layer SHALL include compose recovery or resume guidance

When compose recovery support is installed, the generated team entrypoint layer SHALL include compose recovery or resume guidance.

#### Scenario: Operator reads generated playbook for compose recovery posture

- **WHEN** the operator reads the generated playbook after compose recovery support is installed
- **THEN** the playbook SHALL identify the compose recovery or resume helper
- **AND** it SHALL explain how compose recovery posture differs from ordinary pane-level resume guidance
