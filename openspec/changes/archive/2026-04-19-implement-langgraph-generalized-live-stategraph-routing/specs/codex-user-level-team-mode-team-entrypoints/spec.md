## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph generalized live-routing inspection entrypoint

When the user-level LangGraph generalized live-routing lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph generalized live-routing inspection helper.

#### Scenario: Operator looks for generalized live-routing inspection

- **WHEN** the user-level installation includes the LangGraph generalized live-routing lane
- **THEN** the generated entrypoint set SHALL include a LangGraph generalized live-routing inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
