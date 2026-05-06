## Context

This repository uses `D:\PythonProject_langgraph` as the primary coordination directory and `.worktrees/` for task-specific feature branches. The primary directory can become misleading if it remains on a merged feature branch or stale branch after a cleanup operation. A future cold-start session may then treat that branch as the active mainline and make incorrect decisions.

The existing checker already detects dirty `main`, dirty feature worktrees, duplicate dirty paths, and local `main` versus `gitlab/main` drift. It needs one more local invariant: the primary registered worktree must itself be checked out on local `main` and match the local `main` reference.

## Goals / Non-Goals

Goals:

- Make the primary directory alignment rule explicit in startup and governance documents.
- Keep the rule separate from remote freshness. Local `main` versus `gitlab/main` remains the remote freshness check; primary directory versus local `main` is the local checkout-alignment check.
- Make `tools/check_worktree_session_hygiene.py` fail when the primary directory is on a feature branch, detached HEAD, or a HEAD that differs from local `main`.
- Preserve `.worktrees/` as the allowed place for feature-branch work.

Non-goals:

- Do not delete or reset any worktree.
- Do not require every local commit to be pushed immediately.
- Do not convert current local-ahead-of-remote batching into an error by itself.
- Do not change Codex runtime, MCP, OMX, or LangGraph behavior.

## Decisions

### Decision 1: Treat primary directory alignment as a local invariant

The checker will inspect the first registered worktree from `git worktree list --porcelain`, which is the main worktree Git associates with the repository. That worktree must be on local `main` and its HEAD must match `main`.

Why:

- It catches the exact failure mode where the main directory remains on an old branch.
- It does not break valid feature work in secondary `.worktrees/` directories.

### Decision 2: Keep remote freshness as warning-level unless local main is behind is handled by release workflow

This change does not make local `main` ahead of `gitlab/main` fail. Local-first batching may legitimately keep local commits before a GitLab MR is opened. The new script failure is only for primary directory versus local `main` mismatch.

Why:

- The user explicitly asked for alignment with the local Git repository.
- Existing publication governance already requires refreshing `gitlab/main` and fast-forwarding when local `main` is behind before new writable work or publication decisions.

### Decision 3: Expose alignment evidence in JSON

The checker will emit `primary_worktree_alignment` in its JSON payload.

Why:

- Cold-start sessions and CI logs need an explicit machine-readable field instead of inferring alignment from generic worktree lists.

## Risks / Trade-offs

- Risk: Running the checker from a feature worktree could be confused with primary directory alignment. Mitigation: the checker inspects registered worktrees and checks the primary registered worktree, not just the current working directory.
- Risk: A nonstandard repository layout could make the first worktree unexpected. Mitigation: this repository's governance defines the primary directory as `D:\PythonProject_langgraph`; nonstandard layouts can pass `--root` to the intended repository and inspect the emitted path.
- Risk: Local-ahead-of-remote batching could be mistaken as a failure. Mitigation: this change keeps local primary-directory alignment distinct from remote freshness.

## Migration Plan

1. Update OpenSpec proposal, design, tasks, and delta spec.
2. Update startup and governance documents.
3. Update the read-only checker and unit tests.
4. Run checker, unit tests, OpenSpec guard, name-clarity checker, and whitespace validation.
5. Keep changes local until the active session recommends a release and the user confirms publication.
