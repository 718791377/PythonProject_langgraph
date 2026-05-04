## Why

The active plans now name `R0.6 Durable Routing Smoke Gate` as the next release slice, but the path from R0.6 to `R2.0 Production Durable Team` is still too coarse. A future cold-start session needs a finer release train so it does not jump from a read-only smoke gate directly into the draft production target.

## What Changes

- Refine the active team-mode plan with subrelease slices from R0.6.0 through R2.0.8.
- Refine the active durable-state isolation plan so the immediate next work stays R0.6.0 and R0.6.1 before any status sampling or dry-run routing.
- Refine the draft personal production durable-team plan with an MVP/release ladder while keeping that plan `status: draft`.
- Add an OpenSpec requirement that roadmap slices remain independently reviewable, reversible, and consent-bounded.

impact_scope: Documentation, OpenSpec requirements, and implementation-plan sequencing only.

explicit_non_goals:

- Do not run `omx-team-auto.ps1 -Apply`; `-Apply` is the helper switch that executes a planned durable action.
- Do not start `omx team`; `omx team` is the durable worker-team runtime command.
- Do not write `.omx/state/`; `.omx/state/` is the repo-local durable-state directory.
- Do not promote `codex_cli_personal_production_durable_team_plan.md`; this file remains the English draft north-star plan.
- Do not modify `C:\Users\lenovo\.codex\config.toml`; that file is the user-level Codex configuration file.

rollout_sequence:

1. Update the active team-mode release overlay.
2. Update the active durable-state next-decision section.
3. Update the draft production durable-team release ladder.
4. Add the OpenSpec release-slice requirement.
5. Validate with OpenSpec and repository documentation checkers.

rollback_plan: Revert this documentation/spec change; no runtime state or user-level configuration is mutated.

validation_path:

- `openspec validate --all` - validates OpenSpec specs and active or archived changes.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - runs the aggregate OpenSpec repository guard.
- `python tools/check_name_clarity_rules.py --root . --json` - checks short explanations after scripts, paths, commands, variables, profiles, roles, and similar names.
- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry rules.
- `git diff --check` - checks whitespace and patch hygiene.

mainline_classification: Roadmap refinement for the existing active Codex user-level team-mode and durable-state implementation line; not a runtime implementation and not activation of the production draft.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: require release-train roadmap slices to stay small, independently reviewed, reversible, and consent-bounded before R2.0 production claims.

## Impact

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active English team-mode implementation plan.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - active Chinese companion for the team-mode implementation plan.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - active English durable-state isolation plan.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - active Chinese companion for the durable-state isolation plan.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - draft English north-star plan.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - draft Chinese north-star plan companion.
- `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` - stable plan-status capability that receives a future delta during archive.
