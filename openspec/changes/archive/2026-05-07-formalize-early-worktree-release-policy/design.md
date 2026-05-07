# Design

## Decision

Keep the policy split between two lifecycle objects:

1. Feature worktree: a temporary execution surface. It can be removed once local validation has passed and every file worth keeping is committed, moved, summarized, or explicitly discarded.
2. Feature branch: the publication carrier. It remains until the GitLab MR is merged, local `main` is fast-forwarded to the GitLab main commit, and GitHub `main` is synced to the same commit.

## Checker Behavior

`tools/check_worktree_session_hygiene.py` remains read-only. It reports a `worktree_release_candidates` array in JSON output. Each record distinguishes:

- `worktree_release_ready`: the worktree is on a non-main branch and has no tracked, untracked, or local-only dirty files.
- `branch_cleanup_ready`: the branch is merged into local `main`, local `main` matches `gitlab/main`, and `github/main` matches local `main`.

The checker does not delete worktrees or branches. It only gives cold-start sessions a script-backed status surface.

## File-Class Rule

The policy keeps file-class decisions outside automatic deletion. The operator must classify tracked files, untracked files, local evidence, caches, OCR output, private files, copyrighted files, and large files before releasing the worktree.

## Non-Goals

- Do not auto-delete worktrees.
- Do not auto-delete local or remote branches.
- Do not commit private, copyrighted, cache, OCR, or large evidence payloads as source truth.
