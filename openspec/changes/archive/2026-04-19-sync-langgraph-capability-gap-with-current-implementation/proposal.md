## Why

The repository has now landed the initial queued LangGraph deepening mainlines, but the canonical bilingual implementation plan still describes several already-implemented LangGraph surfaces as if they were only planned. That mismatch now creates avoidable confusion in startup reading, roadmap interpretation, and future mainline selection.

## What Changes

- Sync the bilingual LangGraph capability-gap appendix with the current validated implementation state.
- Reclassify already-landed LangGraph surfaces from “still planned” to “implemented current state”.
- Narrow the remaining “still in plan” section to the real post-queue gaps rather than already-shipped surfaces.
- Update startup-facing repository narrative so it no longer points at the sync pass as still pending after the sync is completed.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `codex-user-level-team-mode-plan-status-sync`: clarify that LangGraph capability-gap narrative and startup-facing summaries must reflect the validated implemented state rather than stale plan-era wording

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
  - this change does not change backend-selection policy or operator command surfaces
  - this change does not relitigate already-accepted implementation contracts
- rollout_sequence:
  1. define the sync change and spec delta
  2. update bilingual implementation-plan narrative to match validated current state
  3. update startup-facing repository summaries to remove stale “sync still pending” posture
  4. validate OpenSpec and archive the sync change
- rollback_plan:
  - revert only the documentation and spec-sync edits introduced by this change
  - keep the already-implemented LangGraph runtime, installer, and tests untouched
- validation_path:
  - `openspec validate --all`
  - `python .\\tools\\run_openspec_guard.py --root .`
- mainline_classification:
  - cross-surface documentation and plan-status alignment for the existing Codex orchestration mainline
