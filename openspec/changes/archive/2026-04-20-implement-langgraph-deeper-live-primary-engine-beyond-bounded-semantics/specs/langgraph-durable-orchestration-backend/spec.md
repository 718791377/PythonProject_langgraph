## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose deeper live primary-engine semantics beyond the current bounded posture

The user-level LangGraph backend SHALL deepen the current live primary-engine semantics beyond the current bounded posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the deeper live engine

- **WHEN** a tracked LangGraph thread is executing through the deeper live primary-engine lane
- **THEN** the backend SHALL preserve deeper live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously bounded primary-engine posture only
