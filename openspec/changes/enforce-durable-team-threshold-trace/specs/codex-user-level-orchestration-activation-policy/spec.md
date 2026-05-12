## ADDED Requirements

### Requirement: First activation traces SHALL report durable-team threshold evidence
Startup and first activation traces SHALL include durable-team threshold evidence.

When a durable team is not selected, the trace SHALL cite the concrete unmet threshold, such as `threshold_not_met:no_frozen_plan`, `threshold_not_met:single_execution_slice`, or an equivalent phase/scope threshold. When a durable team is selected, the trace SHALL cite the concrete trigger, such as a frozen plan with two or more independent execution slices or a stabilization phase with named blocking issues.

#### Scenario: First activation does not select a durable team
- **WHEN** a session emits its first activation trace for startup, resume, or continue
- **AND** durable-team thresholds are not met
- **THEN** the trace SHALL report `persistent_team=not_needed` or `persistent_team=blocked`
- **AND** the trace SHALL identify the unmet durable-team threshold in `why`
- **AND** it SHALL NOT imply that missing user reminders caused the no-team decision

#### Scenario: First activation selects a durable team
- **WHEN** a session emits its first activation trace
- **AND** the plan is frozen with two or more independent execution slices or the stabilization threshold is met
- **THEN** the trace SHALL report the durable-team lane as `selected` or `running`
- **AND** the trace SHALL identify the concrete threshold trigger in `why`
