## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive deeper live-engine inspection entrypoint

When the user-level LangGraph deeper live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph deeper live-engine inspection helper.

#### Scenario: Operator looks for deeper live-engine inspection

- **WHEN** the user-level installation includes the LangGraph deeper live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph deeper live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
