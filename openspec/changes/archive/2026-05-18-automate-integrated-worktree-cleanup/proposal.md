# Proposal: automate integrated local worktree cleanup

## Why

The local-main-first workflow now aims to complete every safe pre-remote step without repeated authorization while preserving local traceability and rollback. The previous worktree policy kept local feature branches until remote publication closed, which left many completed worktrees and branches behind even after local `main` contained the work and rollback refs existed.

## What changes

- Add `tools/cleanup_integrated_worktree.py`, a guarded local-only cleanup helper for already-integrated feature worktrees and local feature branches.
- Require cleanup to prove the worktree is under `.worktrees/`, clean, merged into local `main`, has a completed claim, and has a local rollback backup ref.
- Preserve completed claim metadata into the primary directory before removing the feature worktree.
- Use only `git worktree remove` and `git branch -d`; do not delete backup refs, remote refs, or dirty files.
- Update the worktree hygiene checker, governance policy, and stable OpenSpec spec to make local cleanup pre-remote while remote publication remains separately approved.

## Safety

This change is local-only and guarded. Unsafe or incomplete state fails closed. Remote publication, force deletion, hard reset, backup-ref deletion, and remote-ref deletion remain outside default authorization.
