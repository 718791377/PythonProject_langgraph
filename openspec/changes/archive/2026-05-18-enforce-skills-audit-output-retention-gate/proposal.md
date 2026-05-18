# Proposal: enforce Skills audit output-retention gate

## Why

The Skills usage audit intentionally writes raw JSON reports under `.tmp/` while collecting one month of usage evidence. Those reports can include derived session/log evidence and are local review artifacts, not durable Git evidence. Without an executable retention gate, a forced add or misplaced raw `skills-usage-*.json` report could bypass the plan's data-minimization rule.

## What changes

- Add `tools/check_skills_audit_output_retention.py` to block `.tmp/` artifacts and raw Skills usage audit JSON from Git retention.
- Register the checker in the OpenSpec guard, safety-rule backing registry, CI test manifest, and guard JSON aggregation test.
- Update the bilingual Skills usage audit plan and stable skills-governance lifecycle spec.
- Add regression coverage for allowed sanitized Markdown summaries and blocked raw JSON artifacts.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state. It only prevents local-only raw audit output from becoming durable repository evidence.
