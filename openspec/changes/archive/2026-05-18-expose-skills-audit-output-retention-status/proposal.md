# Proposal: expose Skills audit output-retention status

## Why

The output-retention checker now blocks `.tmp/` artifacts and raw Skills usage audit JSON from entering Git, but the audit report itself should also expose that gate status. Otherwise a reviewer reading a 30-day JSON report or sanitized Markdown summary cannot tell whether local-only raw outputs were kept out of durable evidence without running a separate command.

## What changes

- Add an `output_retention` field to Skills usage audit JSON reports.
- Validate output-retention status in the report field contract and candidate gate.
- Render output-retention status and long-term evidence format in sanitized Markdown summaries.
- Add regression coverage for the new field contract and summary rendering.
- Update the bilingual Skills usage audit plan and stable skills-governance lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state.
