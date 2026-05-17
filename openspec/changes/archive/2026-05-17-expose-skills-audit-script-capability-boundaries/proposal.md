# Proposal: expose skills-audit script capability boundaries

## Why

The Skills usage audit helper is intentionally an evidence aid, not an omniscient fact source. The implementation plan already says 30-day summaries must explain what the script reliably covers and what still needs human review, but the generated report field contract did not yet make that boundary explicit.

## What changes

- Add `script_capability_boundaries` to the audit JSON report and field contract.
- Render the same boundary in sanitized Markdown summaries.
- Add regression coverage that missing or empty boundary lists block the field contract and candidate gate.
- Update bilingual audit-plan text and the stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, or hard-load settings.
