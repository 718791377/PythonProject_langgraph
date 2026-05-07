# Proposal: Prefer archive-before-publication MR packaging

## Why

Implementation-first publication followed by a separate archive MR leaves `main` with completed active changes and consumes extra GitLab pipeline minutes. The repository already prefers local-first batching, so small locally validated OpenSpec changes should publish as one complete package.

## What Changes

Make the repository publication workflow default to archiving completed local OpenSpec changes before opening the GitLab MR when the change is small, locally validated, and ready for publication.

The default package should contain implementation or documentation changes, the archived OpenSpec change, and the stable spec updates in one GitLab MR.

## Scope

- Update `AGENTS.md` publication workflow guidance.
- Update the bilingual multi-session worktree isolation governance policy.
- Update the bilingual OPSX project usage policy.
- Add OpenSpec requirements that distinguish the single-MR default from two-MR exceptions.

## Non-Goals

- Do not remove GitLab-first review and pipeline gates.
- Do not force large or risky implementation work to archive before remote review.
- Do not combine unrelated work only to reduce runner usage.
- Do not publish the branch without user confirmation.
