## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project LangGraph subgraph persistence-mode posture

When the current repository has a tracked LangGraph durable thread using reusable subgraphs, the canonical inspectable durable-state surface SHALL expose LangGraph-specific subgraph persistence-mode projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- active subgraph persistence mode
- whether the active subgraph is inheriting the parent checkpointer, persisting across the thread, or stateless
- whether subgraph-state inspection is available
- the relevant subgraph-state inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after subgraph persistence modes land

- **WHEN** the current repository has a tracked LangGraph thread using reusable subgraphs
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded subgraph persistence-mode and inspection projection data
