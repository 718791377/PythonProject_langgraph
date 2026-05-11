## REMOVED Requirements

### Requirement: Local-only recovery SHALL use a later GitLab-first branch

**Reason**: The recovery rule should require isolated feature-branch migration without making GitLab-first the publication authority.

**Migration**: Use `Local-only recovery SHALL use a later local-main-first feature branch`.

## ADDED Requirements

### Requirement: Local-only recovery SHALL use a later local-main-first feature branch

After the local `main` branch is aligned to the selected upstream baseline, restored local-only or both-changed content SHALL be migrated through a separate feature branch with local validation and local-main-first integration approval.

#### Scenario: Operator wants to keep a local-only file after alignment

- **WHEN** a path preserved in the backup branch is selected for retention
- **THEN** the workflow SHALL restore only the selected path or logical slice into a clean feature branch based on the selected baseline
- **AND** the workflow SHALL validate that branch before local `main` integration or remote publication
- **AND** the workflow SHALL NOT commit the restored content directly to local `main` without the local-main-first gate
