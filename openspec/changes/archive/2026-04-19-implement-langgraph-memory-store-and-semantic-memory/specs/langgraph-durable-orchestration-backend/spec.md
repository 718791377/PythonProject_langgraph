## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose durable memory-store posture for tracked threads

The user-level LangGraph backend SHALL expose durable memory-store posture for tracked threads on top of injected store capability.

At minimum the backend SHALL be able to report:

- whether durable memory store is configured
- memory store kind or bounded store posture
- memory namespace or bounded memory scope when present

#### Scenario: Operator inspects durable memory-store posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured to use a durable memory store
- **THEN** the backend SHALL preserve bounded memory-store posture in durable state
- **AND** it SHALL keep memory-store posture distinguishable from plain injected store availability

### Requirement: The LangGraph backend SHALL expose semantic-memory posture for tracked threads

The user-level LangGraph backend SHALL expose bounded semantic-memory posture for tracked threads without forcing one provider implementation.

At minimum the backend SHALL be able to report:

- whether semantic lookup is enabled
- semantic store kind or bounded semantic posture
- semantic namespace or bounded retrieval scope when present

#### Scenario: Operator inspects semantic-memory posture for a tracked thread

- **WHEN** a tracked LangGraph thread is configured for semantic lookup over durable memory
- **THEN** the backend SHALL preserve bounded semantic-memory posture in durable state
- **AND** it SHALL not overstate that posture as one provider-specific implementation by default
