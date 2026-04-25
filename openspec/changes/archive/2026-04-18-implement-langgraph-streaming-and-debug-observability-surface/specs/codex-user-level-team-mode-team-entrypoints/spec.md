## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph stream-observability entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph stream-observability helper.

#### Scenario: Operator looks for LangGraph streaming and debug observability

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph stream-observability helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, subgraphs, history, replay, recovery, and resume surfaces
