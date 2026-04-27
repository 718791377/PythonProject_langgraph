# codex-repository-multi-session-worktree-isolation Specification

## Purpose

Protect repository work from cross-session dirty-file collisions by requiring dedicated Git worktrees, feature branches, and read-only hygiene checks.

## ADDED Requirements

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
