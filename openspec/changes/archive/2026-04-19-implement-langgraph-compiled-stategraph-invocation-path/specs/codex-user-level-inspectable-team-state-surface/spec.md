## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project compiled-invocation posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread running through the live compiled invocation path, the canonical inspectable durable-state surface SHALL expose LangGraph-specific invocation projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- compiled invocation identity
- current live execution node or mapped phase posture
- bounded invocation transition posture
- the relevant compiled-invocation inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after the compiled invocation path lands

- **WHEN** the current repository has a tracked LangGraph thread running through the live compiled invocation path
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded compiled-invocation projection data
