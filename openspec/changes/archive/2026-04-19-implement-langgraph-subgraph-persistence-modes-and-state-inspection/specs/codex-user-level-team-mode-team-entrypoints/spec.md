## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph subgraph-state inspection entrypoint

When the user-level LangGraph subgraph persistence-mode lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-state inspection helper.

#### Scenario: Operator looks for subgraph-state inspection

- **WHEN** the user-level installation includes the LangGraph subgraph persistence-mode lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, subgraphs, kernel, engine, invocation, live-execution, generalized-routing, approval-queue, migration, memory, runtime, stream, history, replay, recovery, and resume surfaces
