## 1. Implementation

- [x] ?? `tools/durable_routing_smoke_gate_template.json`??? R0.6 durable routing smoke gate ??? gate template?
- [x] ?? `tools/check_durable_routing_smoke_gate_template.py`???????????????? mutation boundary?
- [x] ? checker ?? `tools/run_openspec_guard.py`?
- [x] ?? change ????? OpenSpec artifacts?

## 2. Validation

- [x] ?? `python .\tools\check_durable_routing_smoke_gate_template.py --root . --json`?
- [x] ?? `openspec validate --all`?
- [x] ?? `python .\tools\run_openspec_guard.py --root . --tool codex --json`?
- [x] ?? `git diff --check`?
