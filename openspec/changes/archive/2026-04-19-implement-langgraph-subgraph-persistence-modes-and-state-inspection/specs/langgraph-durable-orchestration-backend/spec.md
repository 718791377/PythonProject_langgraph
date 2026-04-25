## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose official subgraph persistence modes for reusable subgraphs

When the user-level LangGraph lane uses reusable subgraphs, the backend SHALL expose the official subgraph persistence-mode posture rather than only exposing active-subgraph identity.

At minimum the backend SHALL be able to report:

- per-invocation posture (`checkpointer=None`)
- per-thread posture (`checkpointer=True`)
- stateless posture (`checkpointer=False`)
- whether the active subgraph is inheriting parent checkpoint behavior, accumulating thread memory, or running without checkpointing

#### Scenario: Operator inspects a tracked thread using a reusable subgraph

- **WHEN** a tracked LangGraph thread is operating inside a reusable subgraph-aware phase family
- **THEN** the backend SHALL preserve the active subgraph persistence mode in durable state
- **AND** it SHALL not reduce that state to active-subgraph identity alone

### Requirement: The LangGraph backend SHALL expose bounded subgraph-state inspection posture and constraints

When a tracked LangGraph thread uses reusable subgraphs, the backend SHALL expose whether subgraph state inspection is available and why.

At minimum the backend SHALL be able to report:

- whether subgraph state inspection is available for the current subgraph posture
- whether static subgraph discoverability is satisfied
- whether checkpoint-backed state inspection is unavailable because the subgraph is stateless
- whether per-thread same-subgraph parallel calls are disallowed or otherwise conflict-prone

#### Scenario: Operator inspects subgraph-state availability

- **WHEN** the operator requests subgraph-state inspection for a tracked LangGraph thread
- **THEN** the backend SHALL expose bounded inspection availability and constraint posture
- **AND** it SHALL not imply that stateless or non-discoverable subgraphs have inspectable checkpoint state
