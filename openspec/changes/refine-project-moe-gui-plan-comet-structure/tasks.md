## 1. Open / Design Artifacts

- [x] 1.1 Create full Comet/OpenSpec change `refine-project-moe-gui-plan-comet-structure`.
- [x] 1.2 Record proposal, design, management checklist and `.comet.yaml`.
- [x] 1.3 Record Windows bash unavailability as a Comet script-state blocker instead of fabricating transitions.
- [x] 1.4 Create delta spec `project-moe-agent-gui-plan-contract`.

## 2. Superpowers Artifacts

- [x] 2.1 Create design doc `docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md`.
- [x] 2.2 Create implementation plan `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`.

## 3. Document Refactor

- [x] 3.1 Rewrite `project_moe_agent_gui_toolchain_plan.zh-CN.md` into the full Comet executable-plan structure.
- [x] 3.2 Preserve Project MOE-specific contracts: Phase 1/Phase 2, Ready/Bootstrap/Repair lanes, target install boundaries, JSON state contracts and privacy rules.
- [x] 3.3 Add explicit readiness metadata and self-check checklist.

## 4. Verification

- [x] 4.1 Run `git diff --check`.
- [x] 4.2 Run `openspec validate refine-project-moe-gui-plan-comet-structure`.
- [x] 4.3 Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
- [x] 4.4 Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] 4.5 Run `python .\tools\run_openspec_guard.py --root .`.
- [ ] 4.6 Run `.\tools\ci\local_mr_review.ps1` after commit.
