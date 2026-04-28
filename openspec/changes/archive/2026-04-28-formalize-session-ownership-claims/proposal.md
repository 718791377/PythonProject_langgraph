# Proposal: Formalize session ownership claims

## Why

The existing multi-session worktree hygiene checker catches dirty-worktree and duplicate-dirty-path problems after files have already changed. It does not catch the earlier coordination failure where two sessions both plan to archive or implement the same OpenSpec change.

## What Changes

- Provide a local claim surface under `.omx/session-claims/` - ignored local JSON files that declare the active session owner for an OpenSpec change or path scope.
- Add `tools/check_session_ownership_claims.py` - a read-only checker that validates claim files and fails on duplicate active claims.
- Integrate the checker into `tools/run_openspec_guard.py` - the repository aggregate guard script used before publication.
- Update the multi-session worktree governance policy with the claim workflow.

## Impact

- Do not store session claims in durable `.omx/state/` runtime truth.
- Do not require CI clean clones to create a claim file.
- Do not delete or mutate existing worktrees.
- Do not change user-level Codex configuration.
