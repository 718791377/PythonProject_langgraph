# Design: Local-first runner budget policy

## Policy Shape

GitLab-first remains the authoritative remote integration path. The new rule changes the timing of remote publication, not the authority order.

The local-first sequence is:

1. Prepare work on a feature branch and dedicated worktree.
2. Commit and validate locally.
3. Batch related small changes only when they share one review topic and rollback boundary.
4. Push to GitLab only after local validation passes, unless the user asks for an early remote pipeline check.
5. Merge only after GitLab pipeline success.
6. Sync the exact GitLab main commit to GitHub.

## Placement

The rule belongs in:

- `AGENTS.md` - the repository instruction surface read by Codex sessions.
- `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md` - cold-start summaries.
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` and `.zh-CN.md` - the governance authority for Git worktrees, branches, GitLab main, and GitHub sync safety.

## Safety Boundary

The rule reduces runner usage but must not hide review risk. Unrelated topics still require separate MRs because rollback safety and reviewability take priority over runner-minute savings.
