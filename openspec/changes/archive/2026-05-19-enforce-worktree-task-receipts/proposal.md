# Proposal: enforce worktree task receipts

## Why

Recent local-first work has left many residual feature worktrees whose purpose, ownership, and cleanup intent were not obvious from the filesystem alone. A resumed session must be able to identify whether a worktree is active, paused, ready to merge, already locally integrated, or safe to clean without relying on transient chat memory.

## What changes

- Add `tools/check_worktree_task_receipt.py` to scan registered feature worktrees for local task receipts and branch-matching session claims.
- Require new feature worktrees to record task name, branch, worktree path, session, document-plan-only state, code-implementation need, next action, merge/sync intent, and lifecycle status.
- Require completed or cleaned worktrees to preserve rollback ref, local-main commit, cleaned worktree path, deleted branch, and remote sync status.
- Integrate the checker into the aggregate OpenSpec guard and CI test manifest.
- Update bilingual governance policy and stable OpenSpec requirements so residual worktrees are listed separately from the main task and cannot be forgotten.

## Safety

The checker is read-only. Normal guard mode keeps legacy residual worktrees as warnings to avoid blocking unrelated cleanup, while strict mode can be used for a full residual-worktree migration. Remote refs, backup refs, resets, force deletion, and dirty-file cleanup remain outside this change.
