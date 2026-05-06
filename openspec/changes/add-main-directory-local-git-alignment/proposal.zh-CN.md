## Why

The repository root is the coordination and mainline mirror location, but previous work left the primary directory on old feature branches after merge or cleanup. That made cold-start sessions ask why the main directory was not aligned with the local repository state and increased the risk of writing new work in the wrong place.

The existing policy already says local `main` must not lag behind `gitlab/main`, but it does not separately enforce that the primary directory itself is checked out on local `main` and that its HEAD matches the local `main` branch reference. This change adds that explicit local alignment boundary.

## What Changes

- Document the primary directory alignment rule in `AGENTS.md` and the bilingual multi-session worktree isolation policy.
- Extend `tools/check_worktree_session_hygiene.py` so it reports `primary_worktree_alignment` and fails when the primary directory is not on local `main` or its HEAD does not match local `main`.
- Add tests that cover clean primary-directory alignment and a primary directory left on a feature branch.

## Capabilities

### Modified Capabilities

- `codex-repository-multi-session-worktree-isolation` - repository governance for multi-session worktree isolation, local mainline mirroring, and checker-backed worktree safety.

### New Capabilities

- None.

## Impact

- Affected paths:
  - `AGENTS.md` - repository startup instruction surface that summarizes publication and main-directory rules.
  - `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` - English governance policy for multi-session worktree isolation.
  - `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` - Chinese governance companion for multi-session worktree isolation.
  - `tools/check_worktree_session_hygiene.py` - read-only checker for worktree hygiene and main-directory alignment.
  - `test/check_worktree_session_hygiene.test.py` - unit tests for the worktree hygiene checker.
  - `openspec/changes/add-main-directory-local-git-alignment/` - OpenSpec change artifacts for this governance update.
- No destructive Git operations.
- No change to user-level Codex config.
- No change to remote publication behavior beyond clarifying local alignment before and after publication.
