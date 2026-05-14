# Design

## Scope
This change adds a fail-closed publication approval boundary for repository remote publication.

## Boundary model
The workflow has two distinct approval gates:

1. Local integration approval: authorizes validated feature work to enter local `main`.
2. Remote publication approval: authorizes external state changes after local integration, including GitLab push/MR, GitLab MR merge, GitHub mirror sync, and remote source-branch deletion.

A generic continuation such as `continue`, `go on`, `proceed`, or a localized equivalent is not enough to cross the remote publication gate unless the current user message explicitly names remote publication, GitLab push/MR/merge, GitHub sync/mirror, or equivalent remote action.

## Enforcement approach
`tools/check_remote_publication_approval_policy.py` verifies stable snippets in:

- `AGENTS.md` - startup instruction surface for publication behavior
- both startup summaries
- both multi-session worktree governance docs
- `openspec/specs/codex-repository-multi-session-worktree-isolation/spec.md` - stable OpenSpec authority for worktree and publication rules
- the safety-rule registry
- `tools/run_openspec_guard.py` - shared guard entrypoint used by local and remote CI

The checker is added to `tools/run_openspec_guard.py` so local and remote CI fail when the rule drifts.

## Non-goals
- No automatic remote publishing helper in this slice.
- No Git hook installation in this slice.
- No remote API or `git push` execution in this slice.
