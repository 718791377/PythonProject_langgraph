## Why

The repository has now closed the broader automatic runtime-policy mainline. The implementation plan appendix and startup-facing repository summaries need another sync so they do not continue to frame that broader automatic-policy step as future work or current implementation work.

The next justified step is therefore a new capability-gap sync pass. The goal is not to add runtime behavior. The goal is to keep the repository's authoritative implementation-plan and startup-reading surfaces truthful after the archived broader automatic runtime-policy rollout.

## What Changes

- sync the bilingual LangGraph capability-gap appendix with the newly validated post-broader-automatic-policy state
- reclassify the broader automatic runtime-policy surface from active rollout to landed current state
- narrow the remaining future-work narrative to the real post-broader-automatic-policy gaps only
- update startup-facing repository summaries and current-mainline pointers so they no longer point at an already archived implementation mainline

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: clarify that the LangGraph capability-gap narrative and startup-facing summaries must stay aligned after the archived broader automatic-runtime-policy wave

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
  - this change does not re-open the archived broader automatic-runtime-policy implementation mainline
- validation_path:
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
