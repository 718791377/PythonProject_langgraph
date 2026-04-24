## ADDED Requirements

### Requirement: The user-level LangGraph lane SHALL expose command-driven control flow as an additive durable capability

The user-level LangGraph durable lane SHALL expose command-driven control flow as an additive durable capability under the existing Codex CLI leader model.

The first rollout SHALL keep command-driven control flow additive to the current seven-phase root graph and reusable subgraph library instead of replacing them.

#### Scenario: Operator inspects command-driven control flow in the user-level LangGraph lane

- **WHEN** the operator inspects the user-level LangGraph command-driven control-flow capability
- **THEN** the capability SHALL remain additive under the existing Codex CLI leader model
- **AND** it SHALL not present command-driven control flow as a separate replacement runtime

### Requirement: Command-driven control flow SHALL support explicit parent-directed handoffs for reusable subgraphs

The user-level LangGraph command-driven control-flow capability SHALL support explicit parent-directed handoffs for reusable subgraphs.

#### Scenario: Execution subgraph returns to the parent graph through a command-driven handoff

- **WHEN** the durable workflow exits the reusable `execution` subgraph through a parent-directed command path
- **THEN** the capability SHALL expose that parent-directed handoff as first-class durable behavior
- **AND** it SHALL preserve source and target handoff posture for operator inspection

### Requirement: Command-driven continuation SHALL preserve explicit resume posture

The user-level LangGraph command-driven control-flow capability SHALL preserve explicit resume posture when durable continuation depends on command-aware resume intent.

#### Scenario: Operator resumes a tracked thread with command-aware continuation posture

- **WHEN** the operator resumes a tracked LangGraph thread through command-aware continuation
- **THEN** the capability SHALL preserve resume posture as durable command-driven state
- **AND** it SHALL keep that posture bounded and inspectable
