# Change: Implement Durable Smoke Adoption Runtime R4

## Why

The durable smoke/adoption gate template is already reviewed, but the Stage D runtime backlog still needs an executable R4 smoke helper. Without a concrete helper and receipt checker, a future session could confuse a successful read-only smoke command with durable workflow adoption, backend selection, `omx-team-auto.ps1 -Apply`, LangGraph thread start, or remote publication approval.

## What Changes

- Add `tools/run_durable_routing_smoke.py`, a bounded read-only smoke runner that executes only safe local Python checker commands and writes a sanitized R4 `smoke-tested` receipt to an explicit receipt path.
- Add `tools/check_durable_routing_smoke_receipts.py`, a receipt checker that validates timeout release, rollback readiness, bounded redacted transcripts, backend-family evidence, and explicit non-adoption fields.
- Add focused regression coverage and register the checker/test in the OpenSpec guard and CI manifest.
- Update the durable smoke/adoption implementation plan and the stable automatic-team-routing spec to mark R4 smoke receipt runtime complete while leaving apply-mode adoption and live handoff receipts pending.

## Scope

- `tools/run_durable_routing_smoke.py` - read-only R4 smoke receipt writer.
- `tools/check_durable_routing_smoke_receipts.py` - fail-closed R4 smoke receipt validator.
- `test/check_durable_routing_smoke_receipts.test.py` - focused runner/checker regression tests.
- `tools/run_openspec_guard.py`, `test/run_openspec_guard_json.test.py`, and `tools/ci/ci_test_manifest.json` - guard and CI registration.
- `docs_bilingual/implementation_plans/durable_smoke_adoption_gate_template_plan.md` and `.zh-CN.md` - Stage D R4 status and evidence.
- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` and `.zh-CN.md` - reusable R4 smoke receipt requirement.

## Non-Goals

- Do not implement apply-mode adoption or selected/running/adopted durable workflow receipts in this slice.
- Do not run `omx-team-auto.ps1 -Apply`, `omx team`, LangGraph `dev`/thread start, or durable backend launch.
- Do not write `.omx/state/` as durable backend state; the runner writes only the explicit smoke receipt path requested by the caller.
- Do not mutate user-level configuration or remote Git refs.

## Rollout

1. Add the runner, checker, and focused tests.
2. Register the checker and test in local guard/CI surfaces.
3. Update implementation-plan and stable spec evidence.
4. Validate with focused tests, OpenSpec validation, precommit/archive guard, repository guard, local gate, and local MR review.
5. Archive the completed change in the same feature branch before local `main` integration.

## Rollback

- Revert the feature commit or the local `main` merge commit.
- Use the local integration rollback ref if the guarded local-main helper creates one after merge.
- No user-level or durable backend runtime state should need rollback because this slice does not launch or adopt a durable workflow.

## Verification

- `python test/check_durable_routing_smoke_receipts.test.py -v` - focused runner/checker tests.
- `python tools/check_durable_routing_smoke_receipts.py --root . --json` - checker self-test.
- `python tools/run_durable_routing_smoke.py --root . --receipt .tmp/durable-routing-smoke-receipt.json --json` followed by receipt validation.
- `openspec validate implement-durable-smoke-adoption-runtime-r4 --strict` and `openspec validate --all` - OpenSpec validation.
- `python tools/check_precommit_update_archive.py --root . --json`, `python tools/run_openspec_guard.py --root .`, and local CI/MR gates before local integration.
