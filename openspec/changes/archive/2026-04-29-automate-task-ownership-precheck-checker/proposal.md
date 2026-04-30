# Proposal: Automate task ownership precheck

## Why

The governance policy now requires a task ownership precheck before new worktrees, edits, guard repairs, OpenSpec takeovers, or governance repairs. Today the checker only validates explicit claim collisions, leaving branch, worktree, OpenSpec-change, MR, and ignored-file semantic ownership checks as manual operator work.

## What Changes

- Extend `tools/check_session_ownership_claims.py` with an optional task ownership precheck mode that reports semantic ownership signals before a new write scope is created.
- Detect matching Git worktrees, local branches, remote-tracking branches, active OpenSpec changes, active session claims, and ignored/local-only guard-scanned files.
- Add optional GitLab MR inspection for environments with a GitLab token and remote metadata.
- Update governance wording so the checker is the primary executable surface for this rule while still requiring operator classification of any signal.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-repository-multi-session-worktree-isolation`: the session ownership checker gains task ownership precheck behavior for semantic ownership signals beyond explicit claim-file collisions.

## Impact

- Affected code: `tools/check_session_ownership_claims.py` and its tests.
- Affected governance: bilingual multi-session worktree isolation policy wording.
- No new runtime dependency is required; GitLab MR inspection uses the Python standard library and existing token environment variables when requested.
- No CI network dependency is introduced because GitLab MR inspection is opt-in for task-precheck calls and not part of the default guard invocation.
