# Proposal: Add release timing recommendation rule

## Summary

Require the active session's model to judge whether a local batch is ready for remote publication and recommend publish or wait to the user before pushing to GitLab.

## Scope

- Update repository publication instructions.
- Update startup summaries.
- Update the multi-session worktree isolation governance policy.
- Add a stable OpenSpec requirement for model-proposed release timing recommendations.

## Non-Goals

- Do not make the model the final release authority.
- Do not bypass GitLab-first review, GitLab pipeline gates, or GitHub post-merge mirroring.
- Do not add runtime scripts in this docs-only change.
