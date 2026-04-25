## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose migration-aware live primary-engine compatibility-state semantics beyond the current memory-aware posture

The user-level LangGraph backend SHALL deepen the current live primary-engine beyond the current memory-aware posture while preserving the seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the migration-aware live engine

- **WHEN** a tracked LangGraph thread is executing through the migration-aware live primary-engine lane
- **THEN** the backend SHALL preserve migration-aware live-engine posture in durable state
- **AND** it SHALL not collapse that state back into the previously memory-aware posture only
