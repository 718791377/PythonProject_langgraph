## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive fuller live-engine inspection entrypoint

When the user-level LangGraph fuller live-engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph fuller live-engine inspection helper.

#### Scenario: Operator looks for fuller live-engine inspection

- **WHEN** the user-level installation includes the LangGraph fuller live-engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph fuller live-engine inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, live-execution, generalized-routing, subgraph-state, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
