# Main Worktree Backup Reconciliation Plan

## Status

This active plan defines how to reconcile the preserved local backup branch with `gitlab/main` while keeping local `main` aligned to GitLab main.

## Problem

The local primary worktree has already been aligned to `gitlab/main`, but the backup branch `backup/mainworktree-dirty-before-main-align-20260426-234655` still contains local changes that may include useful name-clarity comments, documentation updates, checker updates, and scratch notes.

The repository must keep local `main` equal to `gitlab/main`, but it must not lose useful content from the backup branch. Therefore reconciliation must happen through clean feature branches and GitLab merge requests, not through direct merges into `main`.

## Goals

- Keep `main` - the local branch that mirrors GitLab main - aligned with `gitlab/main`.
- Preserve `backup/mainworktree-dirty-before-main-align-20260426-234655` - the local backup branch that stores the pre-alignment dirty worktree.
- Classify backup content into local-only, target-only, both-changed-different, and both-changed-same groups.
- Migrate useful local-only and both-changed-different content through small local-main-first integration packages.
- Prevent direct merge of the full backup branch into `main`.
- Keep scratch notes out of main until the operator explicitly chooses a documentation destination.

## Non-Goals

- Do not merge the whole backup branch.
- Do not commit `.worktrees/` - the local Git secondary-worktree container.
- Do not push the backup branch unless the operator explicitly requests a remote backup.
- Do not overwrite GitLab main with older backup content.
- Do not treat local scratch files as official documentation without review.

## Reconciliation Source and Target

- `backup/mainworktree-dirty-before-main-align-20260426-234655` - local backup branch containing the preserved dirty worktree content.
- `gitlab/main` - GitLab remote-tracking branch and upstream freshness baseline.
- `e0e0acb8c4d70d891a1b91c9628b38f567966dc3` - current GitLab main commit at the start of this plan.
- `81de0bbc2605915fb996446ac0fc15b3043092b3` - current local backup commit at the start of this plan.
- `afdbd34cc7ee71f3d7acf8000e030c571fa71be7` - shared comparison base used to classify backup and target changes.

## Phase 1: Inventory and Guardrails

Add `tools/report_main_worktree_reconciliation.py` - a read-only report script that compares backup content against `gitlab/main`.

The script must report:

- `local_only` - paths changed in the backup branch but not in `gitlab/main`.
- `target_only` - paths changed in `gitlab/main` but not in the backup branch.
- `both_changed_different` - paths changed on both sides with different final content.
- `both_changed_same_content` - paths changed on both sides but converged to the same final content.
- `local_changed_already_same_as_target` - paths that appear local but already match the target.

Generate:

- `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.md` - English reconciliation inventory report.
- `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.zh-CN.md` - Chinese reconciliation inventory report.

## Phase 2: Both-Changed Documentation Merge

Create `reconcile/active-docs-three-way-merge` - a clean branch from `gitlab/main` for active documentation merges.

Manually reconcile:

- `docs_bilingual/project_startup_summary.md` - English startup summary requiring both-side merge review.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup summary requiring both-side merge review.
- active implementation plans under `docs_bilingual/implementation_plans/` - active plans that changed in both backup and GitLab main.
- active governance files under `docs_bilingual/governance/` - governance documents that changed in both backup and GitLab main.

## Phase 3: Checker and Test Merge

Create `reconcile/checker-three-way-merge` - a clean branch from `gitlab/main` for tool and test reconciliation.

Manually reconcile:

- `tools/run_openspec_guard.py` - OpenSpec guard entry script that changed on both sides.
- `tools/check_name_clarity_rules.py` - name-clarity checker that exists in both backup and GitLab main with different content.
- `tools/name_clarity_baseline.json` - compatibility baseline for name-clarity findings.
- `test/run_openspec_guard_json.test.py` - guard JSON test that changed on both sides.

## Phase 4: Local-Only Bilingual Documentation Review

Create `reconcile/local-only-doc-name-clarity` - a clean branch from `gitlab/main` for local-only documentation updates.

Review local-only documentation files from the backup branch. Accept only changes that are still valid after the current GitLab main state is considered.

## Phase 5: OpenSpec Name-Clarity Batches

Create small branches named `reconcile/openspec-name-clarity-batch-<n>` - batch branches from `gitlab/main` for OpenSpec-only comment migration.

Each batch must:

- restore only a small OpenSpec folder set from the backup branch;
- verify the restored lines are purpose explanations, not stale behavioral changes;
- run `openspec validate --all` - full OpenSpec validation for specs and changes;
- run `python .\tools\check_name_clarity_rules.py --root . --json` - name-clarity checker for documentation and OpenSpec files.

## Phase 6: Scratch Note Disposition

The local scratch files remain only in the backup branch unless explicitly promoted:

- `commn_layer.md` - local note about legacy external provider and service layering.
- `reference.md` - local reference list for related legacy external tooling material.
- `rollout20260422.md` - local rollout transcript and research note.
- `.githooks/.githooks/pre-commit` - nested hook path that requires manual review before any reuse.
- `.trae/.ignore` - local Trae ignore file that should not become repository policy without review.

## Required Workflow for Every Reconciliation MR

```powershell
git fetch gitlab main
```

This command refreshes `gitlab/main` before creating a branch.

```powershell
git worktree add .worktrees/<name> -b <branch> gitlab/main
```

This command creates a clean isolated worktree from the latest GitLab main.

```powershell
git checkout backup/mainworktree-dirty-before-main-align-20260426-234655 -- <path>
```

This command restores one selected path or path group from the backup branch.

```powershell
python .\tools\run_openspec_guard.py --root . --tool codex --json
```

This command runs the repository OpenSpec guard before publication.

## Validation

The reconciliation queue is healthy when:

- local `main` and `gitlab/main` remain the same commit after every MR;
- every migrated path enters through a clean branch based on `gitlab/main`;
- both-changed files are manually merged rather than overwritten;
- local-only OpenSpec changes are batched and validated;
- scratch notes remain out of main unless explicitly promoted.
