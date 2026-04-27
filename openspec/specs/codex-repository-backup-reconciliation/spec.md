# codex-repository-backup-reconciliation Specification

## Purpose
TBD - created by archiving change reconcile-backed-up-main-worktree-updates. Update Purpose after archive.
## Requirements
### Requirement: Backup reconciliation SHALL preserve local main alignment

Repository reconciliation work SHALL keep the local `main` branch aligned with `gitlab/main` while useful backup content is migrated through separate feature branches.

#### Scenario: Reconciliation branch is created

- **WHEN** backup content needs to be reviewed
- **THEN** the workflow SHALL create a clean branch from `gitlab/main`
- **AND** the workflow SHALL NOT commit the restored backup content directly to local `main`

### Requirement: Backup reconciliation SHALL classify path categories

The reconciliation workflow SHALL classify paths as local-only, target-only, both-changed-different, both-changed-same, or already-equal before migration decisions are made.

#### Scenario: Inventory report is generated

- **WHEN** the reconciliation report tool compares the backup branch with `gitlab/main`
- **THEN** it SHALL report counts for local-only paths
- **AND** it SHALL report counts for target-only paths
- **AND** it SHALL report counts for both-changed-different paths
- **AND** it SHALL report counts for both-changed-same paths

### Requirement: Both-changed files SHALL be manually merged

Files that changed in both the backup branch and `gitlab/main` with different final content SHALL be treated as manual merge candidates.

#### Scenario: Both sides changed an active implementation plan

- **WHEN** an active implementation plan changed in both the backup branch and `gitlab/main`
- **THEN** the workflow SHALL preserve reviewed `gitlab/main` content
- **AND** the workflow SHALL add only still-valid backup content after review
- **AND** the workflow SHALL NOT replace the whole target file with the backup version

### Requirement: Scratch notes SHALL require explicit promotion

Root-level scratch notes and local tool residue SHALL remain outside main unless the operator explicitly promotes them into an approved documentation or tooling path.

#### Scenario: Scratch note is found in the backup branch

- **WHEN** a root-level scratch note exists only in the backup branch
- **THEN** the workflow SHALL leave it in the backup branch by default
- **AND** the workflow SHALL require an explicit destination before adding it to a merge request

