## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose a compiled `StateGraph` primary-runtime engine as an additive durable capability

The user-level LangGraph durable lane SHALL expose a compiled `StateGraph` primary-runtime engine as an additive durable capability under the existing Codex CLI leader model.

The first rollout SHALL keep the engine posture additive to the current seven-phase shell, bounded graph-kernel layer, reusable subgraph library, command-driven control flow, streaming observability, runtime/store injection, memory posture, migration posture, multi-interrupt posture, and replay or recovery surfaces.

#### Scenario: Operator inspects the user-level LangGraph primary-runtime capability

- **WHEN** the operator inspects the user-level LangGraph primary-runtime capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present the primary-runtime engine as a separate replacement runtime outside the current user-level orchestration line
