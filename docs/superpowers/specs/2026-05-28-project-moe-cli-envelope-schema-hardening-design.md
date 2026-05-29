# Design: Project MOE CLI Envelope Schema Hardening

## Current State

`require_cli_envelope()` validates the common JSON envelope shape for read-contract commands. It already rejects non-object payloads, missing common fields, command echo mismatches, bad ok/token pairs, CLI contract mismatches, and private-field exposure.

## Gap

A target Mode CLI can currently include a `schema_version` field with an unsupported value while still passing the rest of the common envelope checks. That creates an ambiguous compatibility state for the GUI readiness gate.

## Decision

Add a dedicated blocker, `blocked:cli_envelope_schema_version_mismatch`, when `payload["schema_version"] != SCHEMA_VERSION`. The blocker belongs to the `mode_cli_contract` repair category, requires target-project write to repair, and is returned through the existing readiness checker remediation plan.

## Safety Notes

- The check is read-only and only inspects JSON already emitted by safe read commands.
- Static-only mode remains non-executing.
- Static blockers and dirty target state still prevent CLI execution before this check can run.
- Private prompt sources, Agent TOMLs, and `.omx/state` are not read or written by this change.

## Verification Focus

- Ready fixtures still pass.
- A CLI envelope with unsupported `schema_version` fails closed in the read-contract path.
- The readiness output keeps `control_mode_allowed=false` and exposes the stable blocker/remediation group.
