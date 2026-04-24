## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive automatic runtime-policy inspection entrypoint

When the user-level LangGraph richer automatic runtime-policy lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph automatic runtime-policy inspection helper.

#### Scenario: Operator looks for automatic runtime-policy inspection

- **WHEN** the user-level installation includes the LangGraph automatic runtime-policy lane
- **THEN** the generated entrypoint set SHALL include a LangGraph automatic runtime-policy inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, generalized-routing, subgraph-state, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
