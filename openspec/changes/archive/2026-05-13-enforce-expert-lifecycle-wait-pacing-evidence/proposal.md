# Change: Enforce expert lifecycle, wait, and pacing evidence

## Why

The automatic orchestration routing enforcement plan requires completed experts to be closed after result absorption, wait windows to stay bounded with visible liveness and stall handling, and upstream provider pacing to be treated as backpressure rather than a reason to disable orchestration. Existing policy text states those rules, but saved run summaries could still omit closure evidence, use vague wait claims, or cite provider pacing as an orchestration blocker without a script-backed check.

This change adds a focused evidence checker for expert lifecycle, bounded wait, liveness/stall, and provider-pacing labels, then wires the checker into the orchestration activation policy surface so these claims have executable coverage.

## What Changes

- Add `tools/check_expert_lifecycle_wait_pacing_evidence.py` for saved run-summary or transcript evidence snippets.
- Add unit coverage for completed-expert closure, preserved-thread exceptions, bounded wait windows, indefinite waits, stall actions, provider backpressure labels, and pacing-as-disablement regressions.
- Update orchestration activation governance docs and stable OpenSpec policy text to reference the checker-backed lifecycle/wait/pacing evidence contract.
- Extend the activation-policy checker so repository surfaces must mention the new checker and so the checker import path is exercised.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-orchestration-activation-policy`: strengthens expert lifecycle, wait/liveness, and provider pacing evidence enforcement.

## Impact

- `tools/check_expert_lifecycle_wait_pacing_evidence.py`: new saved evidence validator.
- `test/check_expert_lifecycle_wait_pacing_evidence.test.py`: focused regression tests.
- `tools/check_orchestration_activation_policy.py` and its tests: require policy surfaces and checker availability.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: document the evidence checker.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: stable requirement text.

## impact_scope

Saved run-summary evidence, expert lifecycle labels, bounded wait/liveness evidence, provider pacing/backpressure language, and the user-level orchestration activation policy checker surface.

## explicit_non_goals

- No live `omx team` launch.
- No `omx-team-auto.ps1 -Apply` run.
- No mutation of `.omx/state/` or user-level capability state.
- No durable backend selection change.
- No remote publication or GitLab MR creation.
- No CI manifest edit in this slice.

## rollout_sequence

1. Add the saved evidence checker.
2. Add focused checker unit tests.
3. Update governance docs and OpenSpec requirement text.
4. Validate the active change, target tests, OpenSpec guard, local gate, and local MR review.
5. Archive the OpenSpec change into the same local integration package if validation passes.

## rollback_plan

Revert this branch's commits to remove the new checker, tests, docs, and spec updates. No durable runtime state or user-level state needs recovery because the change is read-only validation logic.

## validation_path

- `D:\PythonProject_langgraph\.venv\Scripts\python.exe test\check_expert_lifecycle_wait_pacing_evidence.test.py` - verifies the new expert lifecycle/wait/pacing checker regressions.
- `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_expert_lifecycle_wait_pacing_evidence.py --evidence <sample> --json` - validates a saved evidence sample through the new checker CLI.
- `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\check_orchestration_activation_policy.py --root . --json` - verifies policy surfaces mention and load the new checker.
- `openspec validate enforce-expert-lifecycle-wait-pacing-evidence --json` and `openspec validate --all --json` - validate the active change and stable specs.
- `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --tool codex --json` - runs the repository OpenSpec guard sequence.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180` - runs the shared local CI gate.

## mainline_classification

Small checker-backed enforcement slice under the active automatic orchestration routing plan and the current `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` mainline.
