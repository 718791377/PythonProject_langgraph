## ADDED Requirements

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
