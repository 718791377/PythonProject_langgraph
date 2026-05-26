## ADDED Requirements

### Requirement: Local implementation flow SHALL proceed to the remote publication gate by default
For repository-local tasks that the user has already authorized for implementation, the repository SHALL treat the local flow as authorized through local `main` integration and guarded cleanup.

The local flow SHALL include feature worktree creation, session claim creation, local checks, local commit, local gate, local MR review, refreshed `gitlab/main` baseline check, local rollback backup ref creation, `git merge --ff-only` into local `main`, post-merge local gate, completed-claim preservation, and guarded cleanup of the integrated local feature worktree and local feature branch.

This default local authorization SHALL stop at the remote publication gate. It SHALL NOT authorize GitLab push, GitLab MR create/update/merge, GitHub sync, remote ref deletion, backup ref deletion, force push, reset, or destructive cleanup.

#### Scenario: Local package is ready
- **WHEN** a feature worktree has a clean validated local package and local `main` is not behind `gitlab/main`
- **THEN** the session MAY create the rollback backup ref and fast-forward the package into local `main` without another local-integration prompt
- **AND** it SHALL run the post-merge local gate before cleanup

#### Scenario: Local main leads remote after integration
- **WHEN** local `main` contains the integrated package and `gitlab/main` or `github/main` is behind
- **THEN** the session SHALL report intentional remote lag
- **AND** it SHALL stop before any remote publication mutation unless the current user message explicitly approves remote publication

### Requirement: Local commit subjects SHALL contain Chinese text
Repository-local feature commits SHALL use commit subjects that contain Chinese text. ASCII conventional prefixes are allowed only when the subject also contains Chinese text.

#### Scenario: Commit subject uses an ASCII prefix and Chinese body
- **WHEN** a local feature commit subject is `docs: <Chinese governance update>`
- **THEN** the commit-language checker SHALL pass

#### Scenario: Commit subject is ASCII-only
- **WHEN** a local feature commit subject is `docs: update governance rules`
- **THEN** the commit-language checker SHALL fail
- **AND** local MR review or the commit-msg hook SHALL require a Chinese subject before completion
