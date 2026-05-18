# codex-user-level-team-mode-quick-reference-card Specification

## Purpose

Define a concise user-level operator command card for the most common team-mode commands, alongside the full playbook.

## Requirements

### Requirement: The quick-reference card SHALL preserve the automatic collaboration default

The generated user-level quick-reference card SHALL include a concise global automatic collaboration default section. The section SHALL state that automatic collaboration is on by default for all projects and all user-level Codex sessions, that the user does not need to repeat collaboration reminder phrases, and that native `spawn_agent` platform/tool constraints must be reported as concrete blockers rather than missing-reminder reasons.

#### Scenario: Operator opens regenerated quick-reference card

- **WHEN** the user-level installer regenerates `docs/team-mode-quick-reference.md`
- **THEN** the card SHALL contain a global automatic collaboration default section
- **AND** it SHALL mention automatic evaluation of native experts, `native_omx`, LangGraph durable workflow, and persistent team for qualifying tasks
- **AND** it SHALL include `experts=blocked:platform_subagent_invocation_constraint` for native subagent platform/tool blockers
- **AND** it SHALL preserve threshold-gated durable/persistent team selection language

### Requirement: The user-level installation SHALL generate a quick-reference command card
The user-level installation SHALL generate a concise quick-reference card for the most common team-mode commands.

The quick-reference card SHALL remain a companion to the full playbook rather than a replacement for it.

#### Scenario: Operator opens the generated quick-reference card
- **WHEN** the user opens the generated quick-reference card under the user-level docs directory
- **THEN** it SHALL present a concise command-oriented reference
- **AND** it SHALL not try to replace the full playbook as the canonical long-form reference

### Requirement: The quick-reference card SHALL group commands by operator task
The quick-reference card SHALL group commands by operator task rather than by script directory listing.

At minimum the first rollout SHALL cover:

- mode and switch inspection
- backend inspection
- durable-state inspection
- durable-state cleanup or reconciliation preview and apply
- native `omx` team launch or operations
- LangGraph run, inspect, and resume
- compose runtime inspect, shutdown, and reconcile
- compose runtime await

#### Scenario: Operator looks for the command to inspect current durable state
- **WHEN** the operator uses the quick-reference card to find the durable-state inspection command
- **THEN** the card SHALL present the command in a task-oriented section
- **AND** it SHALL not require the operator to infer the right command only from a full bin-directory inventory

### Requirement: The quick-reference card SHALL distinguish read-only and mutating commands
The quick-reference card SHALL distinguish whether each listed command is read-only, preview-first, or mutating.

#### Scenario: Operator reads the cleanup and reconciliation section
- **WHEN** the quick-reference card lists cleanup or reconciliation commands
- **THEN** it SHALL indicate that preview is read-first by default
- **AND** it SHALL indicate which command form performs mutation

### Requirement: The quick-reference card SHALL include compose lifecycle helper commands when compose runtime lifecycle helpers are installed

When compose runtime lifecycle helpers are installed, the quick-reference card SHALL include the common compose lifecycle commands alongside the other user-level operator commands.

#### Scenario: Operator looks for the command to inspect or shut down tracked compose runtime

- **WHEN** the operator uses the quick-reference card after compose lifecycle helpers are installed
- **THEN** the card SHALL include compose inspect or status and compose shutdown command examples
- **AND** it SHALL not require the operator to search the full playbook for those common lifecycle actions

### Requirement: The quick-reference card SHALL include compose await commands when compose await support is installed

When compose await support is installed, the quick-reference card SHALL include the common compose await command alongside the other compose lifecycle commands.

#### Scenario: Operator looks for the command to await tracked compose runtime

- **WHEN** the operator uses the quick-reference card after compose await support is installed
- **THEN** the card SHALL include a compose await command example
- **AND** it SHALL not require the operator to search the full playbook for that common compose lifecycle action

### Requirement: The quick-reference card SHALL include compose recovery or resume commands when compose recovery support is installed

When compose recovery support is installed, the quick-reference card SHALL include the common compose recovery or resume command alongside the other compose lifecycle commands.

#### Scenario: Operator looks for the command to inspect compose recovery posture

- **WHEN** the operator uses the quick-reference card after compose recovery support is installed
- **THEN** the card SHALL include a compose recovery or resume command example
- **AND** it SHALL not require the operator to search the full playbook for that common compose recovery action
