## Context

The safe alignment plan has already preserved the dirty primary worktree in `backup/mainworktree-dirty-before-main-align-20260426-234655` and aligned local `main` to `gitlab/main`.

The remaining problem is deciding which saved changes should enter main. Directly merging the backup branch is unsafe because it contains a mixture of:

- useful local name-clarity comments
- active documentation edits
- checker and test edits
- scratch notes
- possible stale OpenSpec refresh drift

The design therefore adds a read-only report tool and a staged reconciliation queue.

## Goals / Non-Goals

**Goals:**

- keep local `main` equal to `gitlab/main`
- preserve the backup branch as the recovery source
- generate a repeatable inventory of local-only, target-only, both-changed-different, and both-changed-same paths
- define small future MR slices for actual content migration
- make scratch-note disposition explicit

**Non-Goals:**

- merging every backup change in one MR
- deleting the backup branch
- pushing the backup branch
- deciding that all local-only OpenSpec changes are valid
- replacing GitLab-first publication rules

## Decisions

### Decision 1: Use a read-only report tool

`tools/report_main_worktree_reconciliation.py` compares a backup ref, a target ref, and their base ref. It writes JSON and optional Markdown reports without modifying Git state.

Alternative considered:

- Use ad hoc shell commands only.

Rejected because:

- the classification needs to be reproducible in cold-start sessions.

### Decision 2: Keep migration branches small

The queue separates both-changed documentation, checker/test changes, local-only documentation, and OpenSpec name-clarity batches.

Alternative considered:

- Restore all backup files onto a single branch.

Rejected because:

- it would mix scratch notes, stale drift, and valid updates in one review.

### Decision 3: Treat both-changed files as manual merges

Both-changed-different files must be merged by comparing base, backup, and `gitlab/main`. The backup version must not blindly overwrite the target version.

Alternative considered:

- Prefer the backup version for all both-changed files.

Rejected because:

- GitLab main includes newer reviewed changes that must be preserved.

### Decision 4: Keep scratch notes out of main by default

Scratch files such as `commn_layer.md`, `reference.md`, and `rollout20260422.md` stay in the backup branch until the operator explicitly promotes them into a proper memory or governance path.

Alternative considered:

- Commit scratch notes as root-level repository files.

Rejected because:

- root-level scratch files are not a stable documentation surface.

## Risks / Trade-offs

- [Risk] The inventory report becomes stale after new GitLab main merges.
  - Mitigation: the report tool can be rerun with the same backup ref and latest `gitlab/main`.

- [Risk] Local-only OpenSpec updates include stale refresh drift.
  - Mitigation: migrate OpenSpec updates in small batches and run OpenSpec validation for each batch.

- [Risk] Both-changed files lose target-side updates.
  - Mitigation: require manual three-way merge instead of backup overwrite.

- [Risk] The backup branch is accidentally deleted before reconciliation completes.
  - Mitigation: keep the backup branch local and reference it explicitly in the implementation plan and reports.
