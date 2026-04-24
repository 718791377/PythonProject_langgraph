## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph subgraph-library inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-library inspection entrypoint.

#### Scenario: Operator looks for available reusable LangGraph subgraphs

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-library inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, history, replay, recovery, and resume surfaces
