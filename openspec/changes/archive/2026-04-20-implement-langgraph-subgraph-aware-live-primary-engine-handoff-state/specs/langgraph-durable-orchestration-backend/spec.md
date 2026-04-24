## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose subgraph-aware live primary-engine handoff-state semantics beyond the current graph-resident boundary-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current graph-resident boundary-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the subgraph-aware handoff-state live engine

- **WHEN** a tracked LangGraph thread is executing through the subgraph-aware live primary-engine handoff-state lane
- **THEN** the backend SHALL preserve subgraph-aware live-engine handoff posture in durable state
- **AND** it SHALL not collapse that state back into the previously graph-resident boundary-state posture only
