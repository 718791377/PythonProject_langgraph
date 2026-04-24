## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project primary-runtime engine posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread running under the compiled primary-runtime engine, the canonical inspectable durable-state surface SHALL expose LangGraph-specific engine projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- primary-runtime engine identity
- current engine execution node or mapped phase posture
- bounded engine transition posture
- the relevant primary-runtime inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after the primary-runtime engine lands

- **WHEN** the current repository has a tracked LangGraph thread running under the compiled primary-runtime engine
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded primary-runtime engine projection data
