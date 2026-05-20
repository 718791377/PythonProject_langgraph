## ADDED Requirements

### Requirement: Feature worktrees SHALL carry task receipts and lifecycle metadata

The repository SHALL require every newly created feature worktree to carry task receipt metadata before writable work begins.

The metadata SHALL exist in two local-only surfaces:

- `.omx/session-claims/<session>.json` for session ownership and conflict checks.
- `.omx/worktree-task-receipt.json` inside the worktree for quick resumed-session task identification.

Both surfaces SHALL record at least the worktree path, branch, creating or taking-over session, task name, task summary, document-plan-only flag, later-code-required flag, touched paths, next action, local-main merge requirement, remote-sync requirement, expected merge-or-pause point, and lifecycle status.

Allowed lifecycle statuses SHALL include `active`, `paused`, `ready-to-merge`, `merged-local-main`, `cleaned`, `remote-sync-needed`, `completed`, and `superseded`. Completed or cleaned worktrees SHALL carry completion receipt fields including rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status.

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
- **THEN** every registered feature worktree SHALL have a receipt and branch-matching claim
- **AND** missing metadata SHALL fail the check

### Requirement: OpenSpec guard SHALL include worktree task receipt verification

The aggregate repository OpenSpec guard SHALL run the worktree task receipt checker so local gate, remote mirrored CI, and pre-commit hook paths detect missing lifecycle metadata for current feature worktrees.

#### Scenario: Aggregate guard scans worktree receipts

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregated output SHALL include a `check_worktree_task_receipt` step
- **AND** the aggregate guard SHALL fail if the checker reports errors
