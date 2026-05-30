## MODIFIED Requirements

### Requirement: Feature worktrees SHALL carry task receipts and lifecycle metadata

The repository SHALL require every newly created feature worktree to carry task receipt metadata before writable work begins.

The metadata SHALL exist in two local-only surfaces:

- `.omx/session-claims/<session>.json` for session ownership and conflict checks.
- `.omx/worktree-task-receipt.json` inside the worktree for quick resumed-session task identification.

Both surfaces SHALL record at least the worktree path, branch, creating or taking-over session, task name, task summary, document-plan-only flag, later-code-required flag, touched paths, next action, local-main merge requirement, remote-sync requirement, expected merge-or-pause point, and lifecycle status.

Allowed lifecycle statuses SHALL include `active`, `paused`, `ready-to-merge`, `merged-local-main`, `cleaned`, `remote-sync-needed`, `completed`, `superseded`, and `stale`. `stale` and `superseded` SHALL classify residual or obsolete work without asserting local-main integration, cleanup, branch deletion, or remote publication. `merged-local-main`, `cleaned`, `remote-sync-needed`, and `completed` worktrees SHALL carry completion receipt fields including rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status.

#### Scenario: New feature worktree lacks a receipt

- **WHEN** `tools/check_worktree_task_receipt.py --root . --json` scans the current feature worktree
- **AND** that feature worktree lacks `.omx/worktree-task-receipt.json`
- **THEN** the checker SHALL fail
- **AND** it SHALL instruct the operator to create lifecycle metadata before continuing writable work

#### Scenario: Legacy residual worktrees lack receipts

- **WHEN** the worktree task receipt checker runs in normal guard mode
- **AND** older residual feature worktrees lack task receipts or branch-matching claims
- **THEN** the checker MAY report warnings rather than fail
- **AND** it SHALL summarize the residual worktree classification so cleanup work can classify or migrate them later

#### Scenario: Strict audit is requested

- **WHEN** the checker runs with `--require-all-feature-worktrees`
- **THEN** every registered non-main feature worktree SHALL have both a task receipt and a branch-matching claim
- **AND** the checker SHALL fail if any feature worktree is missing either surface

#### Scenario: Stale residual work is classified without completion evidence

- **WHEN** a worktree task receipt or branch-matching claim records lifecycle status `stale`
- **THEN** the worktree task receipt checker SHALL accept the status without requiring completion receipt fields
- **AND** it SHALL preserve the next action so the operator can classify, migrate, supersede, or clean the residue later

#### Scenario: Integration and completion states require completion evidence

- **WHEN** a worktree task receipt records `merged-local-main`, `cleaned`, `remote-sync-needed`, or `completed`
- **THEN** the worktree task receipt checker SHALL require completion fields for rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status
- **AND** it SHALL fail closed when those fields are absent or empty
