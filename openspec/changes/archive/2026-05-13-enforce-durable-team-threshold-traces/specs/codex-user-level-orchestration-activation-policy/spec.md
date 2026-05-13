## MODIFIED Requirements

### Requirement: Activation traces SHALL expose full orchestration state
The user-level orchestration activation policy SHALL require activation traces to report task phase, capability-chain state, default durable backend, backend readiness, expert selection, durable workflow state, persistent-team state, and a concrete reason.

The trace vocabulary SHALL distinguish `not_needed`, `candidate`, `selected`, `blocked`, and `running`.

The repository SHALL provide an executable trace-evidence validator that can inspect saved activation trace text for required fields, capability-chain consistency, backend readiness semantics, durable workflow and persistent-team vocabulary, forbidden missing-reminder reasons, expert-timeout evidence labels, and durable-team threshold evidence in the `why` field.

#### Scenario: Saved trace evidence is checked
- **WHEN** a saved activation trace is passed to the repository trace-evidence validator
- **THEN** the validator SHALL fail if any required trace field is missing
- **AND** it SHALL fail if capability-chain dependency states are inconsistent
- **AND** it SHALL fail if durable workflow or persistent-team states use unsupported vocabulary
- **AND** it SHALL fail if expert timeout language is presented without a non-evidence, bounded-wait, respawn, durable-handoff, or main-session-takeover label
- **AND** it SHALL fail if durable workflow or persistent-team decisions omit required unmet-threshold, named-blocker, or triggered-threshold evidence from `why`

### Requirement: First activation traces SHALL report durable-team threshold evidence
Startup and first activation traces SHALL include durable-team threshold evidence.

When a durable team is not selected, the trace SHALL cite the concrete unmet threshold, such as `threshold_not_met:no_frozen_plan`, `threshold_not_met:single_execution_slice`, or an equivalent phase/scope threshold. When a durable team is blocked, the trace SHALL cite a named blocker or unmet threshold. When a durable team is selected or running, the trace SHALL cite the concrete trigger, such as `triggered_threshold:frozen_plan_with_2+_independent_slices`, a frozen plan with two or more independent execution slices, or a stabilization phase with named blocking issues.

#### Scenario: First activation does not select a durable team
- **WHEN** a session emits its first activation trace for startup, resume, or continue
- **AND** durable-team thresholds are not met
- **THEN** the trace SHALL report `persistent_team=not_needed` or `persistent_team=blocked`
- **AND** the trace SHALL identify the unmet durable-team threshold or named blocker in `why`
- **AND** it SHALL NOT imply that missing user reminders caused the no-team decision

#### Scenario: First activation selects a durable team
- **WHEN** a session emits its first activation trace
- **AND** the plan is frozen with two or more independent execution slices or the stabilization threshold is met
- **THEN** the trace SHALL report the durable-team lane as `selected` or `running`
- **AND** the trace SHALL identify the concrete threshold trigger in `why`

#### Scenario: Trace validator rejects vague durable-team decisions
- **WHEN** saved trace evidence reports `persistent_team=not_needed` without `threshold_not_met:*` or equivalent unmet-threshold language in `why`
- **OR** it reports `persistent_team=blocked` without `blocked:*` or unmet-threshold language in `why`
- **OR** it reports `persistent_team=selected` or `persistent_team=running` without `triggered_threshold:*` or equivalent trigger language in `why`
- **THEN** the trace-evidence validator SHALL fail the trace
