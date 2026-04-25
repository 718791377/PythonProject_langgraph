## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive subgraph-aware live-engine handoff-state inspection entrypoint

When the user-level LangGraph subgraph-aware handoff-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph subgraph-aware live-engine handoff-state inspection helper.

#### Scenario: Operator looks for subgraph-aware live-engine handoff-state inspection

- **WHEN** the user-level installation includes the LangGraph subgraph-aware handoff-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph subgraph-aware live-engine handoff-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
