## Context

The repository uses GitLab as the authoritative merge surface. GitHub is a post-merge mirror target. The primary local worktree can still lag behind `gitlab/main` when implementation work happens in isolated worktrees.

The current local state has three important properties:

- `gitlab/main` has newer reviewed commits.
- The primary worktree has local tracked modifications and untracked files.
- `.worktrees/` contains Git-registered secondary worktrees and must not be handled as disposable scratch content.

Therefore the safe design is to preserve first, align second, and migrate selected local content later.

## Goals / Non-Goals

**Goals:**

- document a reproducible backup-first alignment workflow
- make cold-start sessions distinguish remote-only, local-only, both-changed, and already-equal paths
- prevent `.worktrees/` from being committed or manually deleted
- preserve local work in a backup branch before resetting local `main`
- keep later local-content migration inside the GitLab-first workflow

**Non-Goals:**

- performing the reset as part of this change
- deciding which local scratch notes are worth publishing
- rewriting Git history
- pushing local backup branches by default
- changing GitLab-first publication rules

## Decisions

### Decision 1: Require a local backup branch before alignment

The workflow uses `backup/mainworktree-dirty-before-main-align-<timestamp>` as the backup branch pattern. This branch preserves tracked and selected untracked changes before the local `main` branch is reset.

Alternative considered:

- Run `git reset --hard gitlab/main` immediately.

Rejected because:

- it would lose local-only and both-changed content unless the operator had already backed it up elsewhere.

### Decision 2: Exclude `.worktrees/` from backup commits

The `.worktrees/` directory is a Git-managed secondary worktree container. It should be ignored locally and managed through `git worktree` commands, not committed as ordinary repository content.

Alternative considered:

- Commit `.worktrees/` into the backup branch.

Rejected because:

- it would store nested checkouts as ordinary files and can corrupt the operator's understanding of Git worktree ownership.

### Decision 3: Separate alignment from later content migration

The immediate alignment step should make local `main` match `gitlab/main`. Any local content that still matters should be restored later from the backup branch into a fresh feature branch.

Alternative considered:

- Merge all local edits directly into local `main` before alignment.

Rejected because:

- it would mix stale drift, scratch notes, and real updates without review.

### Decision 4: Keep GitHub out of the alignment decision

GitHub remains a mirror after GitLab main is green. The alignment target is `gitlab/main`, not `github/main`.

Alternative considered:

- Compare against both GitLab and GitHub before local alignment.

Rejected because:

- repository policy already defines GitLab as the authoritative review and merge surface.

## Risks / Trade-offs

- [Risk] The backup branch contains scratch or sensitive local files.
  - Mitigation: keep the backup local by default and do not push it unless the operator explicitly requests a remote backup.

- [Risk] A cold-start model deletes `.worktrees/` as an untracked folder.
  - Mitigation: document `.worktrees/` as a Git-managed container and add it to `.git/info/exclude`.

- [Risk] Both-changed files are forgotten after alignment.
  - Mitigation: restore selected paths from the backup branch through a later feature branch and GitLab MR.

- [Risk] The operator mistakes this documentation change for the reset itself.
  - Mitigation: state that this change only creates the plan and OpenSpec contract; the reset remains a separate confirmation-gated action.

## Migration Plan

1. Merge this plan and OpenSpec change through GitLab.
2. In a later user-confirmed step, create the backup branch in the dirty primary worktree.
3. Reset local `main` to `gitlab/main`.
4. Move any useful local-only or both-changed content through separate GitLab-first MRs.

## Open Questions

- Which local scratch notes should be promoted into `docs_bilingual/memory/` after the primary worktree is aligned?
- Which both-changed documentation files contain local additions not already represented on `gitlab/main`?
