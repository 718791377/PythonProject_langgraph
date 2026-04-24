## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive graph-resident live-engine boundary-state inspection entrypoint

When the user-level LangGraph graph-resident boundary-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph graph-resident live-engine boundary-state inspection helper.

#### Scenario: Operator looks for graph-resident live-engine boundary-state inspection

- **WHEN** the user-level installation includes the LangGraph graph-resident boundary-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph graph-resident live-engine boundary-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
