## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive durable-artifact-aware live-engine inspection entrypoint

When the user-level LangGraph durable-artifact-aware lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph durable-artifact-aware live-engine inspection helper.

#### Scenario: Operator looks for durable-artifact-aware live-engine inspection

- **WHEN** the user-level installation includes the LangGraph durable-artifact-aware lane
- **THEN** the generated entrypoint set SHALL include a LangGraph durable-artifact-aware live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, provenance-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
