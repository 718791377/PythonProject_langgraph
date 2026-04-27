## Context

The repository has a GitLab-first publication workflow and a growing set of secondary Git worktrees under `.worktrees/`. Those worktrees are useful only if sessions treat each worktree as a single-owner write scope.

Prompt reminders alone cannot guarantee this. A cold-start model must have a script that can inspect the current repository state and fail closed for dangerous conditions such as dirty `main`.

## Design

### Governance document

`docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` is the English ASCII governance source. Its Chinese companion provides the same operator-facing rule in `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md`.

The policy states that every writable task uses one feature branch and one dedicated Git worktree, while local `main` remains a mirror of reviewed `gitlab/main`.

### Checker

`tools/check_worktree_session_hygiene.py` is read-only. It uses Git commands to inspect registered worktrees and emits JSON for CI or cold-start sessions.

The checker reports:

- dirty `main` as an error
- a dirty current non-main worktree as an error unless `--allow-current-dirty` is present
- non-current dirty worktrees as warnings
- duplicate dirty paths across worktrees as errors
- local `main` versus `gitlab/main` mismatch as a warning

### Guard integration

`tools/run_openspec_guard.py` runs the checker with `--allow-current-dirty` so normal local validation can run before a feature-branch commit while still catching dirty `main` and cross-worktree collision risks.

### OpenSpec lifecycle

After the governance files, checker, tests, and guard integration have merged, this change must be archived. Archiving is part of the implementation because it creates the stable `codex-repository-multi-session-worktree-isolation` spec that future sessions can validate against.

The archive step does not mutate local worktrees or discard dirty files. It only moves the completed OpenSpec change to archive history and syncs the delta requirements into `openspec/specs/`.

### Non-destructive behavior

No checker path deletes files, resets branches, or writes state. The checker only reports and exits non-zero for unsafe states.
