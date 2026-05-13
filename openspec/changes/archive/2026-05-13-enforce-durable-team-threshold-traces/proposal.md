# Change: Enforce durable-team threshold trace evidence

## Why

The automatic orchestration routing enforcement plan requires startup, continue, and phase-change activation traces to explain durable-team decisions with concrete threshold evidence. The policy text already says to report unmet thresholds or triggered thresholds, but saved trace evidence could still pass the validator with vague reasons such as "small task" or "using team now".

This change makes durable workflow and persistent-team threshold claims executable in `tools/check_orchestration_trace_evidence.py`, so timeout-free trace evidence still fails when no-team, blocked-team, selected-team, or running-team decisions omit the required threshold or blocker labels.

## What Changes

- Extend `tools/check_orchestration_trace_evidence.py` so `durable_workflow` and `persistent_team` decisions require threshold evidence in `why`.
- Add regression tests for no-team traces without `threshold_not_met:*`, blocked lanes without a named blocker, and selected/running lanes without `triggered_threshold:*` or equivalent trigger language.
- Update governance and OpenSpec policy text to state that the trace-evidence validator enforces durable-team threshold labels.
- Keep this as a read-only checker enhancement: it does not launch durable teams, mutate `.omx/state/`, or alter user-level capability state.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-orchestration-activation-policy`: strengthens saved activation trace validation so durable-team threshold evidence is checker-enforced.

## Impact

- `tools/check_orchestration_trace_evidence.py`: stricter validation for durable workflow and persistent-team threshold evidence.
- `test/check_orchestration_trace_evidence.test.py`: additional regression coverage for unmet-threshold, named-blocker, and triggered-threshold labels.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: document the stricter evidence requirement.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: stable requirement text for the validator.

## impact_scope

Saved activation trace evidence, durable workflow / persistent-team threshold reporting, and the user-level orchestration activation policy checker surface.

## explicit_non_goals

- No live `omx team` launch.
- No `omx-team-auto.ps1 -Apply` run.
- No mutation of `.omx/state/` or user-level capability state.
- No durable backend selection change.
- No remote publication or GitLab MR creation.
- No CI manifest edit in this slice.

## rollout_sequence

1. Add threshold-evidence checks to the trace evidence validator.
2. Add focused regression tests for accepted and rejected trace snippets.
3. Update governance docs and OpenSpec requirement text.
4. Validate the active change, target tests, OpenSpec guard, local gate, and local MR review.
5. Archive the OpenSpec change into the same local integration package if validation passes.

## rollback_plan

Revert this branch's commits to restore the previous trace-evidence validator behavior and remove the related tests/docs/spec updates. No durable runtime state or user-level state needs recovery because the change is read-only validation logic.

## validation_path

- Trace checker unit test: `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_orchestration_trace_evidence.test.py`.
- Trace checker sample validation: `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_trace_evidence.py --trace <sample> --json`.
- Activation policy checker: `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json`.
- OpenSpec validation: `openspec validate enforce-durable-team-threshold-traces --json` and `openspec validate --all --json`.
- OpenSpec repository guard: `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json`.
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180`.

## mainline_classification

Small checker-backed enforcement slice under the active automatic orchestration routing plan and the current `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` mainline.
