## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph runtime/store inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph runtime/store inspection helper.

#### Scenario: Operator looks for runtime-context and store-injection inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph runtime/store inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, stream, subgraphs, history, replay, recovery, and resume surfaces
