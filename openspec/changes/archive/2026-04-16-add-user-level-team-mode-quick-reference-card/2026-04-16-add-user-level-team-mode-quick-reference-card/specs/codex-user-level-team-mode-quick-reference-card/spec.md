## ADDED Requirements

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
