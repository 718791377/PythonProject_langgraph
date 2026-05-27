## 1. Open / Design Artifacts

- [x] 1.1 Create full Comet/OpenSpec change `refine-project-moe-gui-plan-comet-structure`.
- [x] 1.2 Record proposal, design, management checklist and `.comet.yaml`.
- [x] 1.3 Record Windows bash unavailability as a Comet script-state blocker instead of fabricating transitions.
- [x] 1.4 Create delta spec `project-moe-agent-gui-plan-contract`.

## 2. Superpowers Artifacts

- [x] 2.1 Create design doc `docs/superpowers/specs/2026-05-27-project-moe-gui-plan-comet-design.md`.
- [x] 2.2 Create implementation plan `docs/superpowers/plans/2026-05-27-refine-project-moe-gui-plan-comet-structure.md`.

## 3. Document Refactor

- [x] 3.1 Rewrite `project_moe_agent_gui_toolchain_plan.md` and `.zh-CN.md` into the full Comet executable-plan structure.
- [x] 3.2 Preserve Project MOE-specific contracts: Phase 1/Phase 2, Ready/Bootstrap/Repair lanes, target install boundaries, JSON state contracts and privacy rules.
- [x] 3.3 Add explicit readiness metadata and self-check checklist.
- [x] 3.4 Align with `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` structure: review conclusion, relationship model, goals/non-goals, runtime architecture, source of truth, install artifacts, CLI/JSON/state contracts, gates, rollback, risks and self-check.
- [x] 3.5 Align with `comet_runtime_agile_focus_area_plan.zh-CN.md` semantics: management record, phase gates, Monitoring return semantics, implementation slices, file ownership map, local integration order and evidence retention.
- [x] 3.6 Repair the Chinese OpenSpec/Superpowers support artifacts for this change so they are valid UTF-8 Chinese instead of mojibake/question-mark placeholders.

## 4. Verification

- [x] 4.1 Run `git diff --check`.
- [x] 4.2 Run `openspec validate refine-project-moe-gui-plan-comet-structure`.
- [x] 4.3 Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
- [x] 4.4 Run `python .\tools\check_precommit_update_archive.py --root . --json`.
- [x] 4.5 Run `python .\tools\run_openspec_guard.py --root .`.
- [ ] 4.6 Keep the feature worktree clean and commit the current implementation on the feature branch.
- [ ] 4.7 Run `.\tools\ci\local_gate.ps1` and `.\tools\ci\local_mr_review.ps1` after commit.

## 5. Guarded Uninstall Apply Implementation

- [x] 5.1 Implement `plan_project_moe_gui_uninstall.py --apply` so it deletes only allowlisted Project MOE GUI managed files after manifest hash verification.
- [x] 5.2 Fail closed before deletion when the manifest lists non-allowlisted paths, missing hashes, hash mismatches, or directory entries.
- [x] 5.3 Update Project MOE GUI tests for successful apply, private-file preservation, and allowlist failure.
- [x] 5.4 Update the Project MOE GUI plan and operations document to replace the old apply-not-supported contract with the guarded apply contract.
- [ ] 5.5 Re-run targeted Project MOE tests, repository guards, local gate, and local MR review before local `main` integration.
