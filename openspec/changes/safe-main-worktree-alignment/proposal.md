## Why

The primary worktree can fall behind `gitlab/main` while still containing local edits from previous sessions. Aligning it with GitLab main without a preservation-first plan risks losing useful local work, committing registered worktree directories by mistake, or confusing stale local drift with reviewed mainline changes.

This change is needed now because the repository already uses GitLab as the authoritative review surface, while the primary local worktree currently contains both local-only changes and paths that changed on `gitlab/main`.

## What Changes

- Add a bilingual implementation plan for safe main-worktree alignment.
- Define a required backup-first workflow before any `git reset --hard` command is used.
- Define file classifications for remote-only, local-only, both-changed, and already-equal paths.
- State that `.worktrees/` is a Git-managed secondary worktree container and MUST NOT be committed or manually deleted.
- Require future restoration of local-only or both-changed content to happen through a clean branch and GitLab merge request.

## Capabilities

### New Capabilities

- `codex-repository-main-worktree-alignment-safety`: defines the repository maintenance contract for preserving dirty local work before aligning the primary worktree to `gitlab/main`.

### Modified Capabilities

- None.

## Impact

impact_scope: Documentation, OpenSpec change artifacts, and operator workflow guidance for the local `D:\PythonProject_langgraph` worktree.

explicit_non_goals: This change does not perform the alignment reset, delete files, remove worktrees, push backup branches, or decide which local-only content should enter a future MR.

rollout_sequence:

1. Add the bilingual implementation plan.
2. Add the OpenSpec change and spec requirement.
3. Validate documentation and OpenSpec guard checks.
4. After user confirmation in a later step, run the backup-first alignment workflow.

rollback_plan: Revert this documentation and OpenSpec change if the workflow is replaced. The actual worktree alignment operation remains gated behind a separate user confirmation.

validation_path: Run `tools/check_implementation_plan_rules.py`, `tools/check_document_governance_rules.py`, `tools/check_name_clarity_rules.py`, and `tools/run_openspec_guard.py`.

mainline_classification: Cross-mainline repository maintenance issue. It supports the active user-level orchestration and durable-state isolation work without changing runtime behavior.
