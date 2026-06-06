## MODIFIED Requirements

### Requirement: Feature worktrees SHALL carry task receipts and lifecycle metadata

The repository SHALL require every newly created feature worktree to carry task receipt metadata before writable work begins.

The metadata SHALL exist in two local-only surfaces:

- `.omx/session-claims/<session>.json` for session ownership and conflict checks.
- `.omx/worktree-task-receipt.json` inside the worktree for quick resumed-session task identification.

Both surfaces SHALL record at least the worktree path, branch, creating or taking-over session, task name, task summary, document-plan-only flag, later-code-required flag, touched paths, next action, local-main merge requirement, remote-sync requirement, expected merge-or-pause point, and lifecycle status.

Allowed lifecycle statuses SHALL include `active`, `paused`, `ready-to-merge`, `merged-local-main`, `cleaned`, `remote-sync-needed`, `completed`, `superseded`, and `stale`. `stale` and `superseded` SHALL classify residual or obsolete work without asserting local-main integration, cleanup, branch deletion, or remote publication. `merged-local-main`, `cleaned`, `remote-sync-needed`, and `completed` worktrees SHALL carry completion receipt fields including rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status.

Every runtime lifecycle transition SHALL append a transition-ledger entry that records owner, previous state, next state, transition timestamp, evidence paths, rollback ref when applicable, local-main commit when applicable, cleanup decision, reason when applicable, and remote-publication authorization status.

#### Scenario: Runtime helper advances active work to ready-to-merge

- **WHEN** the lifecycle helper advances a branch-matching receipt and claim from `active` to `ready-to-merge`
- **THEN** it SHALL update both local-only metadata surfaces
- **AND** it SHALL append a transition-ledger entry with owner, previous state, next state, timestamp, evidence paths, cleanup decision, and remote-publication authorization status
- **AND** it SHALL NOT mutate local `main` or any remote ref

#### Scenario: Runtime helper records local-main merge evidence

- **WHEN** the local-main flow records `ready-to-merge` to `merged-local-main`
- **THEN** the helper SHALL require rollback ref and local-main commit evidence
- **AND** it SHALL keep `remote_publication_authorized=false`
- **AND** completion fields SHALL satisfy the worktree task receipt checker

#### Scenario: Runtime helper records cleaned evidence

- **WHEN** guarded cleanup removes an integrated worktree and deletes its merged local branch
- **THEN** the preserved completed claim SHALL record `lifecycle_status=cleaned`
- **AND** it SHALL record removed worktree, deleted branch, rollback ref, local-main commit, and remote sync status
- **AND** it SHALL preserve cleanup evidence without deleting backup refs or remote refs

#### Scenario: Runtime helper records exceptional lifecycle states

- **WHEN** a worktree is paused, superseded, or marked stale before local-main integration
- **THEN** the helper SHALL require a reason or evidence path
- **AND** it SHALL append a transition-ledger entry
- **AND** it SHALL NOT require completion fields reserved for integration or cleanup states
