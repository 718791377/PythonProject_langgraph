# codex-repository-main-worktree-alignment-safety Specification

## Purpose
TBD - created by archiving change safe-main-worktree-alignment. Update Purpose after archive.
## Requirements
### Requirement: Primary worktree alignment SHALL be backup-first

When the primary repository worktree contains local changes, the operator workflow SHALL create a recoverable local backup before any command that forces tracked files to match `gitlab/main`.

#### Scenario: Dirty worktree is aligned to GitLab main

- **WHEN** the primary worktree has tracked or untracked local changes
- **THEN** the workflow SHALL create a backup branch or equivalent recoverable backup before running `git reset --hard gitlab/main`
- **AND** the workflow SHALL report the backup location to the operator

### Requirement: Alignment planning SHALL classify local and remote changes

The alignment workflow SHALL classify affected paths before reset so the operator can distinguish remote-only, local-only, both-changed, and already-equal paths.

#### Scenario: Operator reviews alignment risk

- **WHEN** the operator asks how to align the primary worktree with `gitlab/main`
- **THEN** the workflow SHALL identify paths that changed only on `gitlab/main`
- **AND** the workflow SHALL identify paths that changed only locally
- **AND** the workflow SHALL identify paths that changed both locally and on `gitlab/main`
- **AND** the workflow SHALL identify paths that are locally dirty but already equal to `gitlab/main`

### Requirement: Registered worktrees SHALL NOT be treated as disposable untracked files

The alignment workflow SHALL treat `.worktrees/` as a local container for Git-managed secondary worktrees unless a read-only check proves otherwise.

#### Scenario: Worktree container appears in git status

- **WHEN** `.worktrees/` appears as an untracked path in the primary worktree
- **THEN** the workflow SHALL NOT delete it with ordinary filesystem cleanup
- **AND** the workflow SHALL NOT commit it as ordinary repository content
- **AND** the workflow SHALL require `git worktree list` or equivalent inspection before any worktree removal

### Requirement: Local-only recovery SHALL use a later GitLab-first branch

After the local `main` branch is aligned to `gitlab/main`, restored local-only or both-changed content SHALL be migrated through a separate feature branch and GitLab merge request.

#### Scenario: Operator wants to keep a local-only file after alignment

- **WHEN** a path preserved in the backup branch is selected for retention
- **THEN** the workflow SHALL restore only the selected path or logical slice into a clean branch based on `gitlab/main`
- **AND** the workflow SHALL validate that branch before opening a GitLab merge request
- **AND** the workflow SHALL NOT commit the restored content directly to local `main`

