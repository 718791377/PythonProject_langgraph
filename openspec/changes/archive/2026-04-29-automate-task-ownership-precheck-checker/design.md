# Design: Automate task ownership precheck

## Overview

Add an optional precheck mode to the existing read-only session ownership checker. The default checker behavior remains unchanged for CI and `run_openspec_guard.py`; precheck mode is enabled only when a task, term, target path, or OpenSpec change is provided.

## CLI surface

- `--precheck-task <text>` derives deterministic search terms from a human task description or branch-style slug.
- `--precheck-term <term>` adds an explicit semantic matching term.
- `--target-path <path>` adds a repository-relative path scope to match against claim paths and ignored/local-only files.
- `--openspec-change <change>` adds an exact active-change or claim-change target.
- `--check-gitlab-mrs` attempts open GitLab MR inspection using the `gitlab` remote and token environment variables.
- `--require-gitlab-mrs` fails if GitLab MR inspection cannot run.

## Matching model

The checker uses deterministic substring matching over normalized slugs plus exact path-overlap checks. It does not attempt LLM-style fuzzy matching. This keeps results reproducible and suitable for scripts.

Ownership state is classified as:

- `unclaimed`: no signal matched.
- `claimed-not-started`: a clean matching branch, worktree, remote branch, or ignored/local-only guard target exists.
- `in-progress`: a matching signal has dirty files, ahead commits, an open MR, an active OpenSpec change, or an active claim.

## GitLab behavior

Open MR inspection is opt-in. When requested, the checker parses the `gitlab` remote URL and uses `GITLAB_TOKEN`, `GL_TOKEN`, or `GITLAB_PRIVATE_TOKEN`. If unavailable, it emits a warning by default or an error when `--require-gitlab-mrs` is set.

## Non-goals

- Do not mutate worktrees, branches, claims, or OpenSpec artifacts.
- Do not make the default guard require network access.
- Do not implement ML/LLM semantic matching.
