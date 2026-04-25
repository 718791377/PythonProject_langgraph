## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose a live compiled `StateGraph` execution path for the user-level durable lane

The user-level LangGraph backend SHALL expose a live compiled `StateGraph` execution path instead of keeping compiled graph behavior only as a bounded invocation posture.

At minimum the backend SHALL be able to report:

- live-execution identity
- actual compiled graph execution posture
- graph-native node or phase execution mapping
- resumable live-execution state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the live compiled execution path

- **WHEN** a tracked LangGraph thread is executing through the live compiled `StateGraph` execution path
- **THEN** the backend SHALL preserve live-execution posture in durable state
- **AND** it SHALL not reduce that state to invocation-projection-only posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by the live compiled execution path

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the live compiled execution path.

#### Scenario: Operator inspects live execution state through the existing phase model

- **WHEN** the live compiled execution path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the live compiled execution path
