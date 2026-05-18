# Proposal: expose skills-audit state blockers in summaries

## Why

The Skills usage audit state machine records closure, candidate, summary-review, pause, and warning-triage blockers in JSON. A human reviewer reading only the sanitized Markdown summary should not need to open raw JSON to understand why the audit cannot advance to summary review, closure, or candidate generation.

## What changes

- Render audit-state next action and profile-apply allowance in sanitized audit summaries.
- Render `close_blockers`, `candidate_blockers`, `summary_review_blockers`, `pause_blockers`, and `warning_triage_blockers` in sanitized audit summaries, using `none` when no blocker exists.
- Add regression coverage for blocked and unblocked audit-state summary output.
- Update bilingual audit-plan text and the stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, or remote refs.
