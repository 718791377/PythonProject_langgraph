## Context

R0.6 is the first release band that prepares automatic durable routing exercises. The existing automatic routing spec already requires smoke gates to declare target, phase, task, and consent boundary. This change turns that requirement into a small script-backed template surface without exercising runtime mutation.

## Decisions

- Add `tools/durable_routing_smoke_gate_template.json` as the canonical template for future R0.6.x smoke gates.
- Add `tools/check_durable_routing_smoke_gate_template.py` as a read-only checker for the template.
- Add the checker to `tools/run_openspec_guard.py` so template drift fails the same guard used by cold-start sessions and CI.
- Keep the template separate from `.omx/state/` because it is a reviewed planning artifact, not durable runtime state.

## Boundaries

- `tools/durable_routing_smoke_gate_template.json` is a template file; it is not an active selector and does not activate native_omx or LangGraph.
- `tools/check_durable_routing_smoke_gate_template.py` validates fields and defaults only; it must not call `omx`, `codex`, `langgraph`, or any mutation helper.
- `tools/run_openspec_guard.py` includes the checker as another read-only guard step.

## Validation

- `python .\tools\check_durable_routing_smoke_gate_template.py --root . --json` - checks the durable routing smoke gate template contract.
- `openspec validate --all` - validates all active changes and stable specs.
- `python .\tools\run_openspec_guard.py --root . --tool codex --json` - runs the repository OpenSpec guard sequence for Codex.
- `git diff --check` - checks patch whitespace before commit.

## Rollback

Revert the template, checker, guard wiring, and this OpenSpec change. No runtime state rollback is required because this change does not mutate durable state.
