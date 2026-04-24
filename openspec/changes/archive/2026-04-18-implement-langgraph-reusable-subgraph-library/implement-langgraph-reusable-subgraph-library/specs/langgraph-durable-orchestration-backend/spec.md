## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose reusable subgraph contracts as first-class durable library data

The user-level LangGraph backend SHALL expose reusable subgraph contracts as first-class durable library data instead of only a shallow role-family map.

At minimum each supported subgraph SHALL have:

- stable subgraph identity
- role-family membership
- role list
- default phase association
- input and output artifact expectations

#### Scenario: Operator inspects the backend contract for reusable subgraphs

- **WHEN** the operator inspects the LangGraph backend contract
- **THEN** the backend SHALL expose reusable subgraph contracts for the supported role families
- **AND** it SHALL not reduce those contracts to a bare list of role names only

### Requirement: The LangGraph backend SHALL persist active-subgraph identity for tracked threads

When a tracked LangGraph thread is operating inside a reusable subgraph-aware phase family, the backend SHALL persist active-subgraph identity and subgraph-aware posture in durable thread state.

#### Scenario: A tracked LangGraph thread is executing through the execution subgraph

- **WHEN** the tracked LangGraph thread is operating in an execution-family path
- **THEN** the backend SHALL persist the active subgraph identity
- **AND** it SHALL keep that identity inspectable across resume and later operator inspection
