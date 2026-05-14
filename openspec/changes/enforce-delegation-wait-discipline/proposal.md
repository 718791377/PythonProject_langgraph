# Change: Enforce delegation design and leader wait discipline evidence

## Why

The automatic orchestration routing plan requires delegation to be concrete, bounded, non-duplicative, and useful while the main session remains the leader. Current policy text describes that rule, but there is not yet an executable evidence checker that fails closed when a run summary delegates blocking critical-path work, omits sidecar boundaries, or waits silently without non-overlapping leader work.

## What Changes

- Add a script-backed evidence checker for delegation design quality and leader wait discipline.
- Register the checker in the OpenSpec guard and safety-rule registry.
- Add regression tests for missing critical-path planning, vague delegation, duplicate work, unsafe code-worker briefs, and silent wait behavior.
- Update the orchestration activation policy/spec surfaces to point to the new checker.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: delegation and `wait_agent` discipline evidence becomes executable through a repository checker.

## Impact

- Affected code: `tools/check_delegation_wait_discipline_evidence.py`, `tools/run_openspec_guard.py`, `tools/safety_rule_script_backing_registry.json`, `tools/ci/ci_test_manifest.json`.
- Affected tests: `test/check_delegation_wait_discipline_evidence.test.py`.
- Affected docs/specs: orchestration activation governance docs and OpenSpec delta/stable specs.
- `impact_scope`: repository-local policy/checker enforcement only.
- `explicit_non_goals`: no remote publication, no runtime worker launch, no persistent team start, no LangGraph package install, and no change to native subagent tool contracts.
- `rollout_sequence`: add checker and tests, wire guard/registry/manifest, update policy/spec, run local gate and local MR review, then archive the OpenSpec change.
- `rollback_plan`: revert the checker, registry/guard/manifest wiring, and policy/spec deltas while keeping the implementation plan as historical context.
- `validation_path`: unit test the checker, run `tools/run_openspec_guard.py --root . --json`, run `tools/ci/local_gate.ps1`, and run `tools/ci/local_mr_review.ps1`.
- `mainline_classification`: existing orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
