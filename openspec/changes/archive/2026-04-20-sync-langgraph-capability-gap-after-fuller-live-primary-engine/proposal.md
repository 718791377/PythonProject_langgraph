## Why

The repository has now closed the fuller live `StateGraph` primary execution-engine mainline. That means the canonical plan-layer narrative is stale again: the implementation plan appendix and startup-facing repository summaries still treat the fuller live-engine step as pending rather than archived and landed.

The next justified step is therefore another capability-gap sync pass. The goal is not to add runtime behavior. The goal is to keep the repository's authoritative implementation-plan and startup-reading surfaces truthful after the archived fuller live-engine rollout.

## What Changes

- Sync the bilingual LangGraph capability-gap appendix with the newly validated post-fuller-engine state.
- Reclassify the fuller live primary execution-engine surface from active rollout to landed current state.
- Narrow the remaining future-work narrative to the real post-fuller-engine gaps only.
- Update startup-facing repository summaries and current-mainline pointers so they no longer point at an already archived implementation mainline.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: clarify that the LangGraph capability-gap narrative and startup-facing summaries must stay aligned after the archived fuller live-engine wave

## Impact

- impact_scope:
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
  - `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`
  - `docs_bilingual/project_startup_summary.md`
  - `docs_bilingual/project_startup_summary.zh-CN.md`
  - `README.md`
  - `AGENTS.md`
  - `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md`
- explicit_non_goals:
  - this change does not add new LangGraph runtime capabilities
  - this change does not modify backend-selection policy or operator command surfaces
  - this change does not re-open the archived fuller live-engine implementation mainline
- validation_path:
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
