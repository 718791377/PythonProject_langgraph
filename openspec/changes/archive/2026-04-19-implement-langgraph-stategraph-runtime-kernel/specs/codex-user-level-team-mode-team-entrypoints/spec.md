## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph graph-kernel inspection entrypoint

When the user-level LangGraph runtime-kernel lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph graph-kernel inspection helper.

#### Scenario: Operator looks for graph-native runtime-kernel inspection

- **WHEN** the user-level installation includes the LangGraph runtime-kernel lane
- **THEN** the generated entrypoint set SHALL include a LangGraph graph-kernel inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
