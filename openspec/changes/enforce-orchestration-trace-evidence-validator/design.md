## Context

The existing `tools/check_orchestration_activation_policy.py` verifies that required policy snippets exist across durable instruction surfaces. This change adds a narrower evidence validator for actual activation trace text.

The validator is intentionally text-oriented and local-first. It can inspect a transcript, report, or saved trace file without launching workers or mutating durable state.

## Decisions

- Implement a standalone Python checker at `tools/check_orchestration_trace_evidence.py`.
- Accept either a file path argument or stdin-style future extension only if needed later; this slice uses explicit file input for deterministic tests.
- Parse `key=value` fields from trace text while tolerating both one-line and multi-line trace formats.
- Require the exact fields needed by the activation policy.
- Keep vocabulary checks small and policy-backed rather than trying to infer every future role or lane.
- Treat timeout text as unsafe unless it includes an allowed evidence label such as `expert timed out; not used as evidence`, `main session took over verification`, `respawn`, or `bounded wait`.

## Risks

- The checker may be too strict for free-form traces. Mitigation: require only policy-critical fields and vocabularies.
- The checker may be too weak for full runtime adoption. Mitigation: this is a trace-evidence validator, not a replacement for runtime integration tests.
- Chinese localized traces may use non-English prose. Mitigation: required machine-readable trace fields remain English key/value tokens as defined by policy.

## Rollout

1. Add the checker and tests.
2. Update governance docs and stable spec with trace-evidence validation requirements.
3. Validate locally without adding CI manifest registration in this slice because `tools/ci/ci_test_manifest.json` is owned by another active claim.
