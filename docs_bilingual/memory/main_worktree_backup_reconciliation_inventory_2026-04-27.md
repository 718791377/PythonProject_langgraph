# Main Worktree Backup Reconciliation Inventory

This report compares the local backup branch with `gitlab/main` so future work can migrate useful local-only or both-changed content without making local `main` drift from GitLab main.

## References / 引用

- `backup/mainworktree-dirty-before-main-align-20260426-234655^` - base reference used as the shared ancestor for comparison.
- `backup/mainworktree-dirty-before-main-align-20260426-234655` - local backup branch that preserved dirty main-worktree content.
- `gitlab/main` - target mainline reference that local `main` must match.

## Counts / 统计

- `both_changed_different` - Both changed differently / 双方都更新且内容不同: 18
- `both_changed_same_content` - Both changed to same content / 双方都更新但内容相同: 4
- `local_changed_already_same_as_target` - Local already same as target / 本地改动已等同目标: 0
- `local_only` - Local only / 仅本地备份有更新: 243
- `target_only` - Target only / 仅 gitlab/main 有更新: 57

## Non-OpenSpec paths requiring review / 需要复核的非 OpenSpec 路径

### `both_changed_different` - Both changed differently / 双方都更新且内容不同

- `docs_bilingual/governance/openspec_check_and_guard_json_output_policy.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/governance/openspec_check_and_guard_json_output_policy.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/governance/openspec_opsx_project_usage_policy.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/project_startup_summary.md` - Both changed differently / 双方都更新且内容不同.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Both changed differently / 双方都更新且内容不同.
- `test/run_openspec_guard_json.test.py` - Both changed differently / 双方都更新且内容不同.
- `tools/check_name_clarity_rules.py` - Both changed differently / 双方都更新且内容不同.
- `tools/name_clarity_baseline.json` - Both changed differently / 双方都更新且内容不同.
- `tools/run_openspec_guard.py` - Both changed differently / 双方都更新且内容不同.

### `local_only` - Local only / 仅本地备份有更新

- `.githooks/.githooks/pre-commit` - Local only / 仅本地备份有更新.
- `.trae/.ignore` - Local only / 仅本地备份有更新.
- `commn_layer.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/codex_user_level_skills_governance_policy.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/openspec_official_workflow_policy.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/openspec_official_workflow_policy.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/openspec_usage_convention.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/openspec_usage_convention.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/governance/solo_maintainable_production_persistent_team_research.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/codex_langgraph_repository_split_migration_plan.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/implementation_plans/general_template_phase0_update_patch_plan.zh-CN.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - Local only / 仅本地备份有更新.
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - Local only / 仅本地备份有更新.
- `reference.md` - Local only / 仅本地备份有更新.
- `rollout20260422.md` - Local only / 仅本地备份有更新.

### `target_only` - Target only / 仅 gitlab/main 有更新

- `AGENTS.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/docs_registry.yaml` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/governance/codex_skills_profile_launcher_mapping.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/governance/codex_skills_profile_launcher_mapping.zh-CN.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/governance/codex_skills_profiles.registry.yaml` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/governance/codex_skills_safe_cleanup_report.json` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/implementation_plans/main_worktree_gitlab_main_alignment_safety_plan.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/implementation_plans/main_worktree_gitlab_main_alignment_safety_plan.zh-CN.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.md` - Target only / 仅 gitlab/main 有更新.
- `docs_bilingual/memory/cross_project_durable_state_read_only_inventory_2026-04-25.zh-CN.md` - Target only / 仅 gitlab/main 有更新.
- `test/check_codex_skills_profile_launcher_mapping.test.py` - Target only / 仅 gitlab/main 有更新.
- `test/install-codex-user-level-team-mode.test.ps1` - Target only / 仅 gitlab/main 有更新.
- `test/report_codex_skills_cleanup_candidates.test.py` - Target only / 仅 gitlab/main 有更新.
- `tools/check_codex_skills_profile_launcher_mapping.py` - Target only / 仅 gitlab/main 有更新.
- `tools/current_repo_authority_language_rules.json` - Target only / 仅 gitlab/main 有更新.
- `tools/install-codex-user-level-team-mode.ps1` - Target only / 仅 gitlab/main 有更新.
- `tools/report_codex_skills_cleanup_candidates.py` - Target only / 仅 gitlab/main 有更新.

### `both_changed_same_content` - Both changed to same content / 双方都更新但内容相同

- `test/check_codex_skills_governance.test.py` - Both changed to same content / 双方都更新但内容相同.
- `test/check_name_clarity_rules.test.py` - Both changed to same content / 双方都更新但内容相同.
- `tools/check_codex_skills_governance.py` - Both changed to same content / 双方都更新但内容相同.

## OpenSpec local-only groups / OpenSpec 本地-only 分组

- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p5-automatic-team-routing` - contains 20 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p4-burst-review-agents` - contains 16 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p0-controls` - contains 12 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p2-team-entrypoints` - contains 12 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-14-implement-codex-user-level-team-mode-p6-windows-native-team-backend` - contains 12 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p1-startup-binding` - contains 8 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-13-implement-codex-user-level-team-mode-p3-routing-thresholds` - contains 8 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-15-implement-codex-user-level-team-mode-p6-windows-breakaway-worker-lifecycle` - contains 8 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-15-integrate-langgraph-durable-orchestration` - contains 8 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/audit-codex-skills-governance-phases` - contains 7 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-18-implement-langgraph-reusable-subgraph-library` - contains 6 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-18-implement-user-level-langgraph-quality-gated-loops` - contains 6 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-15-formalize-codex-native-subagent-and-omx-boundaries` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-15-implement-codex-user-level-team-mode-p7-startup-leader-protocol-binding` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-16-sync-codex-team-mode-plan-with-current-implementation` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-18-harden-langgraph-durable-artifacts` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-18-implement-langgraph-streaming-and-debug-observability-surface` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-native-subagent-boundaries` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-routing-thresholds` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-team-entrypoints` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-windows-native-team-backend` - contains 4 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-automatic-team-routing` - contains 3 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/formalize-analyst-fanout-first-routing-rule` - contains 2 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-langgraph-quality-gated-loops` - contains 2 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-mixed-persistent-pane-compose-recovery-semantics` - contains 2 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-burst-review-agents` - contains 2 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-team-mode-controls` - contains 2 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-18-implement-langgraph-command-driven-control-flow-and-parent-handoffs` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-compiled-stategraph-invocation-path` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-fuller-live-stategraph-primary-execution-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-generalized-live-stategraph-routing` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-graph-migration-and-thread-compatibility-guard` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-live-compiled-stategraph-execution-path` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-memory-store-and-semantic-memory` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-multi-interrupt-approval-queue` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-primary-runtime-stategraph-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-runtime-context-and-store-injection` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-stategraph-runtime-kernel` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-implement-langgraph-subgraph-persistence-modes-and-state-inspection` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-sync-langgraph-capability-gap-after-subgraph-persistence` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-19-sync-langgraph-capability-gap-with-current-implementation` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-approval-aware-live-primary-engine-resume-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-broader-automatic-runtime-policy-expansion` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-deeper-live-primary-engine-beyond-bounded-semantics` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-durable-artifact-aware-live-primary-engine-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-graph-resident-live-primary-engine-boundary-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-recovery-aware-live-primary-engine-provenance-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-richer-automatic-runtime-policies` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-stateful-live-primary-engine-beyond-superstep-trace` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-subgraph-aware-live-primary-engine-handoff-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-implement-langgraph-superstep-live-primary-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-approval-aware-live-primary-engine-resume-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-broader-automatic-runtime-policy-expansion` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-deeper-live-primary-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-fuller-live-primary-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-graph-resident-live-primary-engine-boundary-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-recovery-aware-live-primary-engine-provenance-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-richer-automatic-runtime-policies` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-stateful-live-primary-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-subgraph-aware-live-primary-engine-handoff-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-20-sync-langgraph-capability-gap-after-superstep-live-primary-engine` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-implement-langgraph-command-aware-live-primary-engine-control-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-implement-langgraph-memory-aware-live-primary-engine-semantic-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-implement-langgraph-migration-aware-live-primary-engine-compatibility-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-implement-langgraph-reducer-aware-live-primary-engine-merge-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-implement-langgraph-runtime-aware-live-primary-engine-context-store-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-sync-langgraph-capability-gap-after-command-aware-live-primary-engine-control-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-sync-langgraph-capability-gap-after-durable-artifact-aware-live-primary-engine-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-sync-langgraph-capability-gap-after-memory-aware-live-primary-engine-semantic-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-sync-langgraph-capability-gap-after-reducer-aware-live-primary-engine-merge-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/archive/2026-04-21-sync-langgraph-capability-gap-after-runtime-aware-live-primary-engine-context-store-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/implement-user-level-cross-session-durable-state-isolation` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/changes/sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-inspectable-team-state-surface` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-langgraph-reusable-subgraph-library` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/codex-user-level-langgraph-streaming-and-debug-observability-surface` - contains 1 local-only OpenSpec path(s) to review before migration.
- `openspec/specs/langgraph-durable-orchestration-backend` - contains 1 local-only OpenSpec path(s) to review before migration.

## Recommended next steps / 推荐下一步

- `reconcile/active-docs-three-way-merge` - use a clean branch from `gitlab/main` to merge the both-changed active documentation files.
- `reconcile/checker-three-way-merge` - use a clean branch from `gitlab/main` to merge checker and test updates.
- `reconcile/local-only-doc-name-clarity` - use a clean branch from `gitlab/main` to review local-only bilingual documentation updates.
- `reconcile/openspec-name-clarity-batch-*` - use small batches from `gitlab/main` to migrate confirmed OpenSpec name-clarity comments.
