# Main Worktree to GitLab Main Alignment Safety Plan

## Status

This plan is active for the current repository maintenance task. It defines how to preserve local work before aligning the primary worktree with `gitlab/main` - the GitLab remote-tracking branch that represents the authoritative reviewed mainline.

## Background

The primary worktree at `D:\PythonProject_langgraph` - the normal local checkout directory for this repository - is not currently aligned with `gitlab/main` - the GitLab main branch reference used as the review-authoritative source of truth.

The current primary worktree also has tracked modifications and untracked files. Some of those files may be useful local work from another session, while others may be stale refresh output or scratch notes. Therefore the alignment operation MUST be treated as a preservation-first maintenance task, not a cleanup shortcut.

## Goals

- Preserve local changes before any destructive Git operation.
- Classify files into remote-only, local-only, both-changed, and already-equal categories before choosing what to keep.
- Align the local `main` branch - the local branch intended to mirror GitLab main - to `gitlab/main` only after backup evidence exists.
- Keep registered worktrees under `.worktrees/` - the local folder that contains Git-managed secondary worktrees - out of commits and out of manual deletion.
- Provide recovery instructions so a cold-start session can restore local changes from the backup branch.

## Non-Goals

- This plan does not decide that local changes are worthless.
- This plan does not delete `.worktrees/` - the local container for registered secondary worktrees.
- This plan does not bypass the GitLab-first publication workflow.
- This plan does not merge local scratch notes into documentation automatically.
- This plan does not push backup branches unless the operator explicitly asks for a remote backup.

## Required Terms

- `D:\PythonProject_langgraph` - the primary local repository worktree that the operator normally opens.
- `gitlab/main` - the remote-tracking reference for the GitLab main branch and the reviewed source of truth.
- `main` - the local branch that should match `gitlab/main` after alignment.
- `HEAD` - the current commit checked out in the active worktree.
- `merge-base` - the common ancestor commit used to distinguish local drift from remote progress.
- `backup/mainworktree-dirty-before-main-align-<timestamp>` - the local backup branch name pattern used to preserve the current dirty worktree.
- `.worktrees/` - the local directory used to hold Git-registered secondary worktrees for isolated branch work.
- `.git/info/exclude` - the local-only ignore file that hides machine-local paths without changing repository-tracked `.gitignore`.

## Phase 0: Read-Only Inventory

Before creating a backup or resetting anything, run read-only checks:

```powershell
git fetch gitlab main
```

This command refreshes the `gitlab/main` reference from GitLab without changing working files.

```powershell
git rev-parse HEAD
```

This command prints the current worktree commit so the backup can be traced.

```powershell
git rev-parse gitlab/main
```

This command prints the latest GitLab main commit so the alignment target is explicit.

```powershell
git merge-base HEAD gitlab/main
```

This command prints the common ancestor used to determine whether the worktree is behind GitLab main.

```powershell
git status --porcelain=v1 --untracked-files=all
```

This command lists tracked and untracked local changes in a stable machine-readable format.

```powershell
git diff --name-status HEAD gitlab/main
```

This command lists paths that changed on GitLab main after the current `HEAD`.

## Phase 1: Classification

Classify every path before alignment:

- Remote-only path: changed in `gitlab/main` but not changed locally, so the GitLab version can be accepted directly.
- Local-only path: changed locally but not in `gitlab/main`, so it must be preserved in a backup before alignment.
- Both-changed path: changed locally and in `gitlab/main`, so it needs a later manual merge or selective migration.
- Already-equal path: appears dirty locally but already matches `gitlab/main`, so it can be reset safely after backup evidence exists.

The current observed categories in this repository include:

- `AGENTS.md` - repository startup and routing instruction file, currently newer on `gitlab/main`.
- `docs_bilingual/project_startup_summary.md` - English startup summary, currently both-changed and requiring merge review if local additions matter.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup summary, currently both-changed and requiring merge review if local additions matter.
- `tools/run_openspec_guard.py` - OpenSpec guard entry script, currently both-changed and requiring merge review.
- `.worktrees/` - registered secondary worktree container, currently local-only and not a commit candidate.
- `commn_layer.md` - local scratch note, currently local-only and requiring operator review.
- `reference.md` - local scratch reference list, currently local-only and requiring operator review.
- `rollout20260422.md` - local rollout note, currently local-only and requiring operator review.

## Phase 2: Backup

Create a local backup branch before aligning:

```powershell
git switch -c backup/mainworktree-dirty-before-main-align-<timestamp>
```

This command creates a local backup branch from the current dirty worktree without changing file content.

```powershell
git add -A -- . ':(exclude).worktrees/**'
```

This command stages all current local changes while excluding `.worktrees/`, because registered worktrees must not be committed as ordinary files.

```powershell
git commit -m "Backup dirty main worktree before aligning main"
```

This command stores the dirty worktree snapshot in a local backup commit for later recovery.

If untracked scratch files should not enter the backup commit, copy them first to a local backup folder:

```powershell
New-Item -ItemType Directory -Force .local\main-align-backups\<timestamp>
```

This command creates a local backup folder for scratch files that should not be committed.

```powershell
Copy-Item commn_layer.md, reference.md, rollout20260422.md .local\main-align-backups\<timestamp>\ -ErrorAction SilentlyContinue
```

This command copies the known scratch note files into the local backup folder when they exist.

## Phase 3: Align the Primary Local Main Branch

After the backup commit exists, align the local `main` branch:

```powershell
git switch main
```

This command changes the primary worktree to the local branch intended to mirror GitLab main.

```powershell
git reset --hard gitlab/main
```

This command makes tracked files on local `main` exactly match `gitlab/main`.

Add the registered worktree container to local-only ignore rules:

```powershell
Add-Content .git\info\exclude "`n.worktrees/"
```

This command tells only this local checkout to ignore `.worktrees/` without changing repository-tracked ignore rules.

## Phase 4: Verify Alignment

Run final checks:

```powershell
git status --short --branch
```

This command verifies that the current branch is `main` and reports any remaining local files.

```powershell
git rev-parse HEAD
```

This command prints the local `main` commit after alignment.

```powershell
git rev-parse gitlab/main
```

This command prints the GitLab main commit; it should match the local `HEAD`.

## Phase 5: Recover or Migrate Local Updates Later

If a local-only or both-changed path must be restored later, start from the backup branch rather than from memory:

```powershell
git show backup/mainworktree-dirty-before-main-align-<timestamp>:<path>
```

This command prints a saved file from the backup branch for manual review.

```powershell
git checkout backup/mainworktree-dirty-before-main-align-<timestamp> -- <path>
```

This command restores one selected path from the backup branch into a clean feature branch.

Any restored change must use the GitLab-first workflow:

- Create a feature branch from `gitlab/main` - the latest reviewed mainline.
- Restore only the selected path or logical slice - the minimal change set being reviewed.
- Run repository checkers - the validation scripts that protect OpenSpec and documentation rules.
- Open a GitLab merge request - the authoritative review surface for this repository.
- Sync GitHub only after GitLab main is merged and green - the mirror step for the GitHub repository.

## Rollback

If the alignment operation produces an unexpected result, return to the backup branch:

```powershell
git switch backup/mainworktree-dirty-before-main-align-<timestamp>
```

This command returns the worktree to the backup branch that preserved local changes.

If local `main` needs to be restored again later, repeat Phase 3 after confirming the backup branch still exists.

## Validation

This plan is valid when:

- the backup branch exists before any `git reset --hard` command is run;
- `.worktrees/` is excluded from commits and not manually deleted;
- local `main` and `gitlab/main` resolve to the same commit after alignment;
- any local-only or both-changed content is migrated only through a new GitLab-first branch and merge request.
