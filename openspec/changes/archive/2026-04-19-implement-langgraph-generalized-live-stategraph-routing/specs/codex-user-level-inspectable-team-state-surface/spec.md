## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project generalized live-routing posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread running through generalized live routing, the canonical inspectable durable-state surface SHALL expose LangGraph-specific generalized-routing projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- generalized live-routing identity
- current generalized live execution node or mapped phase posture
- bounded route or loop posture
- the relevant generalized live-routing inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after generalized live routing lands

- **WHEN** the current repository has a tracked LangGraph thread running through generalized live routing
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded generalized live-routing projection data
