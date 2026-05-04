## ADDED Requirements

### Requirement: Durable routing smoke gates SHALL use a script-backed template before runtime exercise

Durable routing smoke gates SHALL use a reviewed repository-local template before any later dry-run, read-only sampling, or adoption exercise claims to evaluate automatic durable routing.

The template SHALL remain read-only and SHALL describe, at minimum:

- `target_repository` - the repository root that owns source, OpenSpec artifacts, and repo-local durable state.
- `phase` - the project phase that drives durable routing thresholds.
- `task` - the concrete work item or validation question being evaluated.
- `operator_consent_boundary` - the boundary between read-only planning and mutating actions.
- `routing_mode` - whether the future exercise is read-only, dry-run, or explicitly apply-capable.
- `mutation_allowed` - a boolean that defaults to false for this release.
- `validation_path` - the commands or checks that prove the exercise result.
- `rollback_path` - the recovery steps if a future exercise is misconfigured.

The template SHALL be checked by an executable repository checker and by the OpenSpec guard. The checker SHALL NOT launch a durable team, run `omx-team-auto.ps1 -Apply`, or write `.omx/state/`.

#### Scenario: Guard validates the smoke gate template without mutating durable state

- **WHEN** the repository OpenSpec guard runs
- **THEN** it SHALL execute the durable routing smoke gate template checker
- **AND** the checker SHALL validate the required template fields and descriptions
- **AND** the checker SHALL remain read-only
- **AND** it SHALL NOT launch native_omx, launch LangGraph, or mutate `.omx/state/`

#### Scenario: Future smoke gate starts from explicit consent boundaries

- **WHEN** a future R0.6.x smoke gate copies or references the reviewed template
- **THEN** the future gate SHALL declare `target_repository`, `phase`, `task`, `operator_consent_boundary`, `routing_mode`, `mutation_allowed`, `validation_path`, and `rollback_path`
- **AND** `mutation_allowed` SHALL remain false unless a reviewed change and the operator explicitly authorize mutation
