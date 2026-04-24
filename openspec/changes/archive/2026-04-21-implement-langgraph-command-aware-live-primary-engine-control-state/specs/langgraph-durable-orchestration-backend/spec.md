## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose command-aware live primary-engine control-state semantics beyond the current reducer-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current reducer-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the command-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the command-aware live primary-engine lane
- **THEN** the backend SHALL preserve command-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously reducer-aware posture only
