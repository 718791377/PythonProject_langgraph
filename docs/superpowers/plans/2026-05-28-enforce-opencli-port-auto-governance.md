---
change: enforce-opencli-port-auto-governance-20260528
design-doc: docs/superpowers/specs/2026-05-28-enforce-opencli-port-auto-governance-design.md
status: implemented
---

# Plan: Enforce OpenCLI port-auto governance

- [x] Add OpenCLI port policy validation.
- [x] Require `--port auto`.
- [x] Require sanitized codex-port lease receipt in `39300-39499`.
- [x] Add tests for missing lease, hard-coded port, and wrong range.
- [ ] Run local verification and archive the OpenSpec change.
