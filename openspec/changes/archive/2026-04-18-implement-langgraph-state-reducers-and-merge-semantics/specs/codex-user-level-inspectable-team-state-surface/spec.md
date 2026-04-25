## ADDED Requirements

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
