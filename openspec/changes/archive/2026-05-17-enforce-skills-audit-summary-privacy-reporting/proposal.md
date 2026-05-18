# Proposal: enforce skills-audit summary privacy reporting

## Why

The skills usage audit report already has field-contract privacy checks for explicit-skill noise tokens, manual-note source paths, and candidate source-report references. The human-facing Markdown summaries should surface those privacy gates directly so reviewers do not need to inspect raw JSON before deciding whether the evidence is safe to retain or use for profile decisions.

## What changes

- Show explicit-skill noise privacy fields in the sanitized audit Markdown summary.
- Show manual-note source-path privacy fields in the sanitized audit Markdown summary.
- Show source-report privacy violations in profile-candidate Markdown summaries.
- Update bilingual audit-plan text and regression tests.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, or hard-load settings.
