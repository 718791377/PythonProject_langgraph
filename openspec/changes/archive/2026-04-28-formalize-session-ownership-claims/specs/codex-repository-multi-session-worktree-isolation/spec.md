## ADDED Requirements

### Requirement: Sessions SHALL declare active ownership claims before dirty feature work

The repository SHALL provide a local session-ownership claim mechanism for write tasks that may overlap with other Codex sessions.

Claim files SHALL live under `.omx/session-claims/`, which is a local ignored coordination directory and not durable `.omx/state/` runtime truth.

#### Scenario: Dirty feature worktree has no active claim

- **WHEN** a current non-main feature worktree has uncommitted changes
- **AND** the session ownership checker runs with `--allow-current-dirty`
- **AND** no active claim exists for the current worktree
- **THEN** the checker SHALL fail
- **AND** it SHALL explain that the session must declare its OpenSpec change or path ownership before continuing

### Requirement: Session claims SHALL prevent duplicate OpenSpec change ownership

The repository SHALL provide `tools/check_session_ownership_claims.py` as a read-only checker for active session-ownership claims.

The checker SHALL inspect registered Git worktrees and fail when two active claims own the same OpenSpec change.

#### Scenario: Two sessions claim the same OpenSpec change

- **WHEN** two active claim files declare the same OpenSpec change name
- **THEN** the checker SHALL return a non-zero exit code
- **AND** it SHALL report both claim files so the operator can serialize ownership

### Requirement: Session claims SHALL prevent overlapping hotspot path ownership

The session ownership checker SHALL fail when two active claims declare overlapping repository-relative path scopes.

#### Scenario: Two claims overlap on the same path scope

- **WHEN** one active claim owns `openspec/changes/example`
- **AND** another active claim owns `openspec/changes/example/tasks.md`
- **THEN** the checker SHALL treat the scopes as overlapping
- **AND** it SHALL fail with an operator-facing collision report

### Requirement: OpenSpec guard SHALL include session ownership verification

The repository OpenSpec guard SHALL run the session ownership checker as part of standard local verification.

#### Scenario: Clean CI clone has no local session claims

- **WHEN** `python tools/run_openspec_guard.py --root . --tool codex --json` runs in a clean clone
- **AND** no local `.omx/session-claims/` directory exists
- **THEN** the guard SHALL pass this checker step
- **AND** it SHALL still fail if duplicate active claims are present in registered local worktrees
