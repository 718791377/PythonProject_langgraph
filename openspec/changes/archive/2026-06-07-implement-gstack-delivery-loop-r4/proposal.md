# Proposal: Implement gstack Codex Delivery Loop Runtime R4

## Why

The repository already documents the conflict-priority stack `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, but the gstack lane still lacks executable repo-local enforcement. Without a bounded checker and runtime helper, later work could accidentally let gstack outrank Comet, bypass OpenSpec/Superpowers, overlap with harness runtime-safety controls, or behave like a real installed user-level runtime.

## What Changes

- Add `tools/gstack_codex_delivery_loop_runtime.py` as a repo-local guarded helper for `analyze`, `plan-dry-run`, `review-dry-run`, `qa-dry-run`, `ship-dry-run`, and bounded R4 `smoke`.
- Add `tools/check_gstack_codex_delivery_loop.py` to validate plan/runtime/checker/guard wiring, priority evidence, and smoke receipts.
- Add focused regression tests for the dry-run helper, blocked/positive R4 smoke receipts, authority-priority enforcement, and redaction.
- Register the checker and tests in `tools/run_openspec_guard.py`, `tools/ci/ci_test_manifest.json`, and `tools/safety_rule_script_backing_registry.json`.
- Update the active bilingual implementation plans so they honestly describe the implemented-local R0-R4 boundary.
- Add a stable OpenSpec requirement for repo-local gstack delivery-loop tooling that stays subordinate to Comet/OpenSpec/Superpowers and does not become a live user-level runtime by default.

## Scope

- `tools/gstack_codex_delivery_loop_runtime.py` - repo-local guarded runtime helper for advisory dry-run actions and bounded R4 smoke receipts.
- `tools/check_gstack_codex_delivery_loop.py` - fail-closed checker for priority evidence, receipt validation, and guard wiring.
- `test/gstack_codex_delivery_loop_runtime.test.py` - focused regression test for dry-run and smoke-helper behavior.
- `test/check_gstack_codex_delivery_loop.test.py` - focused regression test for checker behavior, redaction, and fail-closed paths.
- `tools/run_openspec_guard.py` - aggregate OpenSpec guard entrypoint that must call the new gstack checker.
- `tools/ci/ci_test_manifest.json` - CI-managed Python test manifest that must register the new focused tests.
- `tools/safety_rule_script_backing_registry.json` - safety registry entry recording the script-backed governance boundary for this lane.
- `docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.md` and `.zh-CN.md` - active bilingual child-plan pair for the gstack runtime lane.
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` and `.zh-CN.md` - parent-plan pair that records the lane status and cross-lane priority order.
- `openspec/specs/codex-user-level-gstack-delivery-loop-runtime-governance/spec.md` and `.zh-CN.md` after archive - stable spec pair for the repo-local gstack governance contract.

## Non-Goals

- Do not install, clone, or enable upstream gstack.
- Do not enable hooks, browser QA, telemetry, or always-on routing.
- Do not mutate user-level Codex configuration, browser state, durable backend state, or remote Git refs.
- Do not let gstack outrank Comet, OpenSpec/Superpowers, or harness runtime-safety boundaries.
- Do not create R5 active-candidate or live user-level runtime behavior.

## Rollout

1. Resolve the serialized worktree and restore the active implementation claim.
2. Finish repo-local R0-R4 helper/checker/tests and plan updates.
3. Validate focused tests, OpenSpec guard, and local gates.
4. Archive the change on the same branch so the stable spec captures the runtime boundary.
5. Merge into local `main` and stop at the remote-publication gate.

## Rollback

- Revert the feature commit or the later local-`main` merge commit.
- Use the local rollback ref created before local `main` integration.
- Remove the new repo-local helper/checker/tests and restore the previous implementation-plan wording.

## Verification

- `python test/gstack_codex_delivery_loop_runtime.test.py -v` - focused runtime-helper regression suite.
- `python test/check_gstack_codex_delivery_loop.test.py -v` - focused checker regression suite.
- `python tools/check_gstack_codex_delivery_loop.py --root . --json` - repo-local governance checker for the gstack lane.
- `python tools/gstack_codex_delivery_loop_runtime.py smoke --root . --receipt-dir .tmp/gstack-r4-smoke --json` - bounded R4 smoke command that writes an explicit receipt path.
- `python tools/check_precommit_update_archive.py --root . --json` - precommit update/archive review for the local package.
- `python tools/run_openspec_guard.py --root . --json` - aggregate repository guard including the new gstack checker.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - shared local CI gate before integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - local MR review gate before local-main integration.
