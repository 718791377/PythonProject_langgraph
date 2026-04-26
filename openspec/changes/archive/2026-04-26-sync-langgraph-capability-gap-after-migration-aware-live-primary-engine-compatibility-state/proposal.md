## Why

The repository has now closed the migration-aware live primary-engine compatibility-state mainline. The implementation plan appendix and startup-facing repository summaries need another sync so they do not continue to frame that migration-aware step as current implementation work.

The next justified step is therefore a new capability-gap sync pass. The goal is not to add runtime behavior. The goal is to keep the repository's authoritative implementation-plan and startup-reading surfaces truthful after the archived migration-aware live-engine rollout.

## What Changes

- sync the bilingual LangGraph capability-gap appendix with the newly validated post-migration-aware state
- reclassify the migration-aware live primary-engine surface from active rollout to landed current state
- narrow the remaining future-work narrative to the real post-migration-aware gaps only
- update startup-facing repository summaries and current-mainline pointers so they no longer point at an already archived implementation mainline

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: clarify that the LangGraph capability-gap narrative and startup-facing summaries must stay aligned after the archived migration-aware live-engine wave

## Impact

- impact_scope:
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - English active implementation plan carrying the LangGraph capability-gap appendix.
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - Chinese companion for the active team-mode implementation plan.
  - `docs_bilingual/project_startup_summary.md` - English cold-start summary that names the current repository mainline.
  - `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese cold-start companion for the repository startup summary.
  - `README.md` - repository landing page that should not point at stale implementation state.
  - `AGENTS.md` - Codex instruction surface that records current mainline and routing boundaries.
  - `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` - stable spec receiving the plan-status-sync requirement.
- explicit_non_goals:
  - this change does not add new LangGraph runtime capabilities
  - this change does not modify backend-selection policy or operator command surfaces
  - this change does not re-open the archived migration-aware implementation mainline
- validation_path:
  - `openspec validate --all` - official OpenSpec validation command for all specs and active changes.
  - `python .\\tools\\run_openspec_guard.py --root .` - repository guard that aggregates OpenSpec and governance checks.
