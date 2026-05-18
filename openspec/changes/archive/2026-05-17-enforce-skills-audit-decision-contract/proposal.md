# Proposal: enforce skills-audit decision recommendation contract

## Why

The Skills usage audit now exposes advisory decision buckets in JSON and sanitized Markdown output. Those buckets influence later human review, so the report field contract must prove they remain advisory-only, complete, type-safe, and count-consistent before a report can feed profile decisions or candidate generation.

## What changes

- Validate `decision_recommendation` required fields, advisory status, non-apply flag, bucket names, string-only bucket entries, and `bucket_counts` consistency.
- Add regression coverage for broken advisory decision recommendations.
- Document the contract in the bilingual Skills usage audit plan.
- Promote the stable skills-governance spec with an explicit decision-recommendation field-contract requirement.

## Safety

This remains audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state.
