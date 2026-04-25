## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose generalized live `StateGraph` routing for the user-level durable lane

The user-level LangGraph backend SHALL expose generalized live `StateGraph` routing instead of keeping live execution constrained to a narrowly bounded branch only.

At minimum the backend SHALL be able to report:

- generalized live-routing identity
- live loop posture beyond the current narrow branch
- graph-native route decisions across the seven-phase shell
- resumable generalized live-routing state for tracked threads

#### Scenario: Operator inspects a tracked thread running through generalized live routing

- **WHEN** a tracked LangGraph thread is executing through the generalized live-routing path
- **THEN** the backend SHALL preserve generalized live-routing posture in durable state
- **AND** it SHALL not reduce that state to a narrowly bounded branch posture only

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being driven by generalized live routing

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while driving that shell through the generalized live-routing model.

#### Scenario: Operator inspects generalized live routing through the existing phase model

- **WHEN** the generalized live-routing path is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture is being driven by the generalized live-routing model
