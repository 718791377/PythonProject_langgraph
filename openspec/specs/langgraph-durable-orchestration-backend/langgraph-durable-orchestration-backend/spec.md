# langgraph-durable-orchestration-backend Specification

## Purpose

Define the LangGraph-backed durable orchestration backend that integrates under the existing Codex / oh-my-codex leader model, including repo-local persistence, graph phases, research handoff, adversarial-review survivor queues, and interrupt/resume support.

## Requirements

### Requirement: The repository SHALL provide an additive LangGraph durable orchestration backend

The repository SHALL provide a LangGraph-based durable orchestration backend that integrates under the existing Codex / oh-my-codex leader workflow rather than replacing it.

The backend SHALL preserve:

- the current main Codex CLI session as leader
- oh-my-codex as the user-level control and workflow layer
- LangGraph as the persistent orchestration kernel for selected long-running tasks

#### Scenario: Operator selects the LangGraph backend

- **WHEN** the operator enables the LangGraph durable orchestration backend
- **THEN** the workflow SHALL keep the current main Codex CLI session as leader
- **AND** it SHALL not redefine LangGraph as a replacement for Codex itself

### Requirement: The LangGraph backend SHALL persist repo-local threads and checkpoints

The LangGraph backend SHALL persist execution through repo-local thread identity and checkpoints.

At minimum:

- each durable execution SHALL use a stable `thread_id`
- `thread_id` SHALL include repository and worktree identity plus a task identifier
- checkpoint data SHALL remain discoverable from repo-local `.omx` state

#### Scenario: A long-running task is resumed

- **WHEN** the operator resumes a previously started LangGraph-orchestrated task
- **THEN** the backend SHALL locate the existing thread by stable repo-local identity
- **AND** it SHALL resume from persisted checkpoint state rather than restarting from scratch

### Requirement: The LangGraph backend SHALL mirror the seven-phase development flow in a root graph

The LangGraph backend SHALL provide a root graph that mirrors the durable team workflow phases:

- define-target
- read-context
- freeze-plan
- execute-parallel
- integrate-converge
- stabilize
- verify-accept

The root graph SHALL support conditional edges driven by structured gate verdicts.

Selected flows MAY re-enter earlier nodes through bounded quality-gated loops when the gate result indicates the work remains repairable but not yet acceptable.

Persisted graph state SHALL record whether the current execution is first-pass, looping, interrupted, exhausted, or accepted.

#### Scenario: Graph state advances from planning to loop-capable execution

- **WHEN** the task has a frozen plan and enough execution slices to justify durable execution
- **THEN** the root graph SHALL be able to transition from `freeze-plan` into `execute-parallel`
- **AND** it SHALL preserve the current phase and loop-capable execution posture in persisted graph state

### Requirement: Research-to-implementation handoff SHALL persist a frozen implementation brief

The LangGraph durable flow SHALL persist research output as a frozen implementation brief instead of continuing implementation from the full open-ended research context.

That brief SHALL include structured fields covering at least:

- objective
- non-goals
- accepted decisions
- constraints
- ownership boundaries
- acceptance criteria

Execution SHALL restart from a fresh implementation context after the brief is frozen.

#### Scenario: Open-ended research moves into implementation

- **WHEN** research and planning have produced an approved implementation brief
- **THEN** the workflow SHALL persist that brief before durable execution begins
- **AND** the implementation path SHALL start from a fresh execution context rather than reusing the full research context

### Requirement: Adversarial bug review SHALL persist a survivor queue rather than a persistent bug triad

The LangGraph durable flow SHALL keep `bug-finder`, `bug-rebutter`, and `bug-judge` as bursty review roles.

What persists SHALL be the judge-approved survivor queue, including ownership and verification state for downstream repair work.

#### Scenario: Contested bug review feeds a debugger lane

- **WHEN** adversarial bug review produces judge-approved survivors
- **THEN** the workflow SHALL persist those survivors as a repair queue
- **AND** it SHALL not require `bug-finder`, `bug-rebutter`, and `bug-judge` to remain default persistent workers

### Requirement: The LangGraph backend SHALL support interrupts and operator-driven resume

The durable orchestration backend SHALL support human approval points that interrupt execution and later resume it from persisted state.

At minimum the first rollout SHALL support interruptable approval points around:

- plan freeze
- risky stabilization decisions
- failed final verification
- loop verdicts that require human input

Interrupts SHALL preserve active loop metadata when the thread pauses at a gate.

Resume SHALL return to the same conditional graph path rather than flattening back to a one-pass wrapper.

#### Scenario: Plan-freeze or loop-gate approval pauses the graph

- **WHEN** the workflow reaches a plan-freeze approval point or a gate verdict that requires human input
- **THEN** the graph SHALL be able to interrupt and expose the pending state to the operator
- **AND** the operator SHALL be able to resume the same thread with the preserved loop metadata and conditional execution path

### Requirement: The LangGraph backend SHALL project inspectable thread state into the canonical durable-state surface
The LangGraph durable orchestration backend SHALL project repo-local thread state into the canonical inspectable durable-state surface.

At minimum the LangGraph projection SHALL make operator-facing state available for:

- stable thread identity
- current root-graph phase
- backend-record path
- interrupt or resume status
- checkpoint availability
- implementation-brief presence
- survivor-queue presence
- resume and inspect pointers

#### Scenario: Operator inspects a tracked LangGraph durable thread
- **WHEN** the current repository has a tracked LangGraph durable thread
- **THEN** the backend SHALL expose the data needed to populate the canonical inspectable durable-state summary
- **AND** it SHALL include LangGraph-specific projection fields for thread, phase, and resume-related state

### Requirement: The user-level LangGraph lane SHALL define explicit reducer-backed merge channels for fan-out and fan-in state

The user-level LangGraph durable lane SHALL define explicit reducer-backed state channels for branch outputs that are intended to merge across parallel fan-out and fan-in execution.

The contract SHALL distinguish reducer-merged channels from single-writer channels.

The system SHALL NOT silently treat arbitrary multi-writer state updates as mergeable.

#### Scenario: Parallel execution branches return mergeable findings

- **WHEN** multiple LangGraph execution branches complete with outputs for a declared reducer-merged channel
- **THEN** the durable lane SHALL merge those outputs through the declared reducer semantics
- **AND** it SHALL persist the merged result in repo-local LangGraph durable state

#### Scenario: Multiple branches write to a non-reducer field

- **WHEN** multiple LangGraph branches attempt to write the same field that is not declared as reducer-merged
- **THEN** the durable lane SHALL reject or surface that write as invalid multi-writer state
- **AND** it SHALL NOT silently resolve the conflict through implicit overwrite or append behavior

### Requirement: Reducer-backed fan-in state SHALL remain deterministic and resumable

Reducer-backed fan-in behavior SHALL be deterministic enough for checkpoint resume and equivalent branch-result reapplication to preserve the same durable state meaning.

Reducer-aware branch records SHALL therefore preserve stable item identity or equivalent dedup-safe semantics where append-like merging is used.

#### Scenario: Interrupted parallel flow resumes after partial branch completion

- **WHEN** a LangGraph thread resumes after some fan-out branches have already contributed reducer-backed results
- **THEN** the resumed flow SHALL preserve the already-merged branch contributions
- **AND** it SHALL continue fan-in without corrupting or duplicating the durable merged state

### Requirement: Leader-owned summary fields SHALL remain separate from reducer-merged branch channels

The durable lane SHALL keep leader-owned summary fields distinct from reducer-merged branch channels.

Fields that define top-level durable posture, identity, or accepted outcome SHALL remain single-writer unless explicitly reclassified by a later change.

#### Scenario: Branch fan-in completes before final leader convergence

- **WHEN** reducer-backed branch channels have been merged successfully
- **THEN** the durable lane MAY expose the merged branch state as intermediate durable state
- **AND** it SHALL NOT treat that merged branch state as the final accepted thread outcome until leader-owned convergence completes

### Requirement: The user-level LangGraph lane SHALL expose read-oriented replay and state-history inspection for tracked threads

The user-level LangGraph durable lane SHALL expose read-oriented replay, checkpoint-history inspection, and state-history inspection for tracked LangGraph threads.

At minimum the inspection surface SHALL be able to identify:

- the tracked thread identity
- available checkpoint or history targets
- the phase or lifecycle posture associated with each target
- the persisted source records used to derive the replay or history view
- the follow-up helper pointers for resume or explicit recovery

#### Scenario: Operator inspects checkpoint history for a tracked LangGraph thread

- **WHEN** the current repository has a tracked LangGraph durable thread with persisted checkpoint or state-history records
- **THEN** the durable lane SHALL expose those records through a read-oriented inspection surface
- **AND** it SHALL not mutate the tracked active thread state as part of that inspection

### Requirement: LangGraph replay SHALL remain distinct from recovery mutation

Replay or history inspection SHALL remain read-only by default.

The durable lane SHALL distinguish replaying or viewing prior state from mutating the tracked active thread state through recovery controls.

#### Scenario: Operator replays a prior checkpoint for analysis

- **WHEN** the operator requests replay or inspection of a prior LangGraph checkpoint
- **THEN** the durable lane SHALL expose the historical view or replay result as inspection output
- **AND** it SHALL not treat that replay action as an implicit rewind or state rewrite

### Requirement: LangGraph time-travel SHALL require an explicit recovery target

The user-level LangGraph durable lane SHALL support bounded time-travel only as an explicit recovery action against a stable checkpoint or state-history target.

#### Scenario: Operator time-travels a tracked LangGraph thread to a prior checkpoint

- **WHEN** the operator explicitly selects an eligible checkpoint or history target for recovery
- **THEN** the durable lane SHALL apply recovery against that explicit target
- **AND** it SHALL mark the resulting thread posture as recovered or equivalent rather than pretending no recovery occurred

### Requirement: Update-state-style recovery SHALL remain bounded and contract-preserving

The user-level LangGraph durable lane SHALL support explicit update-state-style recovery only within bounded recoverable-field classes that preserve the existing durable-state contract.

It SHALL NOT expose arbitrary raw state mutation as the default operator recovery path.

#### Scenario: Operator applies bounded state repair to a tracked LangGraph thread

- **WHEN** the operator requests explicit state repair for a recoverable LangGraph state field
- **THEN** the durable lane SHALL validate that the requested repair is in scope and contract-compatible
- **AND** it SHALL reject or surface out-of-scope, invalid, or reducer-breaking mutations explicitly

### Requirement: Replay and recovery SHALL preserve source attribution and recovery provenance

Replay and recovery surfaces SHALL preserve source attribution for the underlying state records and SHALL expose whether the current thread posture reflects historical replay, explicit recovery, or ordinary uninterrupted execution.

#### Scenario: Operator inspects a thread after time-travel recovery

- **WHEN** a tracked LangGraph thread has undergone explicit recovery
- **THEN** the durable lane SHALL expose source pointers and recovery provenance for the resulting thread posture
- **AND** it SHALL not collapse recovered state into an indistinguishable uninterrupted-active classification
