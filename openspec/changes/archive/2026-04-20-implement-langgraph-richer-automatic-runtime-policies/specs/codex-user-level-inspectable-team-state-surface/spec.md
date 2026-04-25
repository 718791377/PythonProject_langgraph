## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project automatic runtime-policy posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread using bounded richer automatic runtime-policy behavior, the canonical inspectable durable-state surface SHALL expose LangGraph-specific automatic-policy projection data without changing the shared cross-backend summary contract.

#### Scenario: Operator inspects a tracked LangGraph thread after automatic runtime-policy support lands

- **WHEN** the current repository has a tracked LangGraph durable thread using the automatic runtime-policy lane
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded automatic runtime-policy projection data
