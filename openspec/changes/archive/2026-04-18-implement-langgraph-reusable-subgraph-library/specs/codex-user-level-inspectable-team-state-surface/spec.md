## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project active-subgraph and reusable subgraph-library data for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread using reusable subgraph contracts, the canonical inspectable durable-state surface SHALL expose LangGraph-specific active-subgraph and subgraph-library projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- active subgraph identity when present
- available reusable subgraphs
- the relevant subgraph-library inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread with subgraph-aware state

- **WHEN** the current repository has a tracked LangGraph thread with active-subgraph metadata
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include active-subgraph and reusable-subgraph-library projection data
