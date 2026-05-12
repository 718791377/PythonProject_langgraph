# Codex User-Level Orchestration Activation Policy

## Purpose

Define the reusable user-level orchestration-activation policy for Codex CLI so orchestration can be re-checked, retrofitted, and actually adopted across new and existing task flows.
## Requirements
### Requirement: The user-level installation SHALL expose an orchestration-activation policy

The user-level installation SHALL expose a reusable orchestration-activation policy for Codex CLI.

That policy SHALL define:

- that activation is scoped to the current task flow
- that activation is not limited to new projects or new sessions
- which events require activation re-checks
- what counts as a hard routing directive
- what Codex CLI must do when activation thresholds are met and no blocker exists

#### Scenario: Operator inspects the user-level activation policy

- **WHEN** the operator inspects the user-level orchestration policy surfaces
- **THEN** they SHALL be able to identify activation posture, re-check triggers, hard directives, and retrofit rules
- **AND** they SHALL not have to infer those rules only from repository-local project documents

### Requirement: Existing projects and existing sessions SHALL remain orchestration-retrofit capable

The user-level orchestration policy SHALL support retrofit for:

- existing projects with new sessions
- existing live sessions after reload, restart, explicit user routing directive, or tracked durable-state detection

#### Scenario: Existing live session is explicitly told to use `omx`

- **WHEN** the user explicitly tells Codex CLI to use `omx`
- **THEN** Codex CLI SHALL treat that instruction as a hard routing directive
- **AND** it SHALL adopt the orchestration path unless a concrete blocker exists
- **AND** if it does not adopt the orchestration path, it SHALL explain the concrete blocker

### Requirement: Activation traces SHALL expose full orchestration state

The user-level orchestration activation policy SHALL require activation traces to report task phase, capability-chain state, default durable backend, backend readiness, expert selection, durable workflow state, persistent-team state, and a concrete reason.

The trace vocabulary SHALL distinguish `not_needed`, `candidate`, `selected`, `blocked`, and `running`.

#### Scenario: Startup or continue emits an activation trace

- **WHEN** a Codex session starts, reloads, resumes, receives `continue`, changes task phase, detects durable state, or expands to two or more execution slices
- **THEN** the activation trace SHALL include `capability_chain`, `backend_default`, `backend_ready`, `experts`, `durable_workflow`, `persistent_team`, and `why`
- **AND** the trace SHALL explain the concrete threshold or blocker instead of citing missing user requests

### Requirement: Missing user reminders SHALL NOT be a routing reason

The orchestration activation policy SHALL forbid using "the user did not request parallelism", "the user did not request subagents", or equivalent missing-reminder language as the reason for not using experts, durable workflow, or persistent team.

#### Scenario: A small single-file task does not need a durable team

- **WHEN** the current task is a small single-file task
- **THEN** the trace MAY report `persistent_team=not_needed`
- **AND** the reason SHALL cite task phase, scope, risk, or threshold state
- **AND** it SHALL NOT cite missing user instructions as the reason

### Requirement: Expert timeout SHALL NOT be accepted as verification evidence

The orchestration activation policy SHALL require final reports to separate returned expert evidence from timed-out, stalled, abandoned, or main-session-taken-over verification.

#### Scenario: A key-path expert times out

- **WHEN** a key-path expert or subagent times out or stalls
- **THEN** the session SHALL not use that lane as evidence
- **AND** it SHALL continue bounded wait, respawn a narrower expert, hand off to an eligible durable lane, or explicitly record main-session takeover

### Requirement: Existing sessions SHALL retrofit activation policy at safe boundaries

Existing live sessions SHALL re-run activation checks after reload, restart, resume, continue, phase change, durable-state detection, capability-state change, or expert timeout.

#### Scenario: A legacy session is resumed

- **WHEN** a legacy resumed session continues work in this repository
- **THEN** it SHALL treat current repository governance and capability-chain policy as authoritative
- **AND** it SHALL not allow stale runtime assumptions to override current policy

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
