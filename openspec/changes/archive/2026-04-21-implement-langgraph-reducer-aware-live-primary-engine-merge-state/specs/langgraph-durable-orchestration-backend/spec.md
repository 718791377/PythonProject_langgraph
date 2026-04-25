## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose reducer-aware live primary-engine merge-state semantics beyond the current durable-artifact-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current durable-artifact-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the reducer-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the reducer-aware live primary-engine lane
- **THEN** the backend SHALL preserve reducer-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously durable-artifact-aware posture only
