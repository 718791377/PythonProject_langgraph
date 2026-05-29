---
change: enforce-opencli-port-auto-governance-20260528
status: implemented
---

# Design: Enforce OpenCLI port-auto governance

## Problem

OpenCLI was already on-demand and owner/authorization-gated, but the guard did not enforce the documented `--port auto` and codex-port lease receipt boundary.

## Decision

Add a non-mutating port policy gate to `tools/opencli_governance.py`:

- default port mode is `auto`;
- any hard-coded value such as `--port 39300` is blocked;
- a sanitized codex-port lease receipt is required;
- the lease must be owned by `codex`, sanitized, and in range `39300-39499`.

## Safety

The guard still does not install OpenCLI, start OpenCLI, bind ports, open browsers, read cookies, execute JavaScript, click, type, or navigate.
