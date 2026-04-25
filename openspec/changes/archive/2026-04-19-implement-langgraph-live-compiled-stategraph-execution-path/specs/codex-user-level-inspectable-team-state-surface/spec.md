## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project live-execution posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread running through the live compiled execution path, the canonical inspectable durable-state surface SHALL expose LangGraph-specific live-execution projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- live-execution identity
- current live execution node or mapped phase posture
- bounded live-execution transition posture
- the relevant live-execution inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after the live execution path lands

- **WHEN** the current repository has a tracked LangGraph thread running through the live compiled execution path
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded live-execution projection data
