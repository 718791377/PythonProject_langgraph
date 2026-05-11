## ADDED Requirements

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
