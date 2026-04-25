## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph migration/compatibility inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph migration/compatibility inspection helper.

#### Scenario: Operator looks for graph-migration and thread-compatibility inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph migration/compatibility inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
