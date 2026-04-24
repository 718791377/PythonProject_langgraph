## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project graph-kernel posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread running through the graph-native runtime kernel, the canonical inspectable durable-state surface SHALL expose LangGraph-specific graph-kernel projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- graph-kernel identity
- current kernel node or mapped phase posture
- bounded edge or transition posture
- the relevant graph-kernel inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread after the runtime kernel deepens

- **WHEN** the current repository has a tracked LangGraph thread running under the graph-native runtime kernel
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded graph-kernel projection data
