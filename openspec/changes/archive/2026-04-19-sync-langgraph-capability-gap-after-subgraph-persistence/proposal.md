## Why

The repository has now closed both the generalized live-routing mainline and the subgraph persistence or state-inspection mainline. That means the canonical plan-layer narrative is stale again: the bilingual implementation plan and startup-facing repository summaries still describe those surfaces as pending or currently active rather than archived and landed.

The next justified step is therefore a new capability-gap sync pass. The goal is not to add runtime behavior. The goal is to make the repository's authoritative plan and startup surfaces truthful again before any later LangGraph-deepening candidate is opened.

## What Changes

- Sync the bilingual LangGraph capability-gap appendix with the newly validated post-subgraph-persistence implementation state.
- Reclassify generalized live-routing and subgraph persistence or state-inspection from active rollout to landed current state.
- Narrow the remaining future-work narrative to only the real post-queue gaps.
- Update startup-facing repository summaries and current-mainline pointers so they no longer point at an already archived implementation mainline.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: clarify that the LangGraph capability-gap narrative and startup-facing summaries must stay aligned after each closed LangGraph-deepening wave

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
  - this change does not re-open already archived LangGraph implementation mainlines
- validation_path:
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
