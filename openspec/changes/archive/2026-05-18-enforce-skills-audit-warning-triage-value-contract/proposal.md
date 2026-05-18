# Proposal: enforce Skills audit warning-triage value contract

## Why

The Skills usage audit plan already requires `warning_triage` fields for post-warning review, but the field contract only checked presence and broad types. A stale or manually edited report could therefore retain unknown triage statuses, broad-window policy names, unsupported skipped-loading review actions, malformed blockers, or negative counts while still looking structurally complete.

## What changes

- Add explicit allowed values for `warning_triage.status`, `window_policy`, `skipped_loading_review`, and known blockers.
- Reject non-string or unknown blockers, blocked status without blockers, blockers on non-blocked statuses, and negative warning/skipped-loading counts.
- Add regression coverage for the warning-triage value contract.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
