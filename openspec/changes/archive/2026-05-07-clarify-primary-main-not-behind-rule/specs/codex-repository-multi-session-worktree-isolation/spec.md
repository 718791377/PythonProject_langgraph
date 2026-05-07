## MODIFIED Requirements

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

The repository workflow SHALL keep local `main` from lagging behind `gitlab/main` before new writable work, release-timing judgment, push, MR creation or update, or mainline-state claims.

The primary directory `D:\PythonProject_langgraph` SHALL be the primary main worktree. It SHALL be checked out on local `main`, SHALL NOT lag behind the local `main` branch reference, and normally SHOULD exactly equal the local `main` branch reference.

Local-first batching SHALL NOT be used as permission to continue from a stale remote base.

#### Scenario: Local main is behind before writable work

- **GIVEN** `gitlab/main` has advanced
- **AND** local `main` is behind it
- **WHEN** a session prepares to create a new writable task branch
- **THEN** the session SHALL fast-forward local `main` before continuing
- **AND** the worktree hygiene checker SHALL fail until local `main` is no longer behind `gitlab/main`
- **AND** it SHALL not reset or discard dirty work as part of this freshness check

#### Scenario: Primary main worktree is not on local main

- **GIVEN** the primary directory `D:\PythonProject_langgraph` is not checked out on local `main`
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the session SHALL stop writable work until the primary directory hygiene issue is resolved

#### Scenario: Primary main worktree is behind local main

- **GIVEN** the primary directory `D:\PythonProject_langgraph` is checked out on local `main`
- **AND** its HEAD differs from the local `main` branch reference
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL fail
- **AND** the failure SHALL instruct the operator to check out or fast-forward the primary directory to local `main`

#### Scenario: Local main is ahead of gitlab main

- **GIVEN** refreshed `gitlab/main` is an ancestor of local `main`
- **WHEN** the worktree hygiene checker runs
- **THEN** the checker SHALL treat local `main` as not behind `gitlab/main`
- **AND** it SHALL remind the operator not to use the primary `main` worktree for feature work

#### Scenario: Feature branch was prepared on a stale base

- **GIVEN** a local feature branch is ready for release timing judgment
- **AND** refreshed `gitlab/main` shows the feature branch was prepared on a stale base
- **WHEN** the session evaluates publication readiness
- **THEN** it SHALL recommend rebasing or merging onto the refreshed base before publication
- **AND** it MAY proceed from the stale base only if the user explicitly accepts the risk

#### Scenario: Local repository is current

- **GIVEN** refreshed `gitlab/main` matches local `main`
- **WHEN** local validation and release-timing checks pass
- **THEN** the session MAY recommend remote publication
- **AND** GitLab pipeline success remains the merge gate
