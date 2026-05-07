# formalize-early-worktree-release-policy

## Why

Completed feature worktrees currently tend to remain until remote publication is fully complete. That is safe but keeps local execution surfaces open longer than necessary and can make multi-session coordination noisier. The repository needs a clearer rule that separates releasing a clean validated feature worktree from deleting the feature branch that still carries the publication state.

## What Changes

- Document that a feature worktree may be removed after local validation passes and all files worth keeping are committed, moved, summarized, or explicitly discarded.
- Document that local and remote feature branches must remain until the GitLab MR is merged, local `main` is fast-forwarded, and GitHub `main` is synced.
- Document file-class cleanup rules for tracked files, untracked files, local evidence, caches, OCR output, private files, copyrighted files, and large files.
- Extend the worktree hygiene checker so cold-start sessions can see clean feature worktree release candidates separately from branch cleanup readiness.

## Capabilities

- codex-repository-multi-session-worktree-isolation

## Impact

- Governance: `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`, the English worktree isolation policy.
- Governance: `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`, the Chinese companion policy.
- Checker: `tools/check_worktree_session_hygiene.py`, the read-only Git worktree hygiene checker.
- Tests: `test/check_worktree_session_hygiene.test.py`, the unit tests for the worktree hygiene checker.
