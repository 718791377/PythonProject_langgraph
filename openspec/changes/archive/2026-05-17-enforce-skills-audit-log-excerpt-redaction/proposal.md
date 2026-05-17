# Proposal: enforce skills-audit log-excerpt redaction markers

## Why

Skills usage audit log excerpts are retained as sanitized evidence. When a long excerpt is truncated immediately after path or secret redaction, a partial marker such as `[RE` can appear. That is not a secret leak, but it makes reviewer evidence ambiguous and undermines confidence in the sanitization boundary.

## What changes

- Preserve complete redaction markers when sanitized log excerpts are truncated.
- Add a regression test covering truncation across `[REDACTED_PATH]` / `[REDACTED_SECRET]` boundaries.
- Update bilingual audit-plan text and stable governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, or hard-load settings.
