## ADDED Requirements

### Requirement: The LangGraph backend SHALL expose bounded richer automatic runtime-policy posture for the user-level durable lane

The user-level LangGraph backend SHALL expose bounded automatic runtime-policy posture for concrete domains such as migration handling and approval or queue-resolution behavior.

#### Scenario: Operator inspects automatic runtime-policy posture for a tracked thread

- **WHEN** a tracked LangGraph thread is operating under the richer automatic-policy lane
- **THEN** the backend SHALL preserve bounded automatic-policy posture in durable state
- **AND** it SHALL not hide that posture behind uninspectable implicit behavior
