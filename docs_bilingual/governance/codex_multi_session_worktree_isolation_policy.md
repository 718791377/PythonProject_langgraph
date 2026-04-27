---
doc_id: codex_multi_session_worktree_isolation_policy
lang: en
doc_class: governance
status: active
---

# Codex Multi-Session Worktree Isolation Policy

## 1. Purpose

This policy defines how concurrent Codex sessions must work in this repository without creating unsafe dirty files, branch drift, or cross-session overwrite risk.

The core rule is:

```text
one writable task equals one Git worktree plus one feature branch
```

The repository root `D:\PythonProject_langgraph` is the coordination and mainline mirror location. It must not become an informal shared scratch workspace for multiple sessions.

## 2. Authority Boundary

This policy is repository governance. It applies to all Codex sessions that edit this repository, including normal Codex, oh-my-codex wrapped sessions, native subagents, durable-team workers, and future LangGraph-driven execution contexts.

It does not authorize deleting worktrees, resetting branches, or discarding local edits. Any destructive cleanup still needs an explicit preservation-first plan and operator confirmation.

## 3. Required Worktree Model

- `main` - local branch that mirrors reviewed `gitlab/main`; do not use it as a writable task branch.
- `gitlab/main` - remote-tracking branch for the authoritative GitLab mainline.
- `github/main` - post-merge mirror branch after GitLab main is green.
- `.worktrees/` - local container for secondary Git worktrees; it is local Git workspace infrastructure, not a documentation or source directory.
- `backup/*` - preservation branch namespace for local dirty-worktree snapshots before risky alignment operations.

Every writable task must use:

1. A dedicated feature branch whose name describes the task.
2. A dedicated worktree under `.worktrees/`.
3. A GitLab-first MR before the result enters `main`.

## 4. Multi-Session Safety Rules

Concurrent sessions may prepare independent work in parallel only when their write scopes are isolated.

Required rules:

- Do not let two sessions write to the same worktree.
- Do not let two sessions edit the same hotspot files without leader-owned serialization.
- Do not write directly on `main`.
- Do not manually delete `.worktrees/`; use Git worktree commands after preservation checks.
- Do not assume a dirty file belongs to the current session.
- Do not reset, checkout, clean, move, or delete unknown dirty files until their owning session or backup branch is identified.
- After a GitLab MR merges, fast-forward the local `main` branch reference to the exact GitLab main commit, then sync that exact commit to GitHub.

## 5. Dirty File Classification

Dirty files must be classified before action:

- current-task edits - files intentionally changed by the current session.
- other-session edits - files likely owned by another live or recently interrupted session.
- generated artifacts - files produced by checks, refreshes, or reports.
- scratch notes - local notes that are not yet approved formal documentation.
- stale residue - abandoned worktree or generated output that needs a preservation-first cleanup plan.

If ownership is unknown, keep the file and report it. Do not delete it as a shortcut.

## 6. Script Control

Prompt reminders are not sufficient for this safety boundary.

The repository provides:

- `tools/check_worktree_session_hygiene.py` - read-only checker that inspects registered Git worktrees, dirty states, duplicate dirty paths, and `main` alignment risk.

Expected usage:

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --json
```

The command above runs the read-only hygiene checker and emits a JSON report for cold-start sessions or CI.

For local pre-commit style verification while the current feature branch is intentionally dirty, use:

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --allow-current-dirty --json
```

The `--allow-current-dirty` option allows the current non-main worktree to be dirty while still flagging dirty `main` and cross-worktree collision risks.

## 7. GitLab-First Integration

All repository changes still follow the GitLab-first publication workflow:

1. Create a feature branch from the latest `gitlab/main`.
2. Use a dedicated `.worktrees/<task>` worktree for that branch.
3. Push to GitLab and open a GitLab MR.
4. Wait for the GitLab pipeline to pass.
5. Merge into GitLab `main`.
6. Sync the exact GitLab main commit to GitHub.
7. Fast-forward the local `main` branch reference.

GitHub PRs are not the default workflow for this repository.

## 8. OpenSpec Lifecycle

Changes that create or alter this policy are structural repository-governance changes and must follow the repository OpenSpec lifecycle.

Required lifecycle:

1. Create or update an OpenSpec change before implementation.
2. Keep the governance policy, checker behavior, and guard integration aligned with that change.
3. Run the repository validation commands before publication.
4. Archive the completed OpenSpec change so its delta spec becomes a stable spec.
5. Publish the archive and stable spec through the GitLab-first workflow.

Archive isolation rule:

- For changes that affect code, executable checks, CI, stable specs, startup instructions, repository instruction surfaces, or structural governance rules, perform the archive in a dedicated archive worktree before it is merged back. A dedicated archive worktree is a separate Git worktree used only for the archive branch and its generated stable-spec updates.
- The archive worktree must pass the relevant validation commands before the archive branch is committed. After the archive branch is integrated into the main workspace, the main workspace must pass validation again.
- Purely explanatory text edits may use a lighter archive flow when they do not change enforceable repository behavior, but unclear cases should use the dedicated archive worktree flow.

Do not leave a completed worktree-isolation OpenSpec change active after the implementation has already merged to `main`. A completed active change is a lifecycle gap, even when its tasks are all checked.
