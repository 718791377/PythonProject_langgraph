## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose broader bounded automatic runtime-policy behavior for the user-level durable lane

The user-level LangGraph backend SHALL broaden the bounded automatic runtime-policy layer beyond the initial migration and resolved-queue posture while preserving manual-first control.

#### Scenario: Operator inspects broader automatic-policy posture for a tracked thread

- **WHEN** a tracked LangGraph thread is operating under the broader automatic-policy lane
- **THEN** the backend SHALL preserve broader bounded automatic-policy posture in durable state
- **AND** it SHALL not hide that posture behind uninspectable implicit behavior
