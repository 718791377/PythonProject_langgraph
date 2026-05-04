## ADDED Requirements

### Requirement: Mainline memory handoffs SHALL refresh after cleanup-output closeout and durable routing readiness land

Current mainline memory summaries SHALL be refreshed after repository publication lands both the durable routing readiness closeout and a later cleanup-output control closeout that changes cold-start recovery or operator-surface expectations.

#### Scenario: Cleanup-output closeout lands after durable routing readiness

- **WHEN** MR 6 durable routing readiness has landed on GitLab `main`
- **AND** Windows cleanup-output control implementation and archive closeout have also landed on GitLab `main`
- **AND** GitHub `main` mirrors the same latest commit
- **THEN** the current mainline memory summary SHALL identify both increments as completed baseline work
- **AND** it SHALL state whether active OpenSpec changes exist before recommending a next action
- **AND** it SHALL route future live durable routing smoke or adoption-gate work into a separately named reviewed change that names the target repository, phase, task, and operator consent boundary
- **AND** it SHALL not imply that completed MR 6 readiness or cleanup-output work still needs implementation
