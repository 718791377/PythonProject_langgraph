## ADDED Requirements

### Requirement: Release-train roadmap slices SHALL remain bounded before production durable-team claims

Before the repository treats any production durable-team target as active implementation, the roadmap SHALL decompose the path into bounded release slices.

Each release slice SHALL have an independently reviewable OpenSpec change by default and SHALL state its validation path, rollback path, target repository, task scope, and operator consent boundary.

A roadmap slice SHALL NOT imply permission to mutate `.omx/state/`, run `omx-team-auto.ps1 -Apply`, or launch `omx team` unless the reviewed change and the operator explicitly authorize that mutation.

#### Scenario: A future session chooses the next slice after R0.6 planning

- **WHEN** a future session continues after the R0.6 durable routing smoke gate roadmap is refined
- **THEN** it SHALL prefer the smallest unfinished subrelease such as `R0.6.0 Gate Template` or `R0.6.1 Gate Field Checker`
- **AND** it SHALL not jump directly to `R2.0 Production Durable Team`
- **AND** it SHALL keep the production durable-team plan in draft status unless a specific reviewed release slice promotes part of it

#### Scenario: A roadmap slice reaches runtime exercise

- **WHEN** a future release slice proposes runtime exercise
- **THEN** that slice SHALL declare the operator consent boundary before mutation
- **AND** it SHALL keep read-only inspection as the default posture until explicit consent is present
