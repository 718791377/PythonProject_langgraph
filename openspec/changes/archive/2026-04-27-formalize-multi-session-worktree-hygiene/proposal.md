## Why

Multiple Codex sessions can operate in this repository at the same time. If two sessions write to the same working directory, dirty files can be misattributed, useful local edits can be overwritten, and local `main` can drift from reviewed `gitlab/main`.

This change is needed because the repository now uses many dedicated Git worktrees for GitLab-first MRs, and the multi-session rule must be durable governance plus script control rather than a prompt-only reminder.

## What Changes

- Add a bilingual governance policy for multi-session Git worktree isolation.
- Register the governance policy in `docs_bilingual/docs_registry.yaml`.
- Add startup and AGENTS references so cold-start sessions know when to read the policy.
- Add `tools/check_worktree_session_hygiene.py`, a read-only checker for dirty `main`, dirty worktrees, duplicate dirty paths, and local `main` alignment.
- Add unit coverage for the checker and include it in `tools/run_openspec_guard.py`.
- Close the OpenSpec lifecycle by archiving this completed change into stable specs after validation.

## Capabilities

### New Capabilities

- `codex-repository-multi-session-worktree-isolation`: defines the governance and checker contract for safe multi-session repository editing.

### Modified Capabilities

- Repository OpenSpec guard sequence now includes the worktree session hygiene checker.

## Impact

impact_scope: Governance documents, startup references, OpenSpec change artifacts, a read-only checker, and guard/test integration.

explicit_non_goals: This change does not delete worktrees, reset branches, clean dirty files, push backup branches, or decide ownership of existing stale worktrees.

rollout_sequence:

1. Add the governance policy and register it.
2. Add the read-only checker and tests.
3. Add the checker to the OpenSpec guard sequence.
4. Validate with repository checkers and GitLab CI.
5. Archive the completed OpenSpec change so the worktree-isolation delta spec becomes stable repository contract.

rollback_plan: Revert this change if the policy or checker semantics are replaced. If the archive step itself is wrong, revert the archive commit or reopen an explicit replacement change. No local state mutation is performed by this change.

validation_path: Run `test/check_worktree_session_hygiene.test.py`, `test/run_openspec_guard_json.test.py`, `tools/check_document_governance_rules.py`, `tools/check_name_clarity_rules.py`, `tools/check_worktree_session_hygiene.py`, and `tools/run_openspec_guard.py`.

mainline_classification: Repository governance and safety-control change supporting current user-level orchestration work.
