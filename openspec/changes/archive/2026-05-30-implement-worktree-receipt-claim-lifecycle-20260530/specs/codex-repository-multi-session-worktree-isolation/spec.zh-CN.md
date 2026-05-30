## MODIFIED Requirements - zh-CN companion

### Requirement: Feature worktrees carry task receipts and lifecycle metadata

This companion mirrors the archived English delta. The lifecycle status set is `active`, `paused`, `ready-to-merge`, `merged-local-main`, `cleaned`, `remote-sync-needed`, `completed`, `superseded`, and `stale`. `stale` and `superseded` are classification states and do not assert merge, cleanup, branch deletion, or remote publication. `merged-local-main`, `cleaned`, `remote-sync-needed`, and `completed` require completion receipt fields.

#### Scenario: Strict audit is requested
- **WHEN** the checker runs with `--require-all-feature-worktrees`
- **THEN** every registered non-main feature worktree SHALL have both a task receipt and a branch-matching claim
- **AND** missing metadata SHALL fail the check

#### Scenario: Stale residual work is classified without completion evidence
- **WHEN** a receipt or branch-matching claim records lifecycle status `stale`
- **THEN** the checker SHALL accept it without completion receipt fields
- **AND** the next action remains available for later operator triage

#### Scenario: Integration and completion states require completion evidence
- **WHEN** a receipt records `merged-local-main`, `cleaned`, `remote-sync-needed`, or `completed`
- **THEN** the checker SHALL require rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status
- **AND** missing or empty fields SHALL fail closed
