## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose a `StateGraph`-first runtime kernel for the user-level durable lane

The user-level LangGraph backend SHALL expose a `StateGraph`-first runtime kernel instead of remaining only a projection-first durable shell around repo-local state.

At minimum the backend SHALL be able to report:

- graph-kernel identity
- graph-native node or phase mapping
- graph-native edge or transition posture
- resumable kernel state for tracked threads

#### Scenario: Operator inspects a tracked thread running through the graph-native kernel

- **WHEN** a tracked LangGraph thread is running under the graph-native runtime kernel
- **THEN** the backend SHALL preserve graph-native kernel posture in durable state
- **AND** it SHALL not reduce that state to shell-only summary posture

### Requirement: The seven-phase durable shell SHALL remain externally compatible while being mapped into graph-native kernel state

The user-level LangGraph backend SHALL keep the seven-phase durable shell as the operator-facing contract while mapping that shell into graph-native runtime state internally.

#### Scenario: Operator inspects graph-native kernel state through the existing phase model

- **WHEN** the graph-native kernel is active for a tracked LangGraph thread
- **THEN** the backend SHALL preserve the existing seven-phase operator-facing posture
- **AND** it SHALL expose how that posture maps into graph-native kernel state
