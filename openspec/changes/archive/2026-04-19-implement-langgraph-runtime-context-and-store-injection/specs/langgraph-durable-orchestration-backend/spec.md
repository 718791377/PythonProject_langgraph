## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose runtime-context contracts for tracked threads

The user-level LangGraph backend SHALL expose runtime-context contracts for tracked threads aligned with `context_schema` and `Runtime.context`.

At minimum the runtime-context contract SHALL be able to represent:

- context-schema identity or equivalent schema posture
- bounded runtime-context key posture
- whether runtime context is present for the tracked thread

#### Scenario: Operator inspects runtime-context posture for a tracked thread

- **WHEN** a tracked LangGraph thread was started with runtime-context metadata
- **THEN** the backend SHALL preserve bounded runtime-context posture in durable state
- **AND** it SHALL keep runtime-context posture distinguishable from mutable graph state

### Requirement: The LangGraph backend SHALL expose injected-store posture for tracked threads

The user-level LangGraph backend SHALL expose injected-store posture for tracked threads aligned with `Runtime.store`.

At minimum the backend SHALL be able to report:

- whether an injected store is configured
- whether store access is expected to be available to nodes
- a bounded store-kind or store-posture classification

#### Scenario: Operator inspects injected-store posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured with injected store access
- **THEN** the backend SHALL preserve bounded store-injection posture in durable state
- **AND** it SHALL not overstate that posture as semantic-memory behavior by itself
