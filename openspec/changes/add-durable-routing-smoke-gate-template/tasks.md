## 1. Implementation

- [x] Add `tools/durable_routing_smoke_gate_template.json` as the read-only gate template for R0.6 durable routing smoke gates.
- [x] Add `tools/check_durable_routing_smoke_gate_template.py` to validate the template fields, defaults, and read-only mutation boundary.
- [x] Wire the checker into `tools/run_openspec_guard.py`.
- [x] Add bilingual OpenSpec artifacts for this change.

## 2. Validation

- [x] Run `python .\tools\check_durable_routing_smoke_gate_template.py --root . --json`.
- [x] Run `openspec validate --all`.
- [x] Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] Run `git diff --check`.
