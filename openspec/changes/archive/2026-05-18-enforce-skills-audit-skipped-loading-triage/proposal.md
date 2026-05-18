# Proposal: expose skipped-loading warning triage in Skills audit

## Why

The Skills usage audit plan says `Skipped loading` warnings should be recorded at source before any vendor-cache edit. The audit helper already collected skipped-loading log rows, but the `warning_triage` state did not expose skipped-loading counts or a review policy, so a post-warning run could miss invalid-skill metadata pressure.

## What changes

- Add skipped-loading count, sample count, and review policy fields to `warning_triage`.
- Validate those fields in the report field contract.
- Render skipped-loading triage state in sanitized Markdown summaries.
- Keep skipped-loading log samples sanitized before report retention.
- Add regression coverage for skipped-loading triage and malformed triage fields.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
