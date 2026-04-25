## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph compiled-invocation inspection entrypoint

When the user-level LangGraph compiled-invocation lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph compiled-invocation inspection helper.

#### Scenario: Operator looks for live compiled graph inspection

- **WHEN** the user-level installation includes the LangGraph compiled-invocation lane
- **THEN** the generated entrypoint set SHALL include a LangGraph compiled-invocation inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
