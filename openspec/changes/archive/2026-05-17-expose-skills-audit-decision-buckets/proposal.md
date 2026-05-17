# Proposal: expose skills-audit advisory decision buckets

## Why

The 30-day Skills usage audit summary must help reviewers distinguish modules that are candidates for profile review from modules that should remain on-demand, require manual review, or stay dormant/restorable. The previous summary gave general warnings but did not render an explicit bucketed decision view.

## What changes

- Build non-mutating decision buckets from `module_evidence`.
- Render profile-review candidates, on-demand soft-load modules, manual-review medium/weak modules, and dormant/restorable modules in the sanitized Markdown summary.
- Keep profile apply explicitly disallowed in the audit summary; any apply still requires a separate candidate record and explicit authorization.
- Update tests, bilingual audit-plan text, and the stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, or remote refs.
