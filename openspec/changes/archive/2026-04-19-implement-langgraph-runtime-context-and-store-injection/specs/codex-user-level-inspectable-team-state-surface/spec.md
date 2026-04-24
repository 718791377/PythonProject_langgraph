## ADDED Requirements

### Requirement: The canonical durable-state surface SHALL project runtime-context and store-injection posture for tracked LangGraph threads

When the current repository has a tracked LangGraph durable thread with runtime-context or injected-store metadata, the canonical inspectable durable-state surface SHALL expose LangGraph-specific runtime-context and store-injection projection data without changing the shared cross-backend summary contract.

At minimum the LangGraph projection SHALL be able to report:

- bounded runtime-context schema or key posture
- injected-store configured or not configured
- injected-store kind or bounded posture when present
- the relevant runtime/store inspection helper pointer

#### Scenario: Operator inspects a tracked LangGraph thread with runtime/store injection posture

- **WHEN** the current repository has a tracked LangGraph thread with runtime-context or injected-store metadata
- **THEN** the canonical summary SHALL preserve the shared durable-state fields
- **AND** it SHALL include bounded runtime-context and store-injection projection data
