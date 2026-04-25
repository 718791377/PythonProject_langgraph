## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project graph-migration and thread-compatibility posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread with migration or compatibility metadata, the canonical inspectable durable-state surface SHALL expose LangGraph-specific migration and compatibility projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- current graph-contract identity
- tracked thread contract identity when present
- compatibility verdict
- bounded migration reason codes when present
- the relevant migration/compatibility inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after a graph migration

- **WHEN** the current repository has a tracked LangGraph thread whose compatibility must be evaluated against the current graph contract
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded migration and compatibility projection data
