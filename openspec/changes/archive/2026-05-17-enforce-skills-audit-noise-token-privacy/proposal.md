# Proposal: enforce skills-audit noise-token privacy

## Why

Recent warning-triage output showed `explicit_skill_noise_removed` can contain path fragments, long mojibake strings, and non-skill payload tokens. Even though these tokens are excluded from strong evidence, they should not be retained raw in audit reports or candidate evidence.

## What changes

- Sanitize and truncate rejected explicit-skill noise tokens before they enter report JSON.
- Add `noise_review` to the report field contract with privacy and retention fields.
- Fail the field contract when noise tokens contain raw private paths, secrets, or exceed the fixed token length.
- Update the bilingual audit plan and regression tests.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, or hard-load/profile settings.
