# codex-user-level-mainline-memory-handoff Specification

## Purpose

Define how current mainline memory summaries keep cold-start handoffs aligned with the latest landed governance, checker, tooling, or workflow increment.
## Requirements
### Requirement: Mainline memory handoffs SHALL identify the latest landed increment

A current mainline memory summary SHALL identify the latest landed governance, checker, tooling, or workflow increment before it lists candidate next actions.

The handoff SHALL include:

- latest archived OpenSpec change name when applicable
- affected script, checker, or documentation path when applicable
- current active-change state
- whether the next session should reopen design or continue from implemented behavior
- current publication-ref alignment when the repository uses a GitLab-first plus GitHub mirror workflow
- policy routing pointers when the latest landed increment adds a new governance surface

#### Scenario: A new cold-start session resumes after a checker-backed increment landed

- **WHEN** a new session reads the current mainline memory summary
- **THEN** the summary SHALL identify the latest landed checker-backed increment
- **AND** it SHALL state whether there are active OpenSpec changes
- **AND** it SHALL list safe next-action choices without implying that older completed increments still need implementation

#### Scenario: A new cold-start session resumes after MCP scope policy work landed

- **WHEN** a new session reads the current mainline memory summary after the MCP scope policy and memory-handoff archive work have landed
- **THEN** the summary SHALL identify the latest landed MCP Router scope policy increment
- **AND** it SHALL identify whether active OpenSpec changes exist before recommending implementation
- **AND** it SHALL route MCP Router versus Codex-direct MCP questions to the stable MCP scope policy documents
- **AND** it SHALL avoid presenting already-landed replay or task-ownership increments as the next required implementation step

### Requirement: Mainline memory handoffs SHALL refresh after durable rollout status-sync archive work lands

Current mainline memory summaries SHALL be refreshed after repository publication lands a durable rollout status-sync archive that changes the safe next-action queue.

#### Scenario: Durable rollout status sync is archived after MR 5 is complete

- **WHEN** durable rollout status sync and archive closeout have landed on GitLab `main`
- **AND** GitHub `main` mirrors the same commit
- **THEN** the current mainline memory summary SHALL identify that status-sync archive as a latest landed increment
- **AND** it SHALL state that MR 5 helper mirror source-of-truth work is already completed
- **AND** it SHALL route future MR 6 readiness or automatic durable routing hookup work into separately named OpenSpec changes after ownership precheck
