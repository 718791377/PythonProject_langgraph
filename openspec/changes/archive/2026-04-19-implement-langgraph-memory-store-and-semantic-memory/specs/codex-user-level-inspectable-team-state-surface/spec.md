## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project memory-store and semantic-memory posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread with memory-store or semantic-memory metadata, the canonical inspectable durable-state surface SHALL expose LangGraph-specific memory-store and semantic-memory projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- memory-store configured or not configured
- memory-store kind or bounded memory-store posture
- semantic-memory enabled or not enabled
- semantic namespace or bounded retrieval scope when present
- the relevant memory/store inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread with durable memory posture

- **WHEN** the current repository has a tracked LangGraph thread with memory-store or semantic-memory metadata
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded memory-store and semantic-memory projection data
