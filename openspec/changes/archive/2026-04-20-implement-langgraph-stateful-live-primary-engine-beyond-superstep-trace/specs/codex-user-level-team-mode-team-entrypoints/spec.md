## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive stateful live-engine inspection entrypoint

When the user-level LangGraph stateful live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph stateful live-engine inspection helper.

#### Scenario: Operator looks for stateful live-engine inspection

- **WHEN** the user-level installation includes the LangGraph stateful live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph stateful live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
