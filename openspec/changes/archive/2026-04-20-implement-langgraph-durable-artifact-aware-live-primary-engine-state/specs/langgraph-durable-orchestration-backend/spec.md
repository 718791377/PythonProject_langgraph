## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose durable-artifact-aware live primary-engine semantics beyond the current recovery-aware provenance-state posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current recovery-aware provenance-state posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the durable-artifact-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the durable-artifact-aware live primary-engine lane
- **THEN** the backend SHALL preserve durable-artifact-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously recovery-aware provenance-state posture only
