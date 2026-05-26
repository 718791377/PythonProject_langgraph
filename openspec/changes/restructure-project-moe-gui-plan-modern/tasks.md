## 1. Comet / OpenSpec Trace

- [x] 1.1 Create Comet/OpenSpec change `restructure-project-moe-gui-plan-modern`.
- [x] 1.2 Record Windows bash unavailability as a script-state blocker instead of fabricating Comet state transitions.

## 2. Document Rewrite

- [x] 2.1 Rewrite `project_moe_agent_gui_toolchain_plan.zh-CN.md` into the newer executable-plan structure.
- [x] 2.2 Preserve Project MOE-specific Phase 1/Phase 2 contracts, Ready/Bootstrap/Repair lanes, state model, install model, rollback, and validation rules.
- [x] 2.3 Add explicit readiness metadata and self-check checklist.

## 3. Verification

- [x] 3.1 Run `git diff --check`.
- [x] 3.2 Run `openspec validate restructure-project-moe-gui-plan-modern`.
- [x] 3.3 Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] 3.4 Run `python .\tools\run_openspec_guard.py --root .`.
- [x] 3.5 Run `.\tools\ci\local_mr_review.ps1` after commit.
