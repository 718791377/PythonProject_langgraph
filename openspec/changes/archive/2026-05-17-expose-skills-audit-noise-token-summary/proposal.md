# Proposal: expose skills-audit noise token samples in summaries

## Why

The Skills usage audit already removes generic or unknown explicit-skill tokens such as `and`, `from`, and `draft` from strong evidence. A reviewer reading only the sanitized Markdown summary should be able to see which sanitized tokens were removed without opening raw JSON or session transcripts.

## What changes

- Render a bounded sanitized sample list of removed explicit-skill noise tokens in the audit Markdown summary.
- Render `none` when no explicit-skill noise token was removed.
- Keep removed tokens out of strong evidence and re-sanitize samples before Markdown rendering.
- Update regression coverage, bilingual audit-plan text, and the stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, or remote refs.
