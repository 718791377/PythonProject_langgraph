# Design: Project MOE Readiness Output Contract

## Decision

Expose `warnings`, `checked_files`, and `redacted_paths` as additive top-level readiness fields. Keep existing detailed nested readiness data for operator diagnostics.

## Safety

The fields are derived from already-read metadata and target-relative path candidates. They do not read private prompt bodies and do not write target projects.

## Verification

Use Project MOE toolchain regression tests and OpenSpec validation before local integration.
