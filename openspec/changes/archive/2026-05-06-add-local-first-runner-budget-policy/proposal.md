# Proposal: Add local-first runner budget policy

## Summary

Document a local-first batching policy that keeps GitLab-first publication intact while reducing avoidable GitLab runner-minute consumption.

## Scope

- Update repository startup instructions with local-first batching guidance.
- Update startup summaries so cold-start sessions see the runner-budget rule early.
- Update the multi-session worktree governance policy to make local validation the default before remote push.
- Add an OpenSpec delta requirement for local-first MR batching and early remote pipeline exceptions.

## Non-Goals

- Do not disable GitLab-first review and merge authority.
- Do not remove GitLab pipelines or CI gates.
- Do not change GitHub from post-merge mirror behavior.
- Do not add runtime scripts in this docs-only change.
