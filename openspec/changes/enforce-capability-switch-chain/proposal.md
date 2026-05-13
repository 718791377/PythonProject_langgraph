# Change: Enforce capability switch chain

## Why

The automatic orchestration routing enforcement plan requires `subagent_routing`, `oh_my_codex`, `langgraph`, and `durable_orchestration_backend` to be interpreted as a strict dependency chain. The rule already appears in policy text, but a cold-start session still needs executable evidence that present user-level state is valid instead of relying on prompt memory.

Without a checker, invalid combinations such as `subagent_routing=off` with `langgraph=on`, or `durable_orchestration_backend=langgraph` while `langgraph=off`, can be reported as ready backend state and contaminate activation traces.

## What Changes

- Add `tools/check_capability_switch_chain.py` to validate user-level capability state and optional repo-local LangGraph backend context.
- Add regression tests covering valid state, invalid dependency combinations, missing-state behavior, and unready backend context.
- Make `tools/check_orchestration_activation_policy.py` run the capability-switch checker as a subcheck.
- Update AGENTS.md, governance policy, and capability-switch / activation OpenSpec specs to require checker-backed chain validation.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `codex-user-level-capability-switches`: adds executable dependency-chain validation.
- `codex-user-level-orchestration-activation-policy`: records that activation-policy checks include capability-switch validation.

## Impact

- `tools/check_capability_switch_chain.py`: new checker.
- `test/check_capability_switch_chain.test.py`: checker regression tests.
- `tools/check_orchestration_activation_policy.py`: invokes the capability-chain checker.
- `test/check_orchestration_activation_policy.test.py`: verifies the subcheck is enforced.
- `AGENTS.md`: documents executable capability-chain validation.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` and `.zh-CN.md`: document strict chain rules and checker support.
- `openspec/specs/codex-user-level-capability-switches/spec.md` and `.zh-CN.md`: stable dependency-chain checker requirement.
- `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md`: activation-policy checker wiring requirement.
- `tools/safety_rule_script_backing_registry.json`, `tools/run_openspec_guard.py`, and `tools/ci/ci_test_manifest.json`: intentionally not changed in this slice because overlapping active ownership exists or the orchestration activation checker already runs under the guard.

## impact_scope

User-level capability-state validation and activation-policy guard coverage.

## explicit_non_goals

- No live durable-team launch.
- No `omx-team-auto.ps1 -Apply` run.
- No mutation of `C:\Users\lenovo\.codex\state\user-level-team-mode.json`.
- No automatic normalization of user-level state.
- No remote publication or GitLab MR creation.
- No CI manifest edit in this slice.

## rollout_sequence

1. Add checker and regression tests.
2. Wire checker into the activation-policy checker.
3. Update AGENTS.md, governance docs, and stable specs.
4. Run targeted tests, OpenSpec validation, guard, local gate, and local MR review.
5. Archive the OpenSpec change in the same local integration package if validation passes.

## rollback_plan

Revert this branch commit to remove the checker, tests, activation-policy subcheck, and documentation/spec wording. No user-level state or durable runtime state is changed by this slice.

## validation_path

- Capability-chain unit test: `python test/check_capability_switch_chain.test.py`.
- Capability-chain repository check: `python tools/check_capability_switch_chain.py --root . --json`.
- Activation-policy unit test: `python test/check_orchestration_activation_policy.test.py`.
- Activation-policy repository check: `python tools/check_orchestration_activation_policy.py --root . --json`.
- OpenSpec full validation: `openspec validate --all --json`.
- OpenSpec repository guard: `python tools/run_openspec_guard.py --root . --tool codex --json`.
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Root . -Json -StepTimeoutSeconds 180`.

## mainline_classification

Small checker-backed enforcement slice under the active automatic orchestration routing plan and the current `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` mainline.
