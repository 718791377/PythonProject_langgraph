## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose runtime-aware live primary-engine context-store semantics beyond the current command-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current command-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the runtime-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the runtime-aware live primary-engine lane
- **THEN** the backend SHALL preserve runtime-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously command-aware posture only
