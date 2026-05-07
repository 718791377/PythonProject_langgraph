# Design: Primary main worktree freshness

## Rule Model

The rule is expressed as a freshness chain rather than a blanket equality phrase:

```text
primary main worktree must not lag local main; local main must not lag latest gitlab/main
```

In normal operation, the primary directory `D:\PythonProject_langgraph` is checked out on local `main` and its HEAD exactly equals the local `main` branch reference. Feature implementation still belongs in dedicated feature worktrees and feature branches.

## Checker Behavior

`tools/check_worktree_session_hygiene.py` keeps the existing primary-worktree checks and changes the local-main-to-remote comparison from equality-only to ancestry-aware freshness:

- local `main` equals `gitlab/main`: pass with an informational match message;
- local `main` is behind `gitlab/main`: fail and instruct fast-forward before writable work or publication;
- local `main` is ahead of `gitlab/main`: pass as not-behind, with an operator reminder not to use primary `main` for feature work;
- local `main` diverged from `gitlab/main`: fail and require mainline reconciliation.

## Rollback

This change is reversible by restoring the previous policy wording and equality-only checker warning, but the stronger behind check is preferred because it makes the freshness rule script-backed.
