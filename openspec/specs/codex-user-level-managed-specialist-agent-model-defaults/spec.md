# codex-user-level-managed-specialist-agent-model-defaults Specification

## Purpose

Define reproducible installer-managed model defaults and stale-model cleanup for user-level Codex specialist agent profiles used by native experts, durable teams, and persistent-team helpers.

## Requirements

### Requirement: The user-level installer SHALL keep managed specialist profiles on supported GPT-5.4 or GPT-5.5 models

The user-level installer SHALL generate managed `team-leader.toml`, `verifier.toml`, `debugger.toml`, `researcher.toml`, `dependency-expert.toml`, `writer.toml`, `bug-finder.toml`, `bug-rebutter.toml`, and `bug-judge.toml` specialist profiles under the user-level agents directory.

All installer-managed specialist profiles SHALL declare exactly one top-level `model` value from the supported allowlist: `gpt-5.4` or `gpt-5.5`.

The installer SHALL NOT generate `gpt-5.3*`, `gpt-5.3-codex*`, `gpt-5.4-mini`, or `gpt-5.5-mini` in managed user-level agent TOMLs.

#### Scenario: Operator installs the managed user-level specialist profiles

- **WHEN** the installer renders managed user-level assets into a target Codex home
- **THEN** it SHALL generate the managed specialist TOMLs there
- **AND** each generated TOML SHALL use only `model = "gpt-5.4"` or `model = "gpt-5.5"`
- **AND** those files SHALL be treated as managed assets for backup, rollback, and future refreshes

### Requirement: Execution-critical specialists SHALL use GPT-5.5 and support/research specialists SHALL use GPT-5.4

The managed `team-leader`, `verifier`, and `debugger` profiles SHALL use `gpt-5.5`.

The managed `researcher`, `dependency-expert`, `writer`, `bug-finder`, `bug-rebutter`, and `bug-judge` profiles SHALL use `gpt-5.4`.

#### Scenario: Operator inspects the generated specialist profiles

- **WHEN** the operator reads the generated managed specialist profiles
- **THEN** `team-leader.toml`, `verifier.toml`, and `debugger.toml` SHALL each declare `model = "gpt-5.5"`
- **AND** `researcher.toml`, `dependency-expert.toml`, `writer.toml`, `bug-finder.toml`, `bug-rebutter.toml`, and `bug-judge.toml` SHALL each declare `model = "gpt-5.4"`

### Requirement: The installer SHALL normalize existing user-level agent TOMLs away from stale model identifiers

The user-level installer SHALL scan existing user-level `agents/*.toml` after writing managed assets and normalize any top-level `model` value outside the supported allowlist to a role-appropriate supported model.

It SHALL also normalize embedded metadata references such as `resolved_model:` and exact-model guidance text when those references contain stale model identifiers.

#### Scenario: Operator refreshes a Codex home with stale user-level agents

- **GIVEN** a target Codex home contains existing agent TOMLs with `gpt-5.3-codex*` or `gpt-5.4-mini`
- **WHEN** the installer completes successfully
- **THEN** those TOMLs SHALL no longer contain `gpt-5.3*`, `gpt-5.3-codex*`, `gpt-5.4-mini`, or `gpt-5.5-mini`
- **AND** the install manifest SHALL include an `agent_model_policy` section reporting allowed models and normalized files
