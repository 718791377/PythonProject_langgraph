# Design: Effective lane-fit evidence enforcement

## Approach

Implement one Python checker with two modes:

1. Repository mode validates that core policy surfaces explicitly require effective lane choice to map to task fit:
   - `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, or direct worker lifecycle control.
   - LangGraph for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, or persisted survivor queues.
   - one backend family per durable task unless switching is recorded as an explicit close or handoff.
2. Evidence mode validates saved traces or run summaries:
   - `native_omx` lane claims must include a worker-centric fit marker.
   - LangGraph lane claims must include a graph-shaped fit marker.
   - default-backend-only language is not enough to justify task-level adoption.
   - mixed `native_omx` and LangGraph evidence must include explicit close or handoff language.
   - backend-family switching evidence must include explicit close/handoff.

The checker complements existing checks:

- `check_capability_switch_chain.py` proves capability dependency state.
- `check_role_routing_directive_evidence.py` proves hard-directive adoption or blockers.
- `check_durable_artifact_state_surfaces.py` proves LangGraph state and artifact surfaces.
- This checker proves the task-level effective lane rationale and single-family handoff boundary.

## CI and guard wiring

- Add `tools/check_effective_lane_fit_evidence.py`.
- Add `test/check_effective_lane_fit_evidence.test.py`.
- Add the test to `tools/ci/ci_test_manifest.json`.
- Add a no-input guard step in `tools/run_openspec_guard.py`.
- Add the checker to `tools/safety_rule_script_backing_registry.json` as a separate implemented safety rule and as supporting script control for the orchestration activation policy.

## Policy synchronization

- Update the English and Chinese orchestration activation policy documents.
- Update the English and Chinese startup summaries.
- Update `AGENTS.md` with the checker-backed lane-fit reminder.
- Promote the requirement into `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md` during archive.

## Non-goals

- Do not choose or launch a durable backend for this implementation slice.
- Do not modify user-level runtime state or installed wrappers.
- Do not push to GitLab or GitHub.
