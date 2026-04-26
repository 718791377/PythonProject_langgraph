## Why

The local primary worktree is now aligned with `gitlab/main`, but the backup branch still contains 265 preserved local paths. Some of those paths are useful local documentation or name-clarity updates, while others are scratch notes or stale drift. The repository needs a controlled reconciliation queue so useful content can be migrated without making local `main` diverge from GitLab main.

## What Changes

- Add a bilingual implementation plan for reconciling backup-branch content with `gitlab/main`.
- Add a read-only reconciliation report script that classifies backup and target changes.
- Add generated bilingual inventory reports for the current backup branch.
- Define a staged MR queue for both-changed active docs, checker/test changes, local-only docs, and OpenSpec name-clarity batches.
- Keep scratch notes and nested local-only files out of main unless explicitly promoted.

## Capabilities

### New Capabilities

- `codex-repository-backup-reconciliation`: defines how preserved local backup changes are classified, reported, and migrated while local `main` remains aligned with `gitlab/main`.

### Modified Capabilities

- None.

## Impact

impact_scope: Documentation, OpenSpec change artifacts, one read-only report tool, one test file, and generated memory reports.

explicit_non_goals: This change does not merge the full backup branch, overwrite GitLab main, push the backup branch, or promote scratch notes into official documentation.

rollout_sequence:

1. Add the reconciliation implementation plan.
2. Add the OpenSpec contract and tasks.
3. Add the read-only report tool and test.
4. Generate bilingual inventory reports from the current backup branch.
5. Use later small MRs to migrate selected content from the backup branch.

rollback_plan: Revert this change if the reconciliation queue is replaced. The backup branch remains untouched and local `main` remains aligned with `gitlab/main`.

validation_path: Run the report tool test, implementation-plan checker, document-governance checker, name-clarity checker, OpenSpec validation, and OpenSpec guard.

mainline_classification: Cross-mainline repository maintenance issue. It supports ongoing user-level orchestration work by preventing local backup content from being lost or merged unsafely.
