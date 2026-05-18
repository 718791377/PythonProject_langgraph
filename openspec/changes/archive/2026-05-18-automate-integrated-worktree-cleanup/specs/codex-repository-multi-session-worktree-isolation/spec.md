## UPDATED Requirements

### Requirement: Integrated local feature cleanup SHALL be checker-backed

The repository SHALL treat a feature worktree and its local feature branch as temporary local execution surfaces after their result is integrated into local `main`.

A feature worktree and local feature branch MAY be cleaned automatically before remote publication only when a guarded helper proves that local `main` contains the feature branch result, the worktree is clean, all untracked or local-only artifacts have been classified, a completed claim has been preserved, and a local rollback backup ref exists under `refs/backup/local-main/*-before-<branch>`.

The cleanup helper SHALL use Git worktree commands to remove the local `.worktrees/` worktree and `git branch -d` to delete the merged local branch. It SHALL NOT use force branch deletion, delete backup refs, delete remote refs, reset local `main`, discard dirty files, or mutate GitLab/GitHub publication state. Remote publication branches, remote refs, and backup refs remain separate approval boundaries.

#### Scenario: Clean integrated worktree and local branch are cleaned before remote publication

- **GIVEN** a feature worktree is clean
- **AND** local validation has passed
- **AND** tracked, untracked, local evidence, cache, OCR-output, private, copyrighted, and large-file artifacts have been classified
- **AND** local `main` contains the feature branch result
- **AND** a rollback backup ref exists for the pre-merge local `main`
- **AND** the completed claim has been preserved
- **WHEN** the cleanup helper runs with execute enabled
- **THEN** it MAY remove the local feature worktree and delete the merged local branch with `git branch -d`
- **AND** it SHALL leave remote refs and backup refs untouched

#### Scenario: Hygiene checker reports release and cleanup readiness separately

- **WHEN** the worktree hygiene checker runs
- **THEN** it SHALL report clean feature worktree release candidates
- **AND** it SHALL report local branch cleanup readiness based on local `main` containment and rollback backup ref presence
- **AND** it SHALL remain read-only

#### Scenario: Cleanup helper finds unsafe state

- **WHEN** a feature worktree is dirty, outside `.worktrees/`, not merged into local `main`, missing a completed claim, or missing a rollback backup ref
- **THEN** the cleanup helper SHALL fail closed
- **AND** it SHALL NOT remove the worktree or delete the local branch
