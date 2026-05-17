# Proposal: enforce skills-audit manual-note path privacy

## Why

Manual evidence notes are intentionally local and usually live under `.tmp/` or user-level Codex folders. The audit script already sanitizes note field values, but invalid-note metadata can still preserve source paths for missing files or malformed notes. Those paths should not become retained report evidence.

## What changes

- Redact and bound manual-note source paths before storing them in `manual_evidence.invalid_notes`.
- Add manual-evidence source-path privacy fields to the report field contract.
- Fail the field contract if manual evidence retains raw source paths, private paths, raw secret assignments, or standalone tokens.
- Update bilingual audit-plan text and regression tests.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, or hard-load/profile settings.
