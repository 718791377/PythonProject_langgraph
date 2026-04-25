## ADDED Requirements

### Requirement: The inspectable summary SHALL expose LangGraph durable artifact presence explicitly

When the current repository has tracked LangGraph durable state, the canonical inspectable durable-state summary SHALL expose whether stable LangGraph durable artifacts are present.

At minimum the summary SHALL be able to report:

- frozen implementation brief presence
- survivor queue presence
- survivor count or status when known
- inspect pointer for the backend record or artifact view
- resume pointer when the tracked thread is resumable

#### Scenario: Operator inspects a tracked LangGraph thread with hardened artifacts

- **WHEN** the current repository has a tracked LangGraph durable thread
- **THEN** the canonical inspectable summary SHALL report whether a frozen implementation brief and survivor queue are present
- **AND** it SHALL expose relevant inspect or resume pointers without reopening backend-selection policy
