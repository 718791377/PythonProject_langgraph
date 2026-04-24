## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph live-execution inspection entrypoint

When the user-level LangGraph live-execution lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph live-execution inspection helper.

#### Scenario: Operator looks for live compiled execution inspection

- **WHEN** the user-level installation includes the LangGraph live-execution lane
- **THEN** the generated entrypoint set SHALL include a LangGraph live-execution inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, engine, invocation, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
