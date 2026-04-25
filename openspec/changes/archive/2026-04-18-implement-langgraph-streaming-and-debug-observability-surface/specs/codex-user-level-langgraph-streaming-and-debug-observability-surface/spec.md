## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose streaming and debug observability as an additive durable capability

The user-level LangGraph durable lane SHALL expose streaming and debug observability as an additive durable capability under the existing Codex CLI leader model.

The first rollout SHALL keep this observability surface additive to the current seven-phase root graph, reusable subgraph library, replay or recovery controls, and command-driven control flow.

#### Scenario: Operator inspects the user-level LangGraph streaming and debug observability capability

- **WHEN** the operator inspects the user-level LangGraph streaming and debug observability capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present stream observability as a separate replacement runtime

### Requirement: Streaming and debug observability SHALL support operator-relevant event modes

The user-level LangGraph streaming and debug observability capability SHALL support operator-relevant event modes for durable orchestration diagnosis.

At minimum the first rollout SHALL support:

- `updates`
- `checkpoints`
- `tasks`
- `debug`

#### Scenario: Operator requests debug and checkpoint observability for a tracked thread

- **WHEN** the operator requests stream observability for a tracked LangGraph thread with selected event modes
- **THEN** the capability SHALL preserve those selected event modes as additive observability behavior
- **AND** it SHALL keep mode selection inspectable afterward

### Requirement: Streaming observability SHALL preserve nested subgraph visibility explicitly

The user-level LangGraph streaming and debug observability capability SHALL preserve whether nested subgraph visibility is enabled for streamed execution.

#### Scenario: Operator enables nested subgraph visibility for stream observability

- **WHEN** the operator requests stream observability with nested subgraph visibility
- **THEN** the capability SHALL preserve that nested-subgraph posture explicitly
- **AND** it SHALL keep that posture distinguishable from root-only streaming
