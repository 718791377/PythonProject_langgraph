# Proposal: expose skills-audit cadence summary

## Why

The Skills usage audit plan requires weekly cadence, late-run recovery, and missed-weekly-run markers to remain visible during the 30-day review. The JSON report already carried a top-level `cadence_review` object, but the nested field contract and sanitized Markdown summary did not make cadence drift independently reviewable.

## What changes

- Add decision-critical `cadence_review` nested-field validation to the audit report field contract.
- Render late-run status, missed weekly runs, and weekly-report review status in sanitized Markdown summaries.
- Add regression coverage proving invalid cadence fields fail the field contract and candidate gate.
- Update bilingual audit-plan text and the stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, or remote refs.
