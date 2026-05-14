# Change: Enforce leader session and scope evidence

## Why

The automatic orchestration routing plan now treats main-session leadership, startup non-autolaunch, task-flow scoped adoption, and legacy resume boundaries as hard routing safety rules. The policy surfaces already describe these rules, but cold-start or resumed sessions still need executable evidence checks so they cannot silently replace the current main Codex CLI session with a persistent leader pane, treat Codex startup as an automatic durable-team launch, use repository age as the adoption basis, or let a legacy `/resume` thread override current governance.

## What Changes

- Add a script-backed checker for leader/session scope evidence.
- Register the checker in the OpenSpec guard, safety-rule registry, and local CI manifest.
- Add regression tests for missing leader ownership, separate persistent leader-pane replacement, startup auto-launch without threshold evidence, repo-age based adoption, legacy override, and resume/continue without activation rerun evidence.
- Update startup, governance, and OpenSpec policy surfaces to point to the new checker.

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: main-session leader ownership, startup non-autolaunch, task-flow scoped adoption, legacy resume boundaries, and reload/restart/resume/continue retrofit evidence become executable through a repository checker.

## Impact

- Affected code: `tools/check_leader_session_scope_evidence.py`, `tools/run_openspec_guard.py`, `tools/safety_rule_script_backing_registry.json`, `tools/ci/ci_test_manifest.json`.
- Affected tests: `test/check_leader_session_scope_evidence.test.py`.
- Affected docs/specs: `AGENTS.md`, startup summaries, orchestration activation governance docs, and OpenSpec delta/stable specs.
- `impact_scope`: repository-local policy/checker enforcement only.
- `explicit_non_goals`: no remote publication, no runtime worker launch, no persistent team start, no LangGraph package install, and no change to native subagent tool contracts.
- `rollout_sequence`: add checker and tests, wire guard/registry/manifest, update policy/spec, run local gate and local MR review, then archive the OpenSpec change.
- `rollback_plan`: revert the checker, registry/guard/manifest wiring, and policy/spec deltas while keeping the implementation plan as historical context.
- `validation_path`: unit test the checker, run `tools/run_openspec_guard.py --root . --json`, run `tools/ci/local_gate.ps1`, and run `tools/ci/local_mr_review.ps1`.
- `mainline_classification`: existing orchestration enforcement mainline under `automatic_orchestration_routing_enforcement_plan`.
