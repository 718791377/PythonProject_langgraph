# codex-template-implementation-plan-governance Specification

## Purpose
Define how this repository maintains implementation plans for reusable project templates without copying live runtime state or collapsing distinct template capability tiers.

## Requirements
### Requirement: Template implementation plans SHALL separate reusable template intent from live project state

Implementation plans for reusable project templates SHALL describe the intended generated-project behavior, verification path, and rollback path without treating the current repository session, `.omx/state/`, active worktree claims, local runtime logs, or target-project dirty working trees as reusable template facts.

#### Scenario: A template plan mentions runtime state
- **WHEN** a plan discusses `.omx/state/`, LangGraph runtime state, worktree claims, launcher payloads, MCP entries, or Comet workflow evidence
- **THEN** it SHALL identify whether the item is a reusable template artifact, a generated-project local state surface, or current-session evidence
- **AND** it SHALL NOT instruct future projects to copy current live state directories or active session records

### Requirement: General and General_2 template plans SHALL preserve distinct capability tiers

The `PythonProject_General` plan SHALL describe the fuller reusable Codex/OpenSpec/Comet governance template that may include optional oh-my-codex, native_omx, LangGraph compatibility source, MCP scope policy, launcher payload policy, local and remote gate parity, and generated-project durable-state scaffolding.

The `PythonProject_General_2` plan SHALL describe the local Git, OpenSpec, Superpowers governance, and native Codex subagents template tier only. It SHALL NOT describe oh-my-codex, native_omx, LangGraph durable backend, remote CI/MR, remote publication, or `.omx/state/` as currently enabled General_2 capabilities.

#### Scenario: A maintainer compares the two plans
- **WHEN** the maintainer reads both implementation plans side by side
- **THEN** `PythonProject_General` SHALL be identifiable as the fuller governance template
- **AND** `PythonProject_General_2` SHALL be identifiable as the local-only native-subagent template

### Requirement: Comet references SHALL identify OpenSpec and Superpowers governance boundaries

Template implementation plans that reference `/comet` or Comet SHALL describe Comet as the OpenSpec + Superpowers governance workflow: OpenSpec owns WHAT and lifecycle artifacts, Superpowers owns HOW and implementation practice, and Comet coordinates phases and evidence. These references SHALL NOT treat Comet as a native subagent, oh-my-codex, native_omx, LangGraph, or a durable-team backend.

#### Scenario: A plan imports Comet terminology
- **WHEN** a template implementation plan uses terms such as `/comet`, Open, Design, Build, Verify, Archive, OpenSpec, or Superpowers
- **THEN** it SHALL explain the governance role of those terms in the local plan
- **AND** it SHALL keep subagent evidence, skills, profiles, and durable backends separate

### Requirement: Template plan refactors SHALL remain UTF-8 clean and decision complete

A refactored implementation plan SHALL be saved as UTF-8, avoid mojibake and replacement-character markers, and include enough decisions for a future agent to implement without relying on prior chat context. At minimum, the plan SHALL state goal, non-goals, target capability tier, implementation sequence, validation commands, acceptance criteria, and rollback path.

#### Scenario: A future cold-start session resumes template work
- **WHEN** the session opens a refactored implementation plan without access to the original chat
- **THEN** the session SHALL be able to identify what to implement, what not to implement, how to validate it, and how to roll it back
- **AND** the plan SHALL not require copying corrupted terminal output or hidden conversation context
