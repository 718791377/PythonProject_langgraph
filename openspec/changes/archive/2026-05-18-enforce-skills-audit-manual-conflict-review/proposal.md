# Proposal: expose Skills audit manual conflict review

## Why

The Skills usage audit plan allows sanitized manual notes for medium evidence, urgent exceptions, and false-positive dispositions. The report already counted manual notes, but it did not separately expose when a manual exception or approved hard-load exception required disposition before a profile decision. That could make manual judgment look like it silently overrides script evidence.

## What changes

- Add `manual_evidence.conflict_review` to JSON reports.
- Mark `exception` and `approved hard-load exception` manual notes as requiring conflict/exception disposition.
- Validate conflict-review fields in the report field contract.
- Render conflict-review state in sanitized Markdown summaries.
- Add regression coverage for exception notes and malformed conflict-review fields.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
