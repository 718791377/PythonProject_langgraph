# codex-user-level-inspectable-team-state-surface Specification

## Purpose

Define a canonical user-level operator-facing surface for inspecting durable orchestration state across repo-local `native_omx` and `langgraph` backends.

## Requirements

### Requirement: The user-level installation SHALL expose a canonical inspectable durable-state summary
The user-level orchestration layer SHALL expose one canonical inspectable durable-state summary for the current repository or worktree.

That summary SHALL remain read-oriented by default and SHALL answer at minimum:

- which durable backend family is currently represented
- which tracked identity is currently represented
- which current phase or lifecycle state is known
- which worker shape is known
- which active blockers are known
- which next step is known
- which inspect or resume pointers are relevant

#### Scenario: Operator inspects a repository with tracked native durable-team state
- **WHEN** the current repository has tracked native durable-team state
- **THEN** the inspectable surface SHALL expose a canonical summary for that state
- **AND** the summary SHALL include the backend family, tracked team identity, current worker shape, and relevant inspect or resume pointers

### Requirement: The inspectable summary SHALL normalize cross-backend durable-state fields
The canonical inspectable durable-state summary SHALL use one shared field set across `native_omx` and `langgraph`, while still allowing backend-specific projection fields.

At minimum the shared summary SHALL include:

- `backend_family`
- `state_class`
- `repo_root`
- `tracked_identity`
- `current_phase`
- `worker_shape`
- `active_blockers`
- `next_step`
- `inspect_pointer`
- `resume_pointer`
- `state_sources`
- `updated_at`

#### Scenario: Operator inspects a repository with a tracked LangGraph thread
- **WHEN** the current repository has a tracked LangGraph durable thread
- **THEN** the inspectable surface SHALL still use the shared summary field set
- **AND** it SHALL include LangGraph-specific projection data without changing the shared field contract

### Requirement: The inspectable summary SHALL classify stale, missing, and unmanaged durable state explicitly
The canonical inspectable durable-state summary SHALL classify the current durable-state situation explicitly instead of leaving it implicit in raw files or wrapper output.

At minimum it SHALL distinguish among:

- no durable state
- tracked native team
- tracked LangGraph thread
- stale tracked record
- unmanaged durable state detected

#### Scenario: Tracked record is present but the tracked native team directory is missing
- **WHEN** a tracked durable-team record exists but the referenced team state no longer exists in the current repository state root
- **THEN** the inspectable summary SHALL classify the situation as stale tracked state
- **AND** it SHALL not present that state as an active tracked durable team

### Requirement: The inspectable summary SHALL remain read-only and source-attributed
The inspectable durable-state surface SHALL remain read-oriented by default.

It SHALL expose which repo-local files, tracked records, or backend-specific inspection sources were used to derive the summary.

It MAY include follow-up pointers to existing mutation helpers, but it SHALL NOT itself require a new mutation plane.

#### Scenario: Operator requests inspectable state before deciding whether to resume or mutate
- **WHEN** the operator inspects durable state before choosing a next action
- **THEN** the surface SHALL report the source paths or source records used for the summary
- **AND** it SHALL preserve inspection as a read-only action while pointing later mutation to explicit existing helpers

### Requirement: The inspectable summary SHALL expose cleanup and reconciliation classification
The canonical inspectable durable-state summary SHALL expose enough classification to drive cleanup and reconciliation decisions without turning inspection itself into a mutation action.

At minimum it SHALL indicate:

- whether residue is a safe cleanup candidate
- whether residue requires manual reconciliation
- whether the current state should be treated as protected

It MAY do this through cleanup-class fields, active blockers, or equivalent operator-facing classification, but the classification SHALL be explicit.

#### Scenario: Tracked backend coexists with unmanaged residue
- **WHEN** a tracked durable backend exists and unmanaged residue from another backend is also present
- **THEN** the inspectable summary SHALL surface that residue as an explicit risk or reconciliation signal
- **AND** it SHALL not leave the operator to infer the conflict only from backend-specific detail sections

### Requirement: The inspectable durable-state surface SHALL project tracked compose runtime state when present

When repo-local tracked compose runtime state exists, the canonical inspectable durable-state surface SHALL project that state explicitly instead of leaving compose launch outcome visible only in backend-specific or compose-only files.

That projection SHALL preserve the shared durable-state contract while also exposing compose-specific launch detail as projection data.

#### Scenario: Operator inspects a repository with tracked compose runtime state

- **WHEN** the current repository has tracked compose runtime state for an applied advanced compose manifest
- **THEN** the inspectable surface SHALL expose the shared summary fields for the represented durable state
- **AND** it SHALL also expose compose-specific projection detail for launched panes, planned-only panes, and tracked identities

### Requirement: The canonical inspectable durable-state surface SHALL expose compose lifecycle helper pointers when compose runtime is tracked

When tracked compose runtime state exists, the canonical inspectable durable-state surface SHALL expose compose lifecycle helper pointers in addition to the shared summary fields.

#### Scenario: Operator inspects tracked compose runtime through the canonical durable-state surface

- **WHEN** the current repository has tracked compose runtime state
- **THEN** the canonical inspectable durable-state surface SHALL expose helper pointers for compose inspect, shutdown, or reconcile follow-up actions
- **AND** it SHALL not force the operator to discover compose lifecycle actions only from external documentation

### Requirement: The canonical durable-state surface SHALL expose partial compose lifecycle state and await pointers

When tracked compose runtime is only partially healthy or partially shut down, the canonical inspectable durable-state surface SHALL expose that partial state explicitly and SHALL provide compose await or related helper pointers.

#### Scenario: Operator inspects partially shut down compose runtime through the canonical summary

- **WHEN** the current repository has tracked compose runtime with only some launched pane teams still present
- **THEN** the canonical durable-state surface SHALL expose a partial compose lifecycle signal
- **AND** it SHALL include an await or equivalent compose helper pointer for follow-up inspection

### Requirement: The canonical durable-state surface SHALL expose compose recovery posture and resume helper pointers

When tracked compose runtime exists, the canonical durable-state surface SHALL expose compose recovery posture and compose recovery or resume helper pointers.

#### Scenario: Operator inspects tracked compose runtime recovery posture through the canonical summary

- **WHEN** the current repository has tracked compose runtime with mixed pane recovery eligibility
- **THEN** the canonical durable-state surface SHALL expose compose recovery posture explicitly
- **AND** it SHALL include a compose recovery or resume helper pointer for follow-up action

### Requirement: The canonical durable-state surface SHALL project LangGraph loop progress explicitly

When the current repository has a tracked LangGraph durable thread inside a quality-gated loop, the canonical inspectable durable-state surface SHALL expose LangGraph-specific loop projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- `active_loop`
- `iteration_count`
- `iteration_budget`
- `last_gate_verdict`
- `last_gate_reason`
- `stop_reason`

#### Scenario: Operator inspects a looping LangGraph thread

- **WHEN** the current repository has a tracked LangGraph thread inside a quality-gated loop
- **THEN** the canonical summary SHALL expose the shared durable-state fields
- **AND** it SHALL include LangGraph loop-progress and gate-result projection data for operator inspection

### Requirement: The canonical durable-state surface SHALL project reducer-aware LangGraph merge status

When the current repository has a tracked LangGraph durable thread using reducer-backed fan-out and fan-in state, the canonical inspectable durable-state surface SHALL expose reducer-aware projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- whether reducer-backed merge channels are present
- whether parallel branch fan-out is active, partial, or complete
- whether invalid multi-writer updates were detected
- which source records contributed to the merged state

#### Scenario: Operator inspects a reducer-aware LangGraph thread

- **WHEN** the current repository has a tracked LangGraph thread with reducer-backed branch merges
- **THEN** the canonical summary SHALL expose the shared durable-state fields
- **AND** it SHALL include LangGraph-specific reducer merge status and source-attribution projection data

### Requirement: The canonical durable-state surface SHALL classify pre-reducer LangGraph records explicitly

The inspectable durable-state surface SHALL distinguish reducer-aware LangGraph thread records from older pre-reducer records when merge guarantees are not equivalent.

#### Scenario: Operator inspects an older LangGraph thread without reducer metadata

- **WHEN** the current repository has a tracked LangGraph durable thread created before reducer-aware merge semantics were introduced
- **THEN** the inspectable surface SHALL classify that thread as pre-reducer or equivalent
- **AND** it SHALL NOT imply that reducer-backed merge guarantees are available for that record

### Requirement: The canonical durable-state surface SHALL project LangGraph replay and recovery posture

When the current repository has a tracked LangGraph durable thread with replay or history metadata or explicit recovery posture, the canonical inspectable durable-state surface SHALL expose LangGraph-specific replay and recovery projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- whether replay or history targets are available
- whether the current thread reflects ordinary active state, historical replay context, or explicit recovery posture
- which replay or recovery helper pointers are relevant
- which source records back the inspection result

#### Scenario: Operator inspects a recoverable LangGraph thread

- **WHEN** the current repository has a tracked LangGraph thread with history or recovery metadata
- **THEN** the canonical summary SHALL expose the shared durable-state fields
- **AND** it SHALL include LangGraph-specific replay or recovery status and helper-pointer projection data

### Requirement: The canonical durable-state surface SHALL distinguish read-only inspection from explicit mutation helpers

The inspectable durable-state surface SHALL remain read-oriented by default while pointing mutation to explicit replay or recovery helper surfaces.

#### Scenario: Operator inspects LangGraph durable state before deciding whether to recover

- **WHEN** the operator requests canonical durable-state inspection for a tracked LangGraph thread
- **THEN** the surface SHALL expose replay and history pointers together with explicit recovery helper pointers
- **AND** it SHALL not perform replay, time-travel, or state mutation implicitly
