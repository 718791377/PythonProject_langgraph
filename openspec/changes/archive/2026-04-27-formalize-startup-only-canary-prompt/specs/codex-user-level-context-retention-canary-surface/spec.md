# codex-user-level-context-retention-canary-surface Specification

## Purpose

Define the startup-summary-only source of truth for the repository context-retention canary prompt and the executable control that prevents active instruction surfaces from duplicating that prompt.

## ADDED Requirements

### Requirement: Canary prompt text SHALL live only in the startup summary pair

The repository SHALL maintain the literal context-retention canary prompt only in the active bilingual startup summary pair:

- `docs_bilingual/project_startup_summary.md` - English startup summary and canary prompt source.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup summary and canary prompt source.

Other active instruction surfaces MAY refer to the startup-summary canary and MAY describe the cold-start recovery action, but SHALL NOT duplicate the literal canary prompt text.

#### Scenario: Repository instructions refer to the canary without duplicating it

- **WHEN** `AGENTS.md` documents context-loss recovery
- **THEN** it SHALL point to the startup summary as the canary source of truth
- **AND** it SHALL NOT contain the literal canary prompt text

### Requirement: Canary placement SHALL have executable enforcement

The repository SHALL provide an executable checker that validates active canary placement without relying on model memory alone.

The checker SHALL fail closed when:

- either startup summary is missing the literal canary prompt
- an active non-startup-summary file duplicates the literal canary prompt text

The checker MAY ignore immutable historical archives, external worktrees, caches, runtime state, and binary files.

#### Scenario: Active file duplicates the literal prompt

- **WHEN** an active file outside the startup summary pair contains the literal canary prompt text
- **THEN** the checker SHALL return a non-zero exit code
- **AND** the checker SHALL report the offending file path

### Requirement: OpenSpec guard SHALL run the canary placement checker

The repository OpenSpec guard SHALL run the canary placement checker as part of its standard verification sequence.

#### Scenario: OpenSpec guard runs on a cold-start clone

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs in a repository clone
- **THEN** the aggregated guard output SHALL include a `check_context_retention_canary_surface` step
- **AND** the guard SHALL fail if the checker reports canary placement errors
