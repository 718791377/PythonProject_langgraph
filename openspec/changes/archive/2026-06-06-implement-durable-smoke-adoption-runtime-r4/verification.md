# Verification Report

## Commands before archive

- `python test\check_durable_routing_smoke_receipts.test.py -v` - 6 tests passed.
- `python tools\check_durable_routing_smoke_receipts.py --root . --json` - `ok: true` with three negative self-test fixtures.
- `python tools\run_durable_routing_smoke.py --root . --receipt .tmp\durable-routing-smoke-receipt.json --phase verify-accept --task "manual focused smoke" --candidate-backend-family langgraph --json` - `ok: true` and all adoption/mutation fields remained false.
- `python tools\check_durable_routing_smoke_receipts.py --root . --receipt .tmp\durable-routing-smoke-receipt.json --json` - receipt field meanings: `ok: true` means the receipt passed validation, `runtime_stage=R4` means the R4 smoke stage, `stage=smoke-tested` means smoke evidence only, and `adoption_state=not_adopted` means no durable workflow adoption occurred.
- `openspec validate implement-durable-smoke-adoption-runtime-r4 --strict` - change is valid.

## Field glossary

- `ok: true` means the runner or checker command accepted the evidence for this run.
- `runtime_stage=R4` means the receipt belongs to the R4 smoke runtime stage.
- `stage=smoke-tested` means the evidence proves only smoke execution, not durable workflow adoption.
- `adoption_state=not_adopted` means no durable workflow was selected, running, adopted, or launched.

## Boundary review

The R4 helper writes only the explicit smoke receipt path, records timeout release and rollback readiness, and does not perform apply-mode adoption, durable-team launch, LangGraph thread start, durable backend state mutation, user-level state mutation, or remote publication authorization.

## Archive plan

The active delta is archived in the same feature branch before local main integration so the R4 smoke receipt requirement is promoted into the stable automatic-team-routing spec while remote publication remains unauthorized.


## Value outcome

R4 now has an executable read-only smoke runner and a fail-closed receipt checker. The implementation proves `smoke-tested` evidence without selected/running/adopted durable workflow state, apply-mode execution, durable-team launch, LangGraph thread start, durable backend mutation, user-level mutation, or remote publication authorization.

## Lessons learned

Smoke evidence and adoption evidence must remain separate receipt classes. Future apply-mode helpers should require explicit operator authorization, backend-family ownership, timeout release, rollback readiness, cleanup evidence, and a separate selected/running/adopted/released receipt path instead of upgrading R4 smoke success into adoption.
