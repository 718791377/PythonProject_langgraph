# codex-repository-multi-session-worktree-isolation Specification

## Purpose
Define how concurrent Codex sessions isolate writable work with dedicated Git worktrees, local ownership claims, and read-only guard scripts so sessions do not overwrite each other or treat unknown dirty files as disposable.
## Requirements
### Requirement: Repository SHALL document multi-session worktree isolation governance

The repository SHALL provide an active bilingual governance policy for multi-session worktree isolation.

At minimum, the policy SHALL define:

- `main` - local branch that mirrors reviewed GitLab mainline.
- `gitlab/main` - remote-tracking reference for the authoritative GitLab mainline.
- `.worktrees/` - local container for secondary Git worktrees.
- `backup/*` - branch namespace for preserving dirty worktree snapshots before risky alignment.

#### Scenario: Cold-start session receives a dirty-file question

- **WHEN** a cold-start Codex session is asked about dirty files, multiple sessions, Git worktrees, local `main`, or GitLab/GitHub sync safety
- **THEN** it SHALL read the multi-session worktree isolation governance policy before recommending cleanup
- **AND** it SHALL not recommend deleting or resetting unknown dirty files before ownership is known

### Requirement: Repository SHALL provide a read-only worktree hygiene checker

The repository SHALL provide `tools/check_worktree_session_hygiene.py` as a read-only checker for multi-session repository hygiene.

The checker SHALL inspect registered Git worktrees and report at least:

- dirty `main` worktree state
- dirty current non-main worktree state
- dirty non-current worktree state
- duplicate dirty paths across worktrees
- local `main` versus `gitlab/main` alignment

#### Scenario: Main worktree is dirty

- **WHEN** the local `main` worktree contains uncommitted changes
- **THEN** the checker SHALL fail
- **AND** the failure SHALL explain that changes must be preserved or moved before aligning `main`

#### Scenario: Current feature worktree is intentionally dirty

- **WHEN** the current worktree is on a non-main feature branch
- **AND** `--allow-current-dirty` is provided
- **THEN** the checker MAY pass for the current worktree dirty state
- **AND** it SHALL still check dirty `main` and duplicate dirty path risks

#### Scenario: Multiple worktrees contain the same dirty path

- **WHEN** two or more registered worktrees contain uncommitted changes to the same repository-relative path
- **THEN** the checker SHALL fail
- **AND** the failure SHALL instruct the operator to serialize ownership before continuing

### Requirement: OpenSpec guard SHALL include worktree hygiene verification

The repository OpenSpec guard SHALL run the worktree hygiene checker.

#### Scenario: Local validation runs before feature-branch commit

- **WHEN** `tools/run_openspec_guard.py` runs locally
- **THEN** it SHALL call `tools/check_worktree_session_hygiene.py` with `--allow-current-dirty`
- **AND** it SHALL still fail when dirty `main` or duplicate dirty path risks are detected

### Requirement: Completed worktree-isolation changes SHALL be archived

Completed OpenSpec changes that add or modify repository multi-session worktree isolation behavior SHALL be archived after implementation and validation so their delta requirements become stable specs.

#### Scenario: Worktree-isolation change is complete

- **WHEN** the governance policy, checker, tests, and guard integration are implemented
- **AND** the change tasks are complete
- **THEN** the change SHALL be archived before the repository treats the work as closed
- **AND** the stable spec SHALL exist under `openspec/specs/`

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
