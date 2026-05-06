## MODIFIED Requirements

### Requirement: Repository SHALL provide a read-only worktree hygiene checker

The repository SHALL provide `tools/check_worktree_session_hygiene.py` as a read-only checker for multi-session repository hygiene.

The checker SHALL inspect registered Git worktrees and report at least:

- dirty `main` worktree state
- dirty current non-main worktree state
- dirty non-current worktree state
- duplicate dirty paths across worktrees
- primary directory versus local `main` alignment
- local `main` versus `gitlab/main` alignment

#### Scenario: Primary directory is aligned with local main

- **GIVEN** the primary registered worktree is checked out on local `main`
- **AND** the primary registered worktree HEAD matches the local `main` branch reference
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL report `primary_worktree_alignment` as ok
- **AND** it SHALL include the primary worktree path, branch, head, expected branch, and expected head in the JSON payload

#### Scenario: Primary directory is left on a feature branch

- **GIVEN** the primary registered worktree is checked out on a branch other than local `main`
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the failure SHALL explain that the primary directory must be checked out on local `main`
- **AND** the failure SHALL direct writable feature work to `.worktrees/`

#### Scenario: Primary directory HEAD differs from local main reference

- **GIVEN** the primary registered worktree is checked out on local `main`
- **AND** its HEAD differs from the local `main` branch reference
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the failure SHALL explain that the primary directory HEAD must match local `main`

#### Scenario: GitLab CI uses a detached checkout

- **GIVEN** the worktree hygiene checker runs inside GitLab CI
- **AND** the primary registered worktree is a detached HEAD checkout of the CI commit
- **WHEN** the worktree hygiene checker runs
- **THEN** it SHALL allow the detached checkout as an ephemeral CI workspace
- **AND** it SHALL not extend that tolerance to normal local sessions

### Requirement: Repository SHALL document primary directory alignment governance

The repository SHALL document that `D:\PythonProject_langgraph` is the primary directory for coordination and local mainline mirroring.

The primary directory SHALL stay checked out on local `main`, and its HEAD SHALL match the local `main` branch reference after feature-branch work, MR merge, cleanup, or release sync.

Writable feature work SHALL use secondary worktrees under `.worktrees/` instead of leaving the primary directory on a feature branch.

#### Scenario: A session finishes a merged feature branch

- **WHEN** a feature branch has been merged, cleaned up, or released
- **THEN** the session SHALL restore the primary directory to local `main`
- **AND** it SHALL verify that primary directory HEAD matches local `main`
- **AND** it SHALL not keep the primary directory on the old feature branch as an informal workspace
