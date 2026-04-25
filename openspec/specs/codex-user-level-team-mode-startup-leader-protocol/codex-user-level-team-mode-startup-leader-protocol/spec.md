# codex-user-level-team-mode-startup-leader-protocol Specification

## Purpose

Define the startup-time leader protocol for wrapped Codex sessions so every new session begins with a stable leader-first routing posture and an inspectable first-turn routing trace.

## Requirements

### Requirement: Every wrapped Codex session SHALL start in a leader-first routing posture

When startup is routed through the user-level wrapped `codex` entrypoint, the new session SHALL begin in a stable leader-first routing posture rather than a generic session that merely has routing capability installed.

#### Scenario: Start a fresh wrapped Codex session in enhanced auto mode

- **WHEN** the operator starts a fresh wrapped Codex session with `oh_my_codex=on` and `subagent_routing=auto`
- **THEN** the session SHALL identify itself as a leader-first routed session
- **AND** it SHALL treat the current main Codex CLI session as the leader lane before the first substantive answer

### Requirement: Wrapped startup SHALL classify task shape before first substantive answer

Wrapped startup SHALL perform a first-turn task-shape check before the first substantive answer.

At minimum it SHALL decide:

- whether the task is still in early analysis or planning
- whether leader-side expert native subagents are needed now
- whether durable-team thresholds are already met

#### Scenario: Startup sees an early-stage task

- **WHEN** the initial task is still unclear or still in a planning stage
- **THEN** startup SHALL classify it as not yet durable-team-ready
- **AND** it SHALL not behave as if `omx team` has already been selected

### Requirement: Wrapped startup SHALL emit an inspectable first-turn routing trace

Wrapped startup SHALL expose a short routing trace that explains first-turn routing decisions.

The trace SHALL be able to explain:

- which expert role set was selected or skipped
- whether `omx team` thresholds were met or not met
- why the current session stayed bursty or escalated toward durable team usage

#### Scenario: Startup does not select `omx team`

- **WHEN** the initial task does not yet meet durable-team thresholds
- **THEN** the first-turn routing trace SHALL explain which threshold was not met
- **AND** it SHALL not leave the operator guessing whether routing failed or was intentionally deferred

### Requirement: Wrapped sessions SHALL re-run orchestration activation checks on reload and restart

The user-level startup leader protocol SHALL not treat orchestration activation as a one-time first-turn-only event.

Wrapped sessions SHALL re-run orchestration activation checks:

- on session reload
- on `codex` restart
- before deep execution resumes

#### Scenario: Wrapped session resumes after restart

- **WHEN** the operator restarts `codex` for a repository that already has tracked durable state
- **THEN** the wrapped session SHALL re-run the orchestration activation check
- **AND** it SHALL not behave as if only a brand-new session may trigger orchestration routing
