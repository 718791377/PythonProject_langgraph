## 1. OpenSpec Artifacts

- [x] 1.1 Create `proposal.md`, the OpenSpec proposal for primary directory local Git alignment.
- [x] 1.2 Create `design.md`, the OpenSpec design for checker-backed local main alignment.
- [x] 1.3 Create `specs/codex-repository-multi-session-worktree-isolation/spec.md`, the delta spec for the multi-session worktree isolation capability.

## 2. Governance Documents

- [x] 2.1 Update `AGENTS.md`, the repository startup instruction surface, with the primary directory alignment rule.
- [x] 2.2 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`, the English governance policy, with the primary directory alignment rule.
- [x] 2.3 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`, the Chinese governance companion, with the same rule.

## 3. Script Control

- [x] 3.1 Update `tools/check_worktree_session_hygiene.py`, the read-only worktree hygiene checker, to emit `primary_worktree_alignment`.
- [x] 3.2 Make `tools/check_worktree_session_hygiene.py` fail when the primary registered worktree is not on local `main`.
- [x] 3.3 Make `tools/check_worktree_session_hygiene.py` fail when the primary registered worktree HEAD does not match the local `main` branch reference.
- [x] 3.4 Update `test/check_worktree_session_hygiene.test.py`, the checker unit test file, with coverage for primary-directory alignment.
- [x] 3.5 Make `tools/check_worktree_session_hygiene.py` allow GitLab CI detached checkouts as ephemeral CI workspaces while preserving local-session failures.

## 4. Validation

- [x] 4.1 Run `python .\test\check_worktree_session_hygiene.test.py`, the unit test command for the worktree hygiene checker.
- [x] 4.2 Run `python .\tools\check_worktree_session_hygiene.py --root . --json`, the read-only worktree hygiene command; the new `primary_worktree_alignment` field passed, while dirty `main` correctly failed because this change is intentionally uncommitted.
- [x] 4.3 Run `openspec validate add-main-directory-local-git-alignment`, the OpenSpec validation command for this active change.
- [x] 4.4 Run `openspec validate --all`, the OpenSpec validation command for all active changes and stable specs.
- [x] 4.5 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`, the repository guard command; all other guard steps passed, while worktree hygiene correctly failed because this main-branch change is intentionally uncommitted.
- [x] 4.6 Run `python .\tools\check_name_clarity_rules.py --root . --json`, the name clarity checker command.
- [x] 4.7 Run `git diff --check`, the whitespace validation command.
