## ADDED Requirements

### Requirement: Backend selection surface SHALL expose the four-layer orchestration model

The user-level backend-selection surface SHALL distinguish capability switches, backend family, effective lane, and operational ability.

#### Scenario: Operator inspects native OMX on Windows

- **WHEN** the operator inspects backend state for a Windows worker-centric task
- **THEN** the surface SHALL show enabled capability layers separately from selected backend family
- **AND** it SHALL show task-flow effective lane separately from operational ability
- **AND** it SHALL NOT imply that selected `native_omx` is launchable without preflight evidence.

### Requirement: Backend default SHALL NOT override task-flow effective lane evidence

The backend-selection surface SHALL preserve the difference between a durable backend default and a task-flow effective lane.

#### Scenario: LangGraph is enabled but worker-centric native OMX is considered

- **GIVEN** LangGraph is enabled and may be the ready durable default
- **WHEN** a worker-centric task is evaluated for `native_omx`
- **THEN** the surface SHALL report the task-fit reason for the effective lane
- **AND** it SHALL still require operational preflight before a persistent team is launched.
