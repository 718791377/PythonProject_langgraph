---
change: harden-project-moe-cli-envelope-schema-20260528
design-doc: docs/superpowers/specs/2026-05-28-project-moe-cli-envelope-schema-hardening-design.md
status: active
---

# Plan: Harden Project MOE CLI Envelope Schema

1. Add the OpenSpec package and management checklist.
2. Add `blocked:cli_envelope_schema_version_mismatch` to the blocker catalog.
3. Validate `schema_version == SCHEMA_VERSION` inside `require_cli_envelope()`.
4. Add a regression fixture where the target read CLI emits an unsupported envelope schema.
5. Update the implementation-plan checklist only for evidence covered by tests.
6. Run targeted tests and repository gates before local main integration.
