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

### Requirement: The LangGraph backend SHALL expose reusable subgraph contracts as first-class durable library data

The user-level LangGraph backend SHALL expose reusable subgraph contracts as first-class durable library data instead of only a shallow role-family map.

At minimum each supported subgraph SHALL have:

- stable subgraph identity
- role-family membership
- role list
- default phase association
- input and output artifact expectations

#### Scenario: Operator inspects the backend contract for reusable subgraphs

- **WHEN** the operator inspects the LangGraph backend contract
- **THEN** the backend SHALL expose reusable subgraph contracts for the supported role families
- **AND** it SHALL not reduce those contracts to a bare list of role names only

### Requirement: The LangGraph backend SHALL persist active-subgraph identity for tracked threads

When a tracked LangGraph thread is operating inside a reusable subgraph-aware phase family, the backend SHALL persist active-subgraph identity and subgraph-aware posture in durable thread state.

#### Scenario: A tracked LangGraph thread is executing through the execution subgraph

- **WHEN** the tracked LangGraph thread is operating in an execution-family path
- **THEN** the backend SHALL persist the active subgraph identity
- **AND** it SHALL keep that identity inspectable across resume and later operator inspection

### Requirement: The LangGraph backend SHALL expose command-driven transition contracts for tracked threads

The user-level LangGraph backend SHALL expose explicit command-driven transition contracts for tracked threads instead of reducing all durable movement to implicit phase changes or gate verdicts only.

At minimum the command-driven contract SHALL be able to represent:

- state update intent
- local `goto` target
- graph target scope
- resume intent when present

#### Scenario: Operator inspects a command-driven local transition

- **WHEN** a tracked LangGraph thread records a command-driven transition within the current graph scope
- **THEN** the backend SHALL preserve the command-driven transition posture in durable thread or checkpoint state
- **AND** it SHALL keep that posture inspectable instead of collapsing it into an unqualified phase change only

### Requirement: The LangGraph backend SHALL support explicit parent-directed handoff posture across reusable subgraph boundaries

When a reusable subgraph exits through a parent-directed control-flow path, the backend SHALL preserve that handoff as explicit durable posture rather than treating it as an inferred side effect.

At minimum the backend SHALL be able to report:

- source subgraph identity
- target graph scope
- parent-handoff target when present

#### Scenario: Execution subgraph hands control back to the parent graph

- **WHEN** a tracked LangGraph thread reaches a parent-directed handoff from a reusable subgraph
- **THEN** the backend SHALL preserve the parent-handoff source and target posture in durable state
- **AND** it SHALL not treat that handoff as indistinguishable from an ordinary in-subgraph transition

### Requirement: The LangGraph backend SHALL preserve resume-payload posture for command-driven continuation

When command-driven continuation requires explicit resume intent, the backend SHALL preserve whether the tracked thread is awaiting resume input or has resumed with explicit command-driven continuation posture.

#### Scenario: Interrupted thread resumes through command-driven continuation

- **WHEN** a tracked LangGraph thread resumes from an interrupt with explicit continuation intent
- **THEN** the backend SHALL preserve that resume posture as command-aware durable state
- **AND** it SHALL keep resume metadata bounded and inspectable across later operator inspection

### Requirement: The LangGraph backend SHALL expose additive streaming and debug observability for tracked threads

The user-level LangGraph backend SHALL expose additive streaming and debug observability for tracked threads instead of limiting operator visibility to snapshot inspection only.

The first rollout SHALL support at minimum these operator-facing event modes:

- `updates` - LangGraph stream mode for progress updates.
- `checkpoints` - LangGraph stream mode for checkpoint activity.
- `tasks` - LangGraph stream mode for task execution events.
- `debug` - LangGraph stream mode for detailed debugging events.

#### Scenario: Operator streams task and checkpoint observability for a tracked thread

- **WHEN** the operator requests streaming observability for a tracked LangGraph thread
- **THEN** the backend SHALL expose the selected stream modes as additive observability behavior
- **AND** it SHALL not require the operator to replace existing snapshot inspection to use the stream surface

### Requirement: The LangGraph backend SHALL preserve nested subgraph visibility for stream observability

When streaming observability is enabled with nested subgraph visibility, the backend SHALL preserve that posture explicitly.

#### Scenario: Operator enables nested subgraph visibility for a streamed thread

- **WHEN** the operator requests stream observability with nested subgraph visibility
- **THEN** the backend SHALL preserve that posture in stream-session or equivalent bounded observability state
- **AND** it SHALL keep nested subgraph visibility distinguishable from root-only stream posture

### Requirement: The LangGraph backend SHALL project bounded latest-event stream posture for inspection

The backend SHALL project bounded latest-event stream posture for inspection without requiring a full persisted event log in the canonical durable-state summary.

At minimum that projection SHALL be able to report:

- selected stream modes
- whether nested subgraphs are included
- latest event kind
- latest checkpoint or task signal when present

#### Scenario: Operator inspects the latest bounded stream posture after a streamed execution step

- **WHEN** a tracked LangGraph thread has emitted streamed observability events
- **THEN** the backend SHALL preserve a bounded latest-event stream posture for later inspection
- **AND** it SHALL not overstate that bounded summary as a full stream-history replacement

### Requirement: The LangGraph backend SHALL expose runtime-context contracts for tracked threads

The user-level LangGraph backend SHALL expose runtime-context contracts for tracked threads aligned with `context_schema` and `Runtime.context`.

At minimum the runtime-context contract SHALL be able to represent:

- context-schema identity or equivalent schema posture
- bounded runtime-context key posture
- whether runtime context is present for the tracked thread

#### Scenario: Operator inspects runtime-context posture for a tracked thread

- **WHEN** a tracked LangGraph thread was started with runtime-context metadata
- **THEN** the backend SHALL preserve bounded runtime-context posture in durable state
- **AND** it SHALL keep runtime-context posture distinguishable from mutable graph state

### Requirement: The LangGraph backend SHALL expose injected-store posture for tracked threads

The user-level LangGraph backend SHALL expose injected-store posture for tracked threads aligned with `Runtime.store`.

At minimum the backend SHALL be able to report:

- whether an injected store is configured
- whether store access is expected to be available to nodes
- a bounded store-kind or store-posture classification

#### Scenario: Operator inspects injected-store posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured with injected store access
- **THEN** the backend SHALL preserve bounded store-injection posture in durable state
- **AND** it SHALL not overstate that posture as semantic-memory behavior by itself

### Requirement: The LangGraph backend SHALL expose graph-migration compatibility posture for tracked threads

The user-level LangGraph backend SHALL expose bounded graph-migration compatibility posture for tracked threads instead of assuming every persisted thread remains safely resumable under the latest graph contract.

At minimum the backend SHALL be able to report:

- current graph-contract identity
- tracked thread contract identity when present
- topology compatibility posture
- state-schema compatibility posture
- overall thread-compatibility verdict

#### Scenario: Operator inspects a tracked thread after the graph contract changed

- **WHEN** a tracked LangGraph thread was created under an older graph contract than the current backend contract
- **THEN** the backend SHALL preserve bounded migration and compatibility posture in durable state
- **AND** it SHALL not overstate that thread as fully resumable without compatibility classification

### Requirement: The LangGraph backend SHALL distinguish migration-safe, degraded-compatible, and incompatible thread posture

The user-level LangGraph backend SHALL distinguish at minimum:

- migration_safe
- degraded_compatible
- incompatible

#### Scenario: Operator inspects a degraded-compatible tracked thread

- **WHEN** a tracked LangGraph thread remains inspectable but not fully confidence-equivalent under the current graph contract
- **THEN** the backend SHALL classify that thread as degraded-compatible or equivalent
- **AND** it SHALL keep that posture distinct from both migration-safe and incompatible threads

### Requirement: The LangGraph backend SHALL expose multi-interrupt approval-queue posture for tracked threads

The user-level LangGraph backend SHALL expose bounded multi-interrupt approval-queue posture for tracked threads instead of collapsing every approval need into one generic interrupt record.

At minimum the backend SHALL be able to report:

- stable interrupt item identity
- queue ordering posture
- pending versus resolved item posture
- bounded resume-mapping posture when present

#### Scenario: Operator inspects a tracked thread with multiple pending interrupts

- **WHEN** a tracked LangGraph thread has surfaced multiple interrupt items in one invocation
- **THEN** the backend SHALL preserve ordered approval-queue posture in durable state
- **AND** it SHALL not collapse that state into one undifferentiated interrupt record

### Requirement: The LangGraph backend SHALL keep explicit resume mapping for multi-interrupt continuation

The user-level LangGraph backend SHALL keep explicit resume mapping for multi-interrupt continuation instead of treating later resume intent as queue-unaware thread state only.

#### Scenario: Operator resumes one item in a multi-interrupt queue

- **WHEN** the operator provides resume input for a tracked thread with multiple interrupt items
- **THEN** the backend SHALL preserve which interrupt item that resume input addresses
- **AND** it SHALL keep that resume mapping inspectable

### Requirement: The LangGraph backend SHALL expose a `StateGraph`-first runtime kernel for the user-level durable lane

The user-level LangGraph backend SHALL expose a `StateGraph`-first runtime kernel instead of remaining only a projection-first durable shell around repo-local state.

At minimum the backend SHALL be able to report:

- graph-kernel identity
- graph-native node or phase mapping
- graph-native edge or transition posture
- resumable kernel state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the graph-native kernel

- **WHEN** a tracked LangGraph thread is running under the graph-native runtime kernel
- **THEN** the backend SHALL preserve graph-native kernel posture in durable state
- **AND** it SHALL not reduce that state to shell-only summary posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being mapped into graph-native kernel state

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while mapping that shell into graph-native runtime state internally.

#### Scenario: Operator inspects graph-native kernel state through the existing phase model

- **WHEN** the graph-native kernel is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture maps into graph-native kernel state

### Requirement: The LangGraph backend SHALL expose a compiled `StateGraph` primary-runtime engine for the user-level durable lane

The user-level LangGraph backend SHALL expose a compiled `StateGraph` primary-runtime engine instead of keeping graph-native behavior only as a bounded kernel projection around a shell-first runtime.

At minimum the backend SHALL be able to report:

- primary-runtime engine identity
- compiled graph execution posture
- graph-native node or phase execution mapping
- resumable engine state for tracked threads

#### Scenario: Operator inspects a tracked thread running under the primary-runtime engine

- **WHEN** a tracked LangGraph thread is executing under the primary-runtime `StateGraph` engine
- **THEN** the backend SHALL preserve primary-runtime engine posture in durable state
- **AND** it SHALL not reduce that state to projection-only kernel posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being executed by the primary-runtime engine

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while executing that shell through the compiled primary-runtime engine.

#### Scenario: Operator inspects primary-runtime engine state through the existing phase model

- **WHEN** the compiled primary-runtime engine is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being executed by the primary-runtime engine

### Requirement: The LangGraph backend SHALL expose a live compiled `StateGraph` invocation path for the user-level durable lane

The user-level LangGraph backend SHALL expose a live compiled `StateGraph` invocation path instead of keeping graph-native execution only as a bounded primary-runtime posture.

At minimum the backend SHALL be able to report:

- compiled invocation identity
- live graph execution posture
- graph-native node or phase execution mapping
- resumable invocation state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the compiled invocation path

- **WHEN** a tracked LangGraph thread is executing through the live compiled `StateGraph` invocation path
- **THEN** the backend SHALL preserve compiled invocation posture in durable state
- **AND** it SHALL not reduce that state to engine-projection-only posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by the compiled invocation path

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the live compiled invocation path.

#### Scenario: Operator inspects compiled invocation state through the existing phase model

- **WHEN** the live compiled invocation path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the compiled invocation path

### Requirement: The LangGraph backend SHALL expose a live compiled `StateGraph` execution path for the user-level durable lane

The user-level LangGraph backend SHALL expose a live compiled `StateGraph` execution path instead of keeping compiled graph behavior only as a bounded invocation posture.

At minimum the backend SHALL be able to report:

- live-execution identity
- actual compiled graph execution posture
- graph-native node or phase execution mapping
- resumable live-execution state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the live compiled execution path

- **WHEN** a tracked LangGraph thread is executing through the live compiled `StateGraph` execution path
- **THEN** the backend SHALL preserve live-execution posture in durable state
- **AND** it SHALL not reduce that state to invocation-projection-only posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by the live compiled execution path

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the live compiled execution path.

#### Scenario: Operator inspects live execution state through the existing phase model

- **WHEN** the live compiled execution path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the live compiled execution path

### Requirement: The LangGraph backend SHALL expose durable memory-store posture for tracked threads

The user-level LangGraph backend SHALL expose durable memory-store posture for tracked threads on top of injected store capability.

At minimum the backend SHALL be able to report:

- whether durable memory store is configured
- memory store kind or bounded store posture
- memory namespace or bounded memory scope when present

#### Scenario: Operator inspects durable memory-store posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured to use a durable memory store
- **THEN** the backend SHALL preserve bounded memory-store posture in durable state
- **AND** it SHALL keep memory-store posture distinguishable from plain injected store availability

### Requirement: The LangGraph backend SHALL expose semantic-memory posture for tracked threads

The user-level LangGraph backend SHALL expose bounded semantic-memory posture for tracked threads without forcing one provider implementation.

At minimum the backend SHALL be able to report:

- whether semantic lookup is enabled
- semantic store kind or bounded semantic posture
- semantic namespace or bounded retrieval scope when present

#### Scenario: Operator inspects semantic-memory posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured for semantic lookup over durable memory
- **THEN** the backend SHALL preserve bounded semantic-memory posture in durable state
- **AND** it SHALL not overstate that posture as one provider-specific implementation by default

### Requirement: The LangGraph backend SHALL expose runtime-context contracts for tracked threads

The user-level LangGraph backend SHALL expose runtime-context contracts for tracked threads aligned with `context_schema` and `Runtime.context`.

At minimum the runtime-context contract SHALL be able to represent:

- context-schema identity or equivalent schema posture
- bounded runtime-context key posture
- whether runtime context is present for the tracked thread

#### Scenario: Operator inspects runtime-context posture for a tracked thread

- **WHEN** a tracked LangGraph thread was started with runtime-context metadata
- **THEN** the backend SHALL preserve bounded runtime-context posture in durable state
- **AND** it SHALL keep runtime-context posture distinguishable from mutable graph state

### Requirement: The LangGraph backend SHALL expose injected-store posture for tracked threads

The user-level LangGraph backend SHALL expose injected-store posture for tracked threads aligned with `Runtime.store`.

At minimum the backend SHALL be able to report:

- whether an injected store is configured
- whether store access is expected to be available to nodes
- a bounded store-kind or store-posture classification

#### Scenario: Operator inspects injected-store posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured with injected store access
- **THEN** the backend SHALL preserve bounded store-injection posture in durable state
- **AND** it SHALL not overstate that posture as semantic-memory behavior by itself

### Requirement: The LangGraph backend SHALL expose generalized live `StateGraph` routing for the user-level durable lane

The user-level LangGraph backend SHALL expose generalized live `StateGraph` routing instead of keeping live execution constrained to a narrowly bounded branch only.

At minimum the backend SHALL be able to report:

- generalized live-routing identity
- live loop posture beyond the current narrow branch
- graph-native route decisions across the seven-phase shell
- resumable generalized live-routing state for tracked threads

#### Scenario: Operator inspects a tracked thread running through generalized live routing

- **WHEN** a tracked LangGraph thread is executing through the generalized live-routing path
- **THEN** the backend SHALL preserve generalized live-routing posture in durable state
- **AND** it SHALL not reduce that state to a narrowly bounded branch posture only

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by generalized live routing

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the generalized live-routing model.

#### Scenario: Operator inspects generalized live routing through the existing phase model

- **WHEN** the generalized live-routing path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the generalized live-routing model

### Requirement: The LangGraph backend SHALL expose official subgraph persistence modes for reusable subgraphs

When the user-level LangGraph lane uses reusable subgraphs, the backend SHALL expose the official subgraph persistence-mode posture rather than only exposing active-subgraph identity.

At minimum the backend SHALL be able to report:

- per-invocation posture (`checkpointer=None`)
- per-thread posture (`checkpointer=True`)
- stateless posture (`checkpointer=False`)
- whether the active subgraph is inheriting parent checkpoint behavior, accumulating thread memory, or running without checkpointing

#### Scenario: Operator inspects a tracked thread using a reusable subgraph

- **WHEN** a tracked LangGraph thread is operating inside a reusable subgraph-aware phase family
- **THEN** the backend SHALL preserve the active subgraph persistence mode in durable state
- **AND** it SHALL not reduce that state to active-subgraph identity alone

### Requirement: The LangGraph backend SHALL expose bounded subgraph-state inspection posture and constraints

When a tracked LangGraph thread uses reusable subgraphs, the backend SHALL expose whether subgraph state inspection is available and why.

At minimum the backend SHALL be able to report:

- whether subgraph state inspection is available for the current subgraph posture
- whether static subgraph discoverability is satisfied
- whether checkpoint-backed state inspection is unavailable because the subgraph is stateless
- whether per-thread same-subgraph parallel calls are disallowed or otherwise conflict-prone

#### Scenario: Operator inspects subgraph-state availability

- **WHEN** the operator requests subgraph-state inspection for a tracked LangGraph thread
- **THEN** the backend SHALL expose bounded inspection availability and constraint posture
- **AND** it SHALL not imply that stateless or non-discoverable subgraphs have inspectable checkpoint state

### Requirement: The LangGraph backend SHALL expose a fuller live `StateGraph` primary execution engine for the user-level durable lane

The user-level LangGraph backend SHALL evolve beyond bounded live-execution posture and expose a fuller live `StateGraph` primary execution engine while preserving the current seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the fuller live engine

- **WHEN** a tracked LangGraph thread is executing through the fuller live primary engine
- **THEN** the backend SHALL preserve richer live execution posture in durable state
- **AND** it SHALL not collapse that state back into bounded live-execution posture only

### Requirement: The LangGraph backend SHALL expose bounded richer automatic runtime-policy posture for the user-level durable lane

The user-level LangGraph backend SHALL expose bounded automatic runtime-policy posture for concrete domains such as migration handling and approval or queue-resolution behavior.

#### Scenario: Operator inspects automatic runtime-policy posture for a tracked thread

- **WHEN** a tracked LangGraph thread is operating under the richer automatic-policy lane
- **THEN** the backend SHALL preserve bounded automatic-policy posture in durable state
- **AND** it SHALL not hide that posture behind uninspectable implicit behavior

### Requirement: The LangGraph backend SHALL expose deeper live primary-engine semantics beyond the current bounded posture

The user-level LangGraph backend SHALL deepen the current live primary-engine semantics beyond the current bounded posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the deeper live engine

- **WHEN** a tracked LangGraph thread is executing through the deeper live primary-engine lane
- **THEN** the backend SHALL preserve deeper live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously bounded primary-engine posture only

### Requirement: The LangGraph backend SHALL expose broader bounded automatic runtime-policy behavior for the user-level durable lane

The user-level LangGraph backend SHALL broaden the bounded automatic runtime-policy layer beyond the initial migration and resolved-queue posture while preserving manual-first control.

#### Scenario: Operator inspects broader automatic-policy posture for a tracked thread

- **WHEN** a tracked LangGraph thread is operating under the broader automatic-policy lane
- **THEN** the backend SHALL preserve broader bounded automatic-policy posture in durable state
- **AND** it SHALL not hide that posture behind uninspectable implicit behavior

### Requirement: The LangGraph backend SHALL expose a superstep-aware live primary-engine lane for the user-level durable lane

The user-level LangGraph backend SHALL expose a superstep-aware live primary-engine lane beyond the current deeper projected-path posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the superstep live engine

- **WHEN** a tracked LangGraph thread is executing through the superstep live primary-engine lane
- **THEN** the backend SHALL preserve superstep-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously deeper projected-path posture only

### Requirement: The LangGraph backend SHALL expose stateful live primary-engine semantics beyond the current superstep trace posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current prepared superstep trace posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the stateful live engine

- **WHEN** a tracked LangGraph thread is executing through the stateful live primary-engine lane
- **THEN** the backend SHALL preserve stateful live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously prepared superstep trace posture only

### Requirement: The LangGraph backend SHALL expose graph-resident live primary-engine boundary-state semantics beyond the current stateful transition posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current stateful transition posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the graph-resident boundary-state live engine

- **WHEN** a tracked LangGraph thread is executing through the graph-resident live primary-engine boundary-state lane
- **THEN** the backend SHALL preserve graph-resident live-engine boundary-state posture in durable state
- **AND** it SHALL not collapse that state back into the previously stateful transition posture only

### Requirement: The LangGraph backend SHALL expose subgraph-aware live primary-engine handoff-state semantics beyond the current graph-resident boundary-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current graph-resident boundary-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the subgraph-aware handoff-state live engine

- **WHEN** a tracked LangGraph thread is executing through the subgraph-aware live primary-engine handoff-state lane
- **THEN** the backend SHALL preserve subgraph-aware live-engine handoff posture in durable state
- **AND** it SHALL not collapse that state back into the previously graph-resident boundary-state posture only

### Requirement: The LangGraph backend SHALL expose approval-aware live primary-engine resume-state semantics beyond the current subgraph-aware handoff-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current subgraph-aware handoff-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the approval-aware resume-state live engine

- **WHEN** a tracked LangGraph thread is executing through the approval-aware live primary-engine resume-state lane
- **THEN** the backend SHALL preserve approval-aware live-engine resume posture in durable state
- **AND** it SHALL not collapse that state back into the previously subgraph-aware handoff-state posture only

### Requirement: The LangGraph backend SHALL expose recovery-aware live primary-engine provenance-state semantics beyond the current approval-aware resume-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current approval-aware resume-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the recovery-aware provenance-state live engine

- **WHEN** a tracked LangGraph thread is executing through the recovery-aware live primary-engine provenance-state lane
- **THEN** the backend SHALL preserve recovery-aware live-engine provenance posture in durable state
- **AND** it SHALL not collapse that state back into the previously approval-aware resume-state posture only

### Requirement: The LangGraph backend SHALL expose durable-artifact-aware live primary-engine semantics beyond the current recovery-aware provenance-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current recovery-aware provenance-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the durable-artifact-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the durable-artifact-aware live primary-engine lane
- **THEN** the backend SHALL preserve durable-artifact-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously recovery-aware provenance-state posture only

### Requirement: The LangGraph backend SHALL expose reducer-aware live primary-engine merge-state semantics beyond the current durable-artifact-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current durable-artifact-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the reducer-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the reducer-aware live primary-engine lane
- **THEN** the backend SHALL preserve reducer-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously durable-artifact-aware posture only

### Requirement: The LangGraph backend SHALL expose command-aware live primary-engine control-state semantics beyond the current reducer-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current reducer-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the command-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the command-aware live primary-engine lane
- **THEN** the backend SHALL preserve command-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously reducer-aware posture only

### Requirement: The LangGraph backend SHALL expose runtime-aware live primary-engine context-store semantics beyond the current command-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current command-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the runtime-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the runtime-aware live primary-engine lane
- **THEN** the backend SHALL preserve runtime-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously command-aware posture only

### Requirement: The LangGraph backend SHALL expose memory-aware live primary-engine semantic-state semantics beyond the current runtime-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current runtime-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the memory-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the memory-aware live primary-engine lane
- **THEN** the backend SHALL preserve memory-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously runtime-aware posture only

### Requirement: The LangGraph backend SHALL expose migration-aware live primary-engine compatibility-state semantics beyond the current memory-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current memory-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the migration-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the migration-aware live primary-engine lane
- **THEN** the backend SHALL preserve migration-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously memory-aware posture only

### Requirement: The LangGraph backend SHALL persist explicit thread release receipts

The LangGraph durable backend SHALL provide a repo-local helper that closes, releases, or hands off a tracked LangGraph thread and persists a release receipt under `.omx/state/langgraph/store/releases/`.

The receipt SHALL record at least:

- `thread_id`, which identifies the released LangGraph thread.
- `backend_family`, which remains `langgraph` for this helper.
- `previous_state`, meaning a full snapshot of the thread record before release, and `previous_status`, meaning the pre-release value of the thread `status` field; together they preserve the pre-release posture.
- `release_action`, which is one of `close`, `release`, or `handoff`.
- `survivor_queue_path` and `survivor_queue_status`, which identify persisted survivor state.
- `handoff_target`, which is required for backend-family handoff.
- `checkpoint_path` and `artifact_path`, which point to repo-local recovery evidence.
- `timeout_release`, which records whether the release followed a timeout.
- `rollback_restore_note`, which records recovery guidance without automatically rewriting state.
- `redaction_status`, which records whether the receipt is safe for operator-visible evidence.

#### Scenario: Operator closes a completed tracked thread

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=close`
- **THEN** the backend SHALL write a release receipt under `.omx/state/langgraph/store/releases/`
- **AND** the thread state SHALL no longer report `status=running`
- **AND** status and inspect output SHALL expose the release receipt path and release projection

#### Scenario: Operator hands off a thread to another backend family

- **WHEN** the operator runs the LangGraph thread release helper with `release_action=handoff`
- **THEN** the backend SHALL require `handoff_target` and `reason`
- **AND** the persisted thread state SHALL record `handoff_at`, `handoff_target`, and `reason`
- **AND** the handoff SHALL NOT implicitly start or switch to the target backend family

