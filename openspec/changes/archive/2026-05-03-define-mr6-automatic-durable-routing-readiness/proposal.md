## Why

The cross-session durable-state isolation plan now names MR 6 as the next decision point, but repository evidence shows the automatic durable routing hookup already exists in earlier team-mode surfaces. Without an explicit MR 6 readiness review, cold-start sessions may either repeat completed runtime work or incorrectly assume a durable team should be launched immediately.

## What Changes

- Record MR 6 as a readiness-review and status-reconciliation slice, not a new runtime implementation slice.
- Update the bilingual durable-state isolation plan so it points at the already implemented automatic routing surfaces before asking for new runtime work.
- Add a plan-status-sync requirement that stale rollout queues must reconcile MR 6 against existing `omx-team-auto.ps1` evidence before opening another hookup implementation.
- Keep durable team launch, user-level config edits, MCP changes, and repo-local `.omx/state/` mutation out of scope.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-team-mode-plan-status-sync`: Adds MR 6 readiness-review coverage so rollout queues do not ask for a duplicate automatic durable routing hookup when the existing specs, helpers, and tests already provide that surface.

## Impact

- impact_scope: `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` and `.zh-CN.md` - the active durable-state isolation implementation plan pair.
- impact_scope: `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` and `.zh-CN.md` - the stable plan-status synchronization contract.
- impact_scope: `openspec/changes/define-mr6-automatic-durable-routing-readiness/` - the OpenSpec change artifacts for this bounded status slice.
- explicit_non_goals: do not edit `C:\Users\lenovo\.codex\config.toml`, do not mutate `.omx/state/`, do not start `omx team`, do not modify MCP Router state, and do not rewrite runtime helpers in this change.
- rollout_sequence: create the readiness change, update the plan/status contract, validate with OpenSpec and repository guards, then publish by GitLab-first workflow.
- rollback_plan: revert the documentation and spec-status commit; no runtime state or user-level config rollback is needed because this change is non-mutating.
- validation_path: `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, `python tools/check_name_clarity_rules.py --root . --json`, and `git diff --check`.
- mainline_classification: existing user-level Codex orchestration / cross-session durable-state isolation mainline.
