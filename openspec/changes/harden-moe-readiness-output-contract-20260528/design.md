# Design: Project MOE Readiness Output Contract

## Current State

`check_phase1_readiness()` already computes the adaptation lane, blockers, and `control_mode_allowed`. It also stores inspected surfaces inside nested objects such as `agent_toml`, `mode_cli_surface`, wrappers, startup hooks, and operator docs.

## Gap

GUI preflight and rollout evidence need a stable top-level summary of checked files and redacted path aliases. Without those fields, callers must infer evidence from nested implementation details.

## Decision

Add a small derived contract layer to the readiness payload:

- `warnings`: machine-readable warning records; empty when no warning exists.
- `checked_files`: stable records for every target-project file candidate inspected by Phase 1 readiness.
- `redacted_paths`: stable aliases and relative paths safe for logs and UI evidence.

The new fields are additive and do not remove existing absolute operator-facing fields.

## Safety Notes

- The checker remains read-only.
- Private prompt body content is still not read or copied.
- Paths in `checked_files` are target-relative values or redacted aliases, not private prompt bodies.
- Static-only execution remains non-executing.

## Verification Focus

- Ready Lane output includes all required contract fields.
- Static-only output includes a warning and still blocks control.
- Existing readiness lane behavior remains unchanged.
