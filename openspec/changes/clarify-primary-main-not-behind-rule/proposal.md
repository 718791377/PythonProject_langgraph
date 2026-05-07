# Proposal: Clarify primary main worktree freshness rule

## Summary

Clarify that `D:\PythonProject_langgraph` is the primary main worktree, must remain checked out on local `main`, and must not lag behind local `main`. Local `main` must not lag behind the latest fetched `gitlab/main` before writable work, release timing, push, MR creation or update, or mainline-state claims.

## Motivation

The previous wording said the primary directory must be aligned with `main`. That sounded like exact equality everywhere and did not clearly express the intended freshness chain:

```text
primary main worktree must not lag local main; local main must not lag latest gitlab/main
```

The policy also needs checker-backed enforcement so the rule is not only a prompt reminder.

## Scope

- Update `AGENTS.md`, the repository instruction surface.
- Update the bilingual worktree-isolation governance policy.
- Update `tools/check_worktree_session_hygiene.py` so stale local `main` behind `gitlab/main` is an error, while local `main` ahead of `gitlab/main` is treated as not lagging.
- Add unit tests for behind and ahead cases.

## Non-Goals

- Do not authorize feature implementation directly on primary `main`.
- Do not push or merge `main` directly.
- Do not clean or delete existing worktrees.
