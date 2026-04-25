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

### Requirement: The user-level installation SHALL expose an additive LangGraph subgraph-library inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-library inspection entrypoint.

#### Scenario: Operator looks for available reusable LangGraph subgraphs

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-library inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph stream-observability entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph stream-observability helper.

#### Scenario: Operator looks for LangGraph streaming and debug observability

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph stream-observability helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph runtime/store inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph runtime/store inspection helper.

#### Scenario: Operator looks for runtime-context and store-injection inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph runtime/store inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph migration/compatibility inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph migration/compatibility inspection helper.

#### Scenario: Operator looks for graph-migration and thread-compatibility inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph migration/compatibility inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph approval-queue inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph approval-queue inspection helper.

#### Scenario: Operator looks for multi-interrupt approval inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph approval-queue inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph graph-kernel inspection entrypoint

When the user-level LangGraph runtime-kernel lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph graph-kernel inspection helper.

#### Scenario: Operator looks for graph-native runtime-kernel inspection

- **WHEN** the user-level installation includes the LangGraph runtime-kernel lane
- **THEN** the generated entrypoint set SHALL include a LangGraph graph-kernel inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph primary-runtime inspection entrypoint

When the user-level LangGraph primary-runtime engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph primary-runtime inspection helper.

#### Scenario: Operator looks for compiled graph-engine inspection

- **WHEN** the user-level installation includes the LangGraph primary-runtime engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph primary-runtime inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph compiled-invocation inspection entrypoint

When the user-level LangGraph compiled-invocation lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph compiled-invocation inspection helper.

#### Scenario: Operator looks for live compiled graph inspection

- **WHEN** the user-level installation includes the LangGraph compiled-invocation lane
- **THEN** the generated entrypoint set SHALL include a LangGraph compiled-invocation inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph live-execution inspection entrypoint

When the user-level LangGraph live-execution lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph live-execution inspection helper.

#### Scenario: Operator looks for live compiled execution inspection

- **WHEN** the user-level installation includes the LangGraph live-execution lane
- **THEN** the generated entrypoint set SHALL include a LangGraph live-execution inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph memory/store inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph memory/store inspection helper.

#### Scenario: Operator looks for memory-store and semantic-memory inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph memory/store inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph runtime/store inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph runtime/store inspection helper.

#### Scenario: Operator looks for runtime-context and store-injection inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph runtime/store inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph generalized live-routing inspection entrypoint

When the user-level LangGraph generalized live-routing lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph generalized live-routing inspection helper.

#### Scenario: Operator looks for generalized live-routing inspection

- **WHEN** the user-level installation includes the LangGraph generalized live-routing lane
- **THEN** the generated entrypoint set SHALL include a LangGraph generalized live-routing inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive LangGraph subgraph-state inspection entrypoint

When the user-level LangGraph subgraph persistence-mode lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-state inspection helper.

#### Scenario: Operator looks for subgraph-state inspection

- **WHEN** the user-level installation includes the LangGraph subgraph persistence-mode lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, subgraphs, kernel, engine, invocation, live-execution, generalized-routing, approval-queue, migration, memory, runtime, stream, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive fuller live-engine inspection entrypoint

When the user-level LangGraph fuller live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph fuller live-engine inspection helper.

#### Scenario: Operator looks for fuller live-engine inspection

- **WHEN** the user-level installation includes the LangGraph fuller live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph fuller live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, generalized-routing, subgraph-state, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive automatic runtime-policy inspection entrypoint

When the user-level LangGraph richer automatic runtime-policy lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph automatic runtime-policy inspection helper.

#### Scenario: Operator looks for automatic runtime-policy inspection

- **WHEN** the user-level installation includes the LangGraph automatic runtime-policy lane
- **THEN** the generated entrypoint set SHALL include a LangGraph automatic runtime-policy inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, generalized-routing, subgraph-state, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive deeper live-engine inspection entrypoint

When the user-level LangGraph deeper live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph deeper live-engine inspection helper.

#### Scenario: Operator looks for deeper live-engine inspection

- **WHEN** the user-level installation includes the LangGraph deeper live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph deeper live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive broader automatic runtime-policy inspection entrypoint

When the user-level LangGraph broader automatic runtime-policy lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph broader automatic runtime-policy inspection helper.

#### Scenario: Operator looks for broader automatic runtime-policy inspection

- **WHEN** the user-level installation includes the LangGraph broader automatic runtime-policy lane
- **THEN** the generated entrypoint set SHALL include a LangGraph broader automatic runtime-policy inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive superstep live-engine inspection entrypoint

When the user-level LangGraph superstep live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph superstep live-engine inspection helper.

#### Scenario: Operator looks for superstep live-engine inspection

- **WHEN** the user-level installation includes the LangGraph superstep live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph superstep live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive stateful live-engine inspection entrypoint

When the user-level LangGraph stateful live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph stateful live-engine inspection helper.

#### Scenario: Operator looks for stateful live-engine inspection

- **WHEN** the user-level installation includes the LangGraph stateful live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph stateful live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive graph-resident live-engine boundary-state inspection entrypoint

When the user-level LangGraph graph-resident boundary-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph graph-resident live-engine boundary-state inspection helper.

#### Scenario: Operator looks for graph-resident live-engine boundary-state inspection

- **WHEN** the user-level installation includes the LangGraph graph-resident boundary-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph graph-resident live-engine boundary-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive subgraph-aware live-engine handoff-state inspection entrypoint

When the user-level LangGraph subgraph-aware handoff-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-aware live-engine handoff-state inspection helper.

#### Scenario: Operator looks for subgraph-aware live-engine handoff-state inspection

- **WHEN** the user-level installation includes the LangGraph subgraph-aware handoff-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-aware live-engine handoff-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive approval-aware live-engine resume-state inspection entrypoint

When the user-level LangGraph approval-aware resume-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph approval-aware live-engine resume-state inspection helper.

#### Scenario: Operator looks for approval-aware live-engine resume-state inspection

- **WHEN** the user-level installation includes the LangGraph approval-aware resume-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph approval-aware live-engine resume-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive recovery-aware live-engine provenance-state inspection entrypoint

When the user-level LangGraph recovery-aware provenance-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph recovery-aware live-engine provenance-state inspection helper.

#### Scenario: Operator looks for recovery-aware live-engine provenance-state inspection

- **WHEN** the user-level installation includes the LangGraph recovery-aware provenance-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph recovery-aware live-engine provenance-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive durable-artifact-aware live-engine inspection entrypoint

When the user-level LangGraph durable-artifact-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph durable-artifact-aware live-engine inspection helper.

#### Scenario: Operator looks for durable-artifact-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph durable-artifact-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph durable-artifact-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive reducer-aware live-engine inspection entrypoint

When the user-level LangGraph reducer-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph reducer-aware live-engine inspection helper.

#### Scenario: Operator looks for reducer-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph reducer-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph reducer-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, artifact-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive command-aware live-engine inspection entrypoint

When the user-level LangGraph command-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph command-aware live-engine inspection helper.

#### Scenario: Operator looks for command-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph command-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph command-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, artifact-engine, reducer-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive runtime-aware live-engine inspection entrypoint

When the user-level LangGraph runtime-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph runtime-aware live-engine inspection helper.

#### Scenario: Operator looks for runtime-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph runtime-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph runtime-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, artifact-engine, reducer-engine, command-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive memory-aware live-engine inspection entrypoint

When the user-level LangGraph memory-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph memory-aware live-engine inspection helper.

#### Scenario: Operator looks for memory-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph memory-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph memory-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, artifact-engine, reducer-engine, command-engine, runtime-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces

### Requirement: The user-level installation SHALL expose an additive migration-aware live-engine inspection entrypoint

When the user-level LangGraph migration-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph migration-aware live-engine inspection helper.

#### Scenario: Operator looks for migration-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph migration-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph migration-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, artifact-engine, reducer-engine, command-engine, runtime-engine, memory-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
