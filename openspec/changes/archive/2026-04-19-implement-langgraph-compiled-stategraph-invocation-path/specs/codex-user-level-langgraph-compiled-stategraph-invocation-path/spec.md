## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose a live compiled `StateGraph` invocation path as an additive durable capability

The user-level LangGraph durable lane SHALL expose a live compiled `StateGraph` invocation path as an additive durable capability under the existing Codex CLI leader model.

The first rollout SHALL keep compiled invocation additive to the current seven-phase shell, graph-kernel layer, primary-runtime engine layer, reusable subgraph library, command-driven control flow, streaming observability, runtime/store injection, memory posture, migration posture, multi-interrupt posture, and replay or recovery surfaces.

#### Scenario: Operator inspects the user-level LangGraph compiled-invocation capability

- **WHEN** the operator inspects the user-level LangGraph compiled-invocation capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present the compiled invocation path as a separate replacement runtime outside the current user-level orchestration line
