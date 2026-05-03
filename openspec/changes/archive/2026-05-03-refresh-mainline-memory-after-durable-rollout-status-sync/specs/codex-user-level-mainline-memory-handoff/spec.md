## ADDED Requirements

### Requirement: Mainline memory handoffs SHALL refresh after durable rollout status-sync archive work lands

Current mainline memory summaries SHALL be refreshed after repository publication lands a durable rollout status-sync archive that changes the safe next-action queue.

#### Scenario: Durable rollout status sync is archived after MR 5 is complete

- **WHEN** durable rollout status sync and archive closeout have landed on GitLab `main`
- **AND** GitHub `main` mirrors the same commit
- **THEN** the current mainline memory summary SHALL identify that status-sync archive as a latest landed increment
- **AND** it SHALL state that MR 5 helper mirror source-of-truth work is already completed
- **AND** it SHALL route future MR 6 readiness or automatic durable routing hookup work into separately named OpenSpec changes after ownership precheck
