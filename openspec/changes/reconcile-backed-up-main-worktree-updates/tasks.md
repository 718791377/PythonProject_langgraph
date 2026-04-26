## 1. Planning artifacts

- [x] 1.1 Add `docs_bilingual/implementation_plans/main_worktree_backup_reconciliation_plan.md` - English implementation plan for backup branch reconciliation.
- [x] 1.2 Add `docs_bilingual/implementation_plans/main_worktree_backup_reconciliation_plan.zh-CN.md` - Chinese companion implementation plan for backup branch reconciliation.
- [x] 1.3 Update `docs_bilingual/docs_registry.yaml` - bilingual registry that makes the new implementation plan visible to checkers.

## 2. OpenSpec contract

- [x] 2.1 Add `openspec/changes/reconcile-backed-up-main-worktree-updates/proposal.md` - proposal for the backup reconciliation queue.
- [x] 2.2 Add `openspec/changes/reconcile-backed-up-main-worktree-updates/design.md` - design for read-only classification and staged migration.
- [x] 2.3 Add `openspec/changes/reconcile-backed-up-main-worktree-updates/specs/codex-repository-backup-reconciliation/spec.md` - requirement delta for safe backup reconciliation.
- [x] 2.4 Add `openspec/changes/reconcile-backed-up-main-worktree-updates/tasks.md` - task checklist for this change.

## 3. Report tooling and evidence

- [x] 3.1 Add `tools/report_main_worktree_reconciliation.py` - read-only report script for comparing a backup ref against `gitlab/main`.
- [x] 3.2 Add `test/report_main_worktree_reconciliation.test.py` - test coverage for local-only, target-only, both-changed-different, and both-changed-same classification.
- [x] 3.3 Generate `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.md` - English inventory report for the current backup branch.
- [x] 3.4 Generate `docs_bilingual/memory/main_worktree_backup_reconciliation_inventory_2026-04-27.zh-CN.md` - Chinese inventory report for the current backup branch.

## 4. Verification

- [x] 4.1 Run `python .\test\report_main_worktree_reconciliation.test.py` - unit test for the reconciliation report script.
- [x] 4.2 Run `python .\tools\check_implementation_plan_rules.py --root . --json` - implementation-plan registry checker.
- [x] 4.3 Run `python .\tools\check_document_governance_rules.py --root . --json` - governance registry checker.
- [x] 4.4 Run `python .\tools\check_name_clarity_rules.py --root . --json` - name-clarity checker for docs and OpenSpec files.
- [x] 4.5 Run `openspec validate --all` - full OpenSpec validation.
- [x] 4.6 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json` - repository OpenSpec guard.
