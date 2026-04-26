## 1. Implementation plan

- [x] 1.1 Add `docs_bilingual/implementation_plans/main_worktree_gitlab_main_alignment_safety_plan.md` - English implementation plan for backup-first local main alignment.
- [x] 1.2 Add `docs_bilingual/implementation_plans/main_worktree_gitlab_main_alignment_safety_plan.zh-CN.md` - Chinese companion implementation plan for backup-first local main alignment.
- [x] 1.3 Update `docs_bilingual/docs_registry.yaml` - bilingual document registry that lets checkers find the new implementation plan.

## 2. OpenSpec change artifacts

- [x] 2.1 Add `openspec/changes/safe-main-worktree-alignment/proposal.md` - proposal explaining why the backup-first alignment contract is needed.
- [x] 2.2 Add `openspec/changes/safe-main-worktree-alignment/design.md` - design explaining how preservation, alignment, and later migration stay separate.
- [x] 2.3 Add `openspec/changes/safe-main-worktree-alignment/specs/codex-repository-main-worktree-alignment-safety/spec.md` - requirement delta for safe main-worktree alignment.
- [x] 2.4 Add `openspec/changes/safe-main-worktree-alignment/tasks.md` - implementation checklist for this change.

## 3. Verification

- [x] 3.1 Run `python .\tools\check_implementation_plan_rules.py --root . --json` - checker for bilingual implementation-plan registry integrity.
- [x] 3.2 Run `python .\tools\check_document_governance_rules.py --root . --json` - checker for governance document registry integrity.
- [x] 3.3 Run `python .\tools\check_name_clarity_rules.py --root . --json` - checker that prevents unexplained script, path, command, variable, and profile names.
- [x] 3.4 Run `python .\tools\run_openspec_guard.py --root . --tool codex --json` - repository OpenSpec guard for official OpenSpec validation and local policy checks.
