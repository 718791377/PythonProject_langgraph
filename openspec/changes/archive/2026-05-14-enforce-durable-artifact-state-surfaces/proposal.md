# Change: Enforce durable artifact and state-surface evidence

## Why

The automatic orchestration routing plan requires read-only exploration, code-changing worker execution, LangGraph checkpoint state, frozen briefs, and survivor queues to remain separate evidence surfaces. The policy text already describes those boundaries, but there is not yet an executable checker that fails closed when exploration replaces an implementation worker, graph-shaped work omits repo-local LangGraph state, durable artifacts remain only in chat context, or compatibility records replace the active selector.

## What Changes

- Add a script-backed evidence checker for explorer/worker boundaries and durable artifact state surfaces.
- Register the checker in the OpenSpec guard, safety-rule registry, and local CI manifest.
- Add regression tests for exploration replacing code workers, missing LangGraph state, transient-only durable artifacts, incomplete frozen briefs, persistent bug-triad workers, and selector-source misuse.
- Update orchestration activation policy/spec surfaces to point to the new checker.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: explorer versus worker boundaries, LangGraph state-surface use, active selector authority, frozen research briefs, and survivor queues become executable through a repository checker.

## Impact

- Affected code: `tools/check_durable_artifact_state_surfaces.py`, `tools/run_openspec_guard.py`, `tools/safety_rule_script_backing_registry.json`, `tools/ci/ci_test_manifest.json`.
- Affected tests: `test/check_durable_artifact_state_surfaces.test.py`.
- Affected docs/specs: orchestration activation governance docs and OpenSpec delta/stable specs.
- `impact_scope`: repository-local policy/checker enforcement only.
- `explicit_non_goals`: no remote publication, no runtime worker launch, no persistent team start, no LangGraph package install, and no change to native subagent tool contracts.
- `rollout_sequence`: add checker and tests, wire guard/registry/manifest, update policy/spec, run local gate and local MR review, then archive the OpenSpec change.
- `rollback_plan`: revert the checker, registry/guard/manifest wiring, and policy/spec deltas while keeping the implementation plan as historical context.
- `validation_path`: unit test the checker, run `tools/run_openspec_guard.py --root . --json`, run `tools/ci/local_gate.ps1`, and run `tools/ci/local_mr_review.ps1`.
- `mainline_classification`: existing orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
