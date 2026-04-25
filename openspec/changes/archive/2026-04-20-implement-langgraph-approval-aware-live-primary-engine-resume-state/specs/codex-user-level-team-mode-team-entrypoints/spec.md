## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive approval-aware live-engine resume-state inspection entrypoint

When the user-level LangGraph approval-aware resume-state lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph approval-aware live-engine resume-state inspection helper.

#### Scenario: Operator looks for approval-aware live-engine resume-state inspection

- **WHEN** the user-level installation includes the LangGraph approval-aware resume-state lane
- **THEN** the generated entrypoint set SHALL include a LangGraph approval-aware live-engine resume-state inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, fuller-engine, deeper-engine, superstep-engine, stateful-engine, boundary-engine, handoff-engine, auto-policy, subgraph-state, generalized-routing, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
