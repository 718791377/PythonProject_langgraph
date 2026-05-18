# Proposal: enforce Skills audit candidate-record contract

## Why

The Skills usage audit helper already builds preview-only profile apply candidates, but the retained candidate record itself did not have a dedicated self-contract. A stale, manually edited, or future-expanded candidate artifact could therefore omit rollback or validation details, carry unsafe apply-state flags, or retain a failed source-report privacy result while still looking like a structured candidate.

## What changes

- Add a candidate-record contract for profile apply candidate JSON/Markdown artifacts.
- Require preview-only approval state, non-mutating safety flags, explicit-authorization flags, passed source-report privacy, structured candidate gate fields, rollback restore information, and non-empty validation steps.
- Render the candidate-record contract in the Markdown candidate summary.
- Add regression coverage for malformed or unsafe candidate records.
- Update the bilingual implementation plan and stable skills-governance lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
