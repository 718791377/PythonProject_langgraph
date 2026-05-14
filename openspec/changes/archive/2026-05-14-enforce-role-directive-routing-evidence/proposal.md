# Change: Enforce hard directive and role routing evidence

## Why

The automatic orchestration routing plan requires explicit `omx` and `LangGraph` requests to be hard directives rather than optional preferences, and it requires expert routing to use the smallest sufficient role set. The stable policy states those rules, but saved run summaries and activation traces need executable evidence checks that fail closed when a directive stays in explanation-only mode, when thresholds are satisfied but no lane is adopted, when roles are added merely because they are available, or when bounded multi-face research skips analyst-only first-round fan-out.

## What Changes

- Add a script-backed checker for hard directive adoption and role-routing evidence.
- Register the checker in the OpenSpec guard, safety-rule registry, and local CI manifest.
- Add regression tests for optional-preference directives, directive-without-adoption, explanation-only mode, missing role triggers, extra roles because available, and bounded multi-face research analyst-first behavior.
- Update orchestration activation policy/spec surfaces to point to the new checker.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: hard-directive adoption, explanation-only rejection, smallest-sufficient role routing, and bounded multi-face analyst-first routing become executable through a repository checker.

## Impact

- Affected code: `tools/check_role_routing_directive_evidence.py`, `tools/run_openspec_guard.py`, `tools/safety_rule_script_backing_registry.json`, `tools/ci/ci_test_manifest.json`.
- Affected tests: `test/check_role_routing_directive_evidence.test.py`.
- Affected docs/specs: orchestration activation governance docs and OpenSpec delta/stable specs.
- `impact_scope`: repository-local policy/checker enforcement only.
- `explicit_non_goals`: no remote publication, no runtime worker launch, no persistent team start, no LangGraph package install, and no change to native subagent tool contracts.
- `rollout_sequence`: add checker and tests, wire guard/registry/manifest, update policy/spec, run local gate and local MR review, then archive the OpenSpec change.
- `rollback_plan`: revert the checker, registry/guard/manifest wiring, and policy/spec deltas while keeping the implementation plan as historical context.
- `validation_path`: unit test the checker, run `tools/run_openspec_guard.py --root . --json`, run `tools/ci/local_gate.ps1`, and run `tools/ci/local_mr_review.ps1`.
- `mainline_classification`: existing orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
