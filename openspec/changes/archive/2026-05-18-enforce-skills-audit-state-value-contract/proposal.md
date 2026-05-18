# Proposal: validate Skills audit state values

## Why

The Skills usage audit plan defines an audit-only state machine, but the report field contract only required the `audit_state` fields to exist and have basic types. A manually edited or stale report could therefore carry an unknown state, a truthy `profile_apply_allowed`, or malformed blocker fields while still passing parts of downstream review.

## What changes

- Restrict `audit_state.state` to the approved audit-only lifecycle values.
- Require `audit_state.profile_apply_allowed=false` in the field contract.
- Require audit-state blocker fields to be lists of strings when present.
- Add regression coverage for invalid state values, non-false profile-apply allowance, and malformed blocker lists.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load state, remote refs, or live plugin state.
