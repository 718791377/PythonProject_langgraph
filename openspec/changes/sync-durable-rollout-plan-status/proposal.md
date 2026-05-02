## Why

The cross-session durable-state isolation plan still says MR 5 is the next active implementation slice, but the helper mirror source-of-truth slice has already landed, passed validation, and been archived. Cold-start sessions may otherwise repeat completed work or choose the wrong next step.

## What Changes

- Mark MR 5 as completed in the bilingual cross-session durable-state isolation plan.
- Cite the landed helper mirror source-of-truth evidence and archived OpenSpec change.
- Reframe the next step as an MR 6 readiness review or automatic durable routing hookup, not another MR 5 implementation.
- Add a plan-status-sync requirement so completed durable-state rollout slices are not left labeled as the next active slice.

## Capabilities

### Modified Capabilities
- `codex-user-level-team-mode-plan-status-sync`: Extends status-sync requirements to the cross-session durable-state rollout queue.

## Impact

- Impact scope: `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.md` - English ASCII implementation plan source of truth.
- Impact scope: `docs_bilingual/implementation_plans/codex_user_level_cross_session_durable_state_isolation_plan.zh-CN.md` - UTF-8 Chinese companion plan.
- Impact scope: `openspec/specs/codex-user-level-team-mode-plan-status-sync/spec.md` and `.zh-CN.md` - stable status-sync requirement.
- Explicit non-goals: do not edit `C:\Users\lenovo\.codex\config.toml`; do not mutate `.omx/state/`; do not start a durable team; do not implement MR 6 in this change.
- Validation path: OpenSpec validation, repository guard, name clarity check, implementation plan check, and whitespace check.
