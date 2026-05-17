# Proposal: enforce skills-audit recommendation threshold contract

## Why

The Skills usage audit converts `module_evidence` rows into advisory recommendations. The row shape is now validated, but a stale or edited row could still carry a recommendation that contradicts its strong evidence count, weak mention count, or candidate threshold.

## What changes

- Add a shared recommendation-threshold helper for module evidence rows.
- Validate that each row recommendation matches its `strong_total`, `weak_plugin_mentions`, and `default_candidate_threshold`.
- Add regression coverage for stale recommendation-threshold mismatches.
- Update the bilingual Skills usage audit plan and stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state.
