## ADDED Requirements

### Requirement: Feature Worktree Release SHALL Be Separate From Branch Cleanup

The repository SHALL treat a feature worktree as a temporary execution surface and a feature branch as the publication carrier. A clean, locally validated feature worktree MAY be released before remote publication, but the feature branch SHALL remain until the GitLab MR is merged, local `main` is aligned, and GitHub `main` is synced.

#### Scenario: Clean locally validated worktree is ready to release

- **GIVEN** all intended tracked changes are committed on the feature branch
- **AND** local validation has passed
- **AND** `git status` is clean for the feature worktree
- **AND** `.local/`, untracked files, local evidence, caches, OCR output, private files, copyrighted files, and large files have been committed, moved, summarized, or explicitly discarded according to their classification
- **WHEN** the operator wants to reduce local worktree clutter
- **THEN** the feature worktree may be removed with Git worktree commands
- **AND** removing the worktree does not delete the feature branch

#### Scenario: Feature branch cleanup waits for publication closure

- **GIVEN** a feature branch was used for a GitLab MR
- **WHEN** the GitLab MR has merged
- **AND** local `main` has fast-forwarded to the GitLab main commit
- **AND** GitHub `main` has synced to the same commit
- **THEN** the local and remote feature branches may be cleaned up
- **AND** branch cleanup must not happen merely because the feature worktree was released

#### Scenario: Hygiene checker reports cleanup readiness without deleting anything

- **WHEN** `tools/check_worktree_session_hygiene.py` runs
- **THEN** it reports clean feature worktree release candidates separately from branch cleanup readiness
- **AND** it remains read-only
- **AND** it lists blockers such as dirty files, an unmerged branch, stale local `main`, or unsynced GitHub mirror state
