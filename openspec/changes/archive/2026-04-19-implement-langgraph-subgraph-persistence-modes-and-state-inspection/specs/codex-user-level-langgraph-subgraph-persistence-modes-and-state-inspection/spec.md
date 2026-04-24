## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose subgraph persistence modes and state inspection as an additive durable capability

The user-level LangGraph durable lane SHALL expose official subgraph persistence modes and bounded subgraph-state inspection as an additive durable capability under the existing Codex CLI leader model.

The first rollout SHALL keep this capability additive to the current reusable subgraph library, command-driven control flow, streaming observability, runtime/store injection, memory posture, migration posture, multi-interrupt posture, replay or recovery surfaces, graph-kernel layer, primary-runtime engine layer, compiled-invocation layer, live-execution layer, and generalized live-routing layer.

#### Scenario: Operator inspects the user-level LangGraph subgraph persistence capability

- **WHEN** the operator inspects the user-level LangGraph subgraph persistence and inspection capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present subgraph persistence modes as a separate replacement runtime outside the current user-level orchestration line
