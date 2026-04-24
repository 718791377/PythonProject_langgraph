# codex-user-level-managed-specialist-agent-model-defaults Specification

## Purpose

Define reproducible installer-managed model defaults for selected user-level specialist agent profiles.

## Requirements

### Requirement: The user-level installer SHALL manage verifier and debugger specialist model defaults

The user-level installer SHALL generate managed `verifier.toml` and `debugger.toml` specialist profiles under the user-level agents directory.

It SHALL also generate managed `researcher.toml`, `dependency-expert.toml`, and `writer.toml` specialist profiles there.

#### Scenario: Operator installs the managed user-level specialist profiles

- **WHEN** the installer renders managed user-level assets into a target Codex home
- **THEN** it SHALL generate `verifier.toml`, `debugger.toml`, `researcher.toml`, `dependency-expert.toml`, and `writer.toml` there
- **AND** those files SHALL be treated as managed assets for backup, rollback, and future refreshes

### Requirement: Managed verifier and debugger profiles SHALL use strengthened frontier defaults

The managed `verifier` and `debugger` profiles SHALL use `gpt-5.4` with `high` reasoning effort.

The managed `researcher` and `dependency-expert` profiles SHALL also use `gpt-5.4` with `high` reasoning effort.

The managed `writer` profile SHALL use `gpt-5.4` with `medium` reasoning effort.

#### Scenario: Operator inspects the generated specialist profiles

- **WHEN** the operator reads the generated managed specialist profiles
- **THEN** `verifier.toml`, `debugger.toml`, `researcher.toml`, and `dependency-expert.toml` SHALL each declare `model = "gpt-5.4"` and `model_reasoning_effort = "high"`
- **AND** `writer.toml` SHALL declare `model = "gpt-5.4"` and `model_reasoning_effort = "medium"`
