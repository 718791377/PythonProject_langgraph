## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose a fuller live `StateGraph` primary execution engine for the user-level durable lane

The user-level LangGraph backend SHALL evolve beyond bounded live-execution posture and expose a fuller live `StateGraph` primary execution engine while preserving the current seven-phase operator shell.

#### Scenario: Operator inspects a tracked thread using the fuller live engine

- **WHEN** a tracked LangGraph thread is executing through the fuller live primary engine
- **THEN** the backend SHALL preserve richer live execution posture in durable state
- **AND** it SHALL not collapse that state back into bounded live-execution posture only
