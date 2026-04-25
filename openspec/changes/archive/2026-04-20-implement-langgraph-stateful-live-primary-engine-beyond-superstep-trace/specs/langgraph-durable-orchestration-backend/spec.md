## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose stateful live primary-engine semantics beyond the current superstep trace posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current prepared superstep trace posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the stateful live engine

- **WHEN** a tracked LangGraph thread is executing through the stateful live primary-engine lane
- **THEN** the backend SHALL preserve stateful live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously prepared superstep trace posture only
