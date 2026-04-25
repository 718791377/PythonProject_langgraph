## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose command-driven transition contracts for tracked threads

The user-level LangGraph backend SHALL expose explicit command-driven transition contracts for tracked threads instead of reducing all durable movement to implicit phase changes or gate verdicts only.

At minimum the command-driven contract SHALL be able to represent:

- state update intent
- local `goto` target
- graph target scope
- resume intent when present

#### Scenario: Operator inspects a command-driven local transition

- **WHEN** a tracked LangGraph thread records a command-driven transition within the current graph scope
- **THEN** the backend SHALL preserve the command-driven transition posture in durable thread or checkpoint state
- **AND** it SHALL keep that posture inspectable instead of collapsing it into an unqualified phase change only

### Requirement: The LangGraph backend SHALL support explicit parent-directed handoff posture across reusable subgraph boundaries

When a reusable subgraph exits through a parent-directed control-flow path, the backend SHALL preserve that handoff as explicit durable posture rather than treating it as an inferred side effect.

At minimum the backend SHALL be able to report:

- source subgraph identity
- target graph scope
- parent-handoff target when present

#### Scenario: Execution subgraph hands control back to the parent graph

- **WHEN** a tracked LangGraph thread reaches a parent-directed handoff from a reusable subgraph
- **THEN** the backend SHALL preserve the parent-handoff source and target posture in durable state
- **AND** it SHALL not treat that handoff as indistinguishable from an ordinary in-subgraph transition

### Requirement: The LangGraph backend SHALL preserve resume-payload posture for command-driven continuation

When command-driven continuation requires explicit resume intent, the backend SHALL preserve whether the tracked thread is awaiting resume input or has resumed with explicit command-driven continuation posture.

#### Scenario: Interrupted thread resumes through command-driven continuation

- **WHEN** a tracked LangGraph thread resumes from an interrupt with explicit continuation intent
- **THEN** the backend SHALL preserve that resume posture as command-aware durable state
- **AND** it SHALL keep resume metadata bounded and inspectable across later operator inspection
