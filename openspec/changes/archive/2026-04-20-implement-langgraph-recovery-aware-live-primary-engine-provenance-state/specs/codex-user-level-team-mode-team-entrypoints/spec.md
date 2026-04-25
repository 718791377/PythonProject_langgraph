## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive recovery-aware live-engine provenance-state inspection entrypoint

When the user-level LangGraph recovery-aware provenance-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph recovery-aware live-engine provenance-state inspection helper.

#### Scenario: Operator looks for recovery-aware live-engine provenance-state inspection

- **WHEN** the user-level installation includes the LangGraph recovery-aware provenance-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph recovery-aware live-engine provenance-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, approval-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
