# Tasks

## 1. Policy Wording

- [x] 1.1 Update `AGENTS.md` to use the primary-main-worktree freshness wording.
- [x] 1.2 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` with the English rule.
- [x] 1.3 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md` with the Chinese rule.
- [x] 1.4 Add `design.md`, the OpenSpec design for the freshness-chain checker behavior.

## 2. Script Control

- [x] 2.1 Update `tools/check_worktree_session_hygiene.py` so local `main` behind `gitlab/main` is an error.
- [x] 2.2 Keep local `main` ahead of `gitlab/main` as not-behind, while warning operators not to use primary `main` for feature work.
- [x] 2.3 Add unit tests for behind and ahead cases.

## 3. Validation

- [x] 3.1 Run `python test/check_worktree_session_hygiene.test.py`.
- [x] 3.2 Run `openspec validate clarify-primary-main-not-behind-rule`.
- [x] 3.3 Run `openspec validate --all`.
- [x] 3.4 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] 3.5 Run `git diff --check`.
