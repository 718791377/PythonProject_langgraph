## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose a live compiled `StateGraph` invocation path for the user-level durable lane

The user-level LangGraph backend SHALL expose a live compiled `StateGraph` invocation path instead of keeping graph-native execution only as a bounded primary-runtime posture.

At minimum the backend SHALL be able to report:

- compiled invocation identity
- live graph execution posture
- graph-native node or phase execution mapping
- resumable invocation state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the compiled invocation path

- **WHEN** a tracked LangGraph thread is executing through the live compiled `StateGraph` invocation path
- **THEN** the backend SHALL preserve compiled invocation posture in durable state
- **AND** it SHALL not reduce that state to engine-projection-only posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by the compiled invocation path

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the live compiled invocation path.

#### Scenario: Operator inspects compiled invocation state through the existing phase model

- **WHEN** the live compiled invocation path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the compiled invocation path
