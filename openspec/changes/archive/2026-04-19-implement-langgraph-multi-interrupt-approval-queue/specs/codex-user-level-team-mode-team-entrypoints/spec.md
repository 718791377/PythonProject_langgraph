## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph approval-queue inspection entrypoint

When the user-level LangGraph lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph approval-queue inspection helper.

#### Scenario: Operator looks for multi-interrupt approval inspection

- **WHEN** the user-level installation includes the LangGraph durable lane
- **THEN** the generated entrypoint set SHALL include a LangGraph approval-queue inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
