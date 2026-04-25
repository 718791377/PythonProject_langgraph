## ADDED Requirements

### Requirement: The user-level installation SHALL expose an additive LangGraph primary-runtime inspection entrypoint

When the user-level LangGraph primary-runtime engine lane is installed, the generated user-level entrypoint set SHALL expose an additive LangGraph primary-runtime inspection helper.

#### Scenario: Operator looks for compiled graph-engine inspection

- **WHEN** the user-level installation includes the LangGraph primary-runtime engine lane
- **THEN** the generated entrypoint set SHALL include a LangGraph primary-runtime inspection helper
- **AND** that helper SHALL remain additive to the existing LangGraph run, status, inspect, kernel, approval-queue, migration, memory, runtime, stream, subgraphs, history, replay, recovery, and resume surfaces
