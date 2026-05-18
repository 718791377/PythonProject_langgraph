# Proposal: enforce skills-audit module evidence row contract

## Why

The Skills usage audit uses `module_evidence` as the evidence source for advisory decision buckets and later profile-candidate records. If module rows are missing fields, count mapped tool calls as strong evidence, carry stale strong totals, or skip manual cross-project review, downstream decisions can look more certain than the evidence actually supports.

## What changes

- Validate every `module_evidence` row in the report field contract.
- Require string plugin entries, non-negative integer counts, strong-total consistency, mapped-tool medium-evidence policy, manual cross-project review, and approved advisory recommendations.
- Add regression coverage for invalid module evidence rows.
- Update the bilingual Skills usage audit plan and stable skills-governance spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state.
