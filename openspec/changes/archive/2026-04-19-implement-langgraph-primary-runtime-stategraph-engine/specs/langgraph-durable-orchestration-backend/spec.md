## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose a compiled `StateGraph` primary-runtime engine for the user-level durable lane

The user-level LangGraph backend SHALL expose a compiled `StateGraph` primary-runtime engine instead of keeping graph-native behavior only as a bounded kernel projection around a shell-first runtime.

At minimum the backend SHALL be able to report:

- primary-runtime engine identity
- compiled graph execution posture
- graph-native node or phase execution mapping
- resumable engine state for tracked threads

#### Scenario: Operator inspects a tracked thread running under the primary-runtime engine

- **WHEN** a tracked LangGraph thread is executing under the primary-runtime `StateGraph` engine
- **THEN** the backend SHALL preserve primary-runtime engine posture in durable state
- **AND** it SHALL not reduce that state to projection-only kernel posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being executed by the primary-runtime engine

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while executing that shell through the compiled primary-runtime engine.

#### Scenario: Operator inspects primary-runtime engine state through the existing phase model

- **WHEN** the compiled primary-runtime engine is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being executed by the primary-runtime engine
