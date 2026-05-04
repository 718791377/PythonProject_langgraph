## Why

The current active rollout has completed the bounded durable-state MR 1 through MR 6 queue, but the next live routing exercise still needs a smaller release boundary before any runtime action is attempted. Defining a Release 0.6 durable routing smoke gate prevents the final production durable-team draft from being treated as directly implementable work.

## What Changes

- Add a Release 0.6 durable routing smoke/adoption gate to the active team-mode and durable-state plans.
- Require every future smoke or adoption-gate change to declare `target_repository` - the repository root that owns the current OpenSpec, source, and repo-local durable state.
- Require every future smoke or adoption-gate change to declare `phase` - the project phase such as read-context, verify-accept, execute-parallel, integrate-converge, or stabilize that drives routing thresholds.
- Require every future smoke or adoption-gate change to declare `task` - the concrete work item or validation question being evaluated.
- Require every future smoke or adoption-gate change to declare `operator_consent_boundary` - the explicit line between read-only planning and mutating actions such as `-Apply`, `.omx/state/` writes, or durable-team launch.
- Add a Release / MVP overlay to the draft personal production durable-team plan without marking that draft as active implementation.

impact_scope: Documentation, OpenSpec requirements, and implementation-plan sequencing only.

explicit_non_goals:

- Do not run `omx-team-auto.ps1 -Apply`; `-Apply` is the helper switch that executes the planned durable action.
- Do not start `omx team`; `omx team` is the durable worker-team runtime command.
- Do not write `.omx/state/`; `.omx/state/` is the repo-local durable-state directory.
- Do not edit `C:\Users\lenovo\.codex\config.toml`; that file is the user-level Codex configuration file.
- Do not change MCP Router state; MCP Router is the shared MCP management layer outside Codex-dedicated `omx_*` MCP tools.

rollout_sequence:

1. Define the Release 0.6 gate in active implementation plans.
2. Add an OpenSpec requirement for the four required gate fields.
3. Keep the final production plan as a draft and add a release-train overlay only.
4. Validate with OpenSpec and repository documentation checkers.
5. Publish through GitLab-first review and GitHub mirror sync.

rollback_plan: Revert this documentation/spec change; no runtime state or user-level configuration is mutated.

validation_path:

- `openspec validate --all` - validates OpenSpec specs and active or archived changes.
- `python tools/run_openspec_guard.py --root . --tool codex --json` - runs the aggregate OpenSpec repository guard.
- `python tools/check_name_clarity_rules.py --root . --json` - enforces short explanations after scripts, paths, commands, variables, and profile names in governed docs.
- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry rules.
- `git diff --check` - checks whitespace and patch hygiene.

mainline_classification: Existing active Codex user-level team-mode and cross-session durable-state rollout line; not a new mainline and not direct implementation of the production durable-team draft.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-team-mode-automatic-team-routing`: define the required smoke/adoption-gate fields and the read-only default before any future live routing exercise.

## Impact

- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active English team-mode implementation plan.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - active Chinese companion for the team-mode implementation plan.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - active English durable-state isolation plan.
- `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - active Chinese companion for the durable-state isolation plan.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.md` - draft English north-star plan.
- `docs_bilingual/implementation_plans/codex_cli_personal_production_durable_team_plan.zh-CN.md` - draft Chinese north-star plan companion.
- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` - stable automatic routing capability that receives a future delta during archive.
