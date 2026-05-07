# Tasks

## 1. Governance Wording

- [x] 1.1 Update `AGENTS.md` with the archive-before-publication MR default.
- [x] 1.2 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md`.
- [x] 1.3 Update `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`.
- [x] 1.4 Update `docs_bilingual/governance/openspec_opsx_project_usage_policy.md`.
- [x] 1.5 Update `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md`.

## 2. OpenSpec Requirements

- [x] 2.1 Add a delta spec for the single-MR archive package default.
- [x] 2.2 Document two-MR exceptions and archive follow-up expectations.
- [x] 2.3 Keep the change class documentation/governance-scoped so archive evidence checks do not require new code evidence.

## 3. Validation

- [x] 3.1 Run `openspec validate prefer-archive-before-publication-mr`.
- [x] 3.2 Run `openspec validate --all`.
- [x] 3.3 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 If local validation passes and the change remains small, archive this change in the same branch and re-run validation.
