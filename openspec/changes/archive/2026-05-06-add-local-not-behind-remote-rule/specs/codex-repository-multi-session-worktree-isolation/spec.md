## ADDED Requirements

### Requirement: Local Repository SHALL Not Lag The Authoritative Remote Before Work Or Publication

The repository workflow SHALL keep local `main` from lagging behind `gitlab/main` before new writable work, release-timing judgment, push, MR creation, or local alignment claims.

Local-first batching SHALL NOT be used as permission to continue from a stale remote base.

#### Scenario: Local main is behind before writable work

- **GIVEN** `gitlab/main` has advanced
- **AND** local `main` is behind it
- **WHEN** a session prepares to create a new writable task branch
- **THEN** the session SHALL fast-forward local `main` before continuing
- **AND** it SHALL not reset or discard dirty work as part of this freshness check

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
