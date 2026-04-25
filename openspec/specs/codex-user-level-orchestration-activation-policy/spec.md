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
