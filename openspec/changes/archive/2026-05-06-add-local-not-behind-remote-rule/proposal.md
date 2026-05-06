# Proposal: Add local not-behind-remote rule

## Summary

Require the local repository baseline to stay current with the authoritative GitLab remote before writable work and remote publication.

## Scope

- Update repository publication instructions.
- Update startup summaries.
- Update the multi-session worktree isolation governance policy.
- Add an OpenSpec requirement for local remote freshness before work and publication decisions.

## Non-Goals

- Do not disable local-first batching.
- Do not require pushing every local checkpoint.
- Do not allow destructive reset or cleanup of dirty work to force alignment.
