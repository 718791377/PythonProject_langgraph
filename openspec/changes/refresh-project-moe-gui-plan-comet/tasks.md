## 1. Comet Artifact Setup

- [x] 1.1 Create lightweight OpenSpec change `refresh-project-moe-gui-plan-comet` for the Comet-requested documentation tweak.
- [x] 1.2 Record proposal, design, and minimal delta spec for traceability because the current Windows shell cannot execute Comet `bash` scripts.

## 2. Plan Refresh

- [x] 2.1 Update `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md` with Comet/cold-start continuation facts.
- [x] 2.2 Preserve `status: draft` and target-project readiness gates.

## 3. Verification

- [x] 3.1 Run `git diff --check`.
- [x] 3.2 Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] 3.3 Run `python .\tools\run_openspec_guard.py --root .`.
- [x] 3.4 Run `.\tools\ci\local_mr_review.ps1` after commit.
