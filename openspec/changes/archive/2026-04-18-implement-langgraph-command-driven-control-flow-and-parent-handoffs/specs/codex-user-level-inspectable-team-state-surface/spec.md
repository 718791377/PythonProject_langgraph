## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project command-driven transition and parent-handoff posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread using command-driven control flow, the canonical inspectable durable-state surface SHALL expose LangGraph-specific command-driven transition and parent-handoff projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- command-driven transition kind when present
- source and target subgraph identity when present
- local versus parent graph target scope
- the relevant command-aware inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread with parent-handoff posture

- **WHEN** the current repository has a tracked LangGraph thread with parent-directed handoff metadata
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include command-driven transition and parent-handoff projection data

### Requirement: The canonical durable-state surface SHALL classify command-driven resume posture explicitly

The inspectable durable-state surface SHALL distinguish ordinary resume posture from command-aware resume posture when the tracked LangGraph thread is waiting for or has consumed explicit continuation intent.

#### Scenario: Operator inspects a tracked LangGraph thread that is waiting for command-aware resume

- **WHEN** the current repository has a tracked LangGraph thread paused at a command-aware continuation point
- **THEN** the canonical inspectable durable-state surface SHALL classify that resume posture explicitly
- **AND** it SHALL not collapse that posture into an undifferentiated generic resume-ready state
