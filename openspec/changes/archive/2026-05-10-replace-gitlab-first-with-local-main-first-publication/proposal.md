## Why

The user explicitly rejected the previous GitLab-first publication rule and wants this repository to support local-first integration where validated work may enter local `main` before GitLab catches up. The current governance still describes GitLab as the authoritative merge gate, which blocks the requested local-main-first workflow and creates contradictory startup guidance.

## What Changes

- Replace GitLab-first wording with a local-main-first publication model.
- Make local `main` the primary integration surface after local CI, local MR review, clean worktree state, and explicit user approval.
- Permit local `main` to intentionally lead `gitlab/main` and `github/main`, while requiring that remote lag is visible and later cleared through remote publication/sync.
- Keep feature work isolated in feature branches/worktrees; do not turn the primary `main` worktree into a feature workspace.
- Keep GitLab/GitHub as remote publication, clean-environment confirmation, backup, and audit/mirror surfaces rather than default gates before local `main` integration.
- Preserve remote-freshness checks before starting from a stale upstream baseline: if `gitlab/main` has newer work, local `main` must be fast-forwarded or the stale-base risk must be explicitly accepted before new work or publication judgment.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-repository-multi-session-worktree-isolation`: replaces GitLab-first publication requirements with local-main-first integration and explicit remote-lag handling.
- `codex-user-level-skills-governance-lifecycle`: updates publication lifecycle requirements from GitLab-first to local-main-first.
- `codex-repository-main-worktree-alignment-safety`: updates local-only recovery wording from GitLab-first branches to local-main-first feature branches.
- `codex-product-lifecycle-document-governance`: updates delivery-gate terminology from GitLab-first to local-main-first.
- `codex-user-level-mainline-memory-handoff`: updates memory handoff publication-ref language to local-main-first plus remote mirror state.

## Impact

- impact_scope: `AGENTS.md`, `README.md`, startup summaries, active governance docs, active implementation-plan references, product lifecycle docs, active OpenSpec specs, `tools/check_worktree_session_hygiene.py`, and related tests.
- explicit_non_goals: no remote deletion, no GitLab/GitHub disablement, no removal of remote CI, no GitHub PR default, no user-level launcher install, and no durable-state mutation.
- rollout_sequence: create OpenSpec artifacts, update active docs and checker wording, validate the active change, archive it into stable specs, re-run validation, then commit locally. Remote publication remains a later user decision.
- rollback_plan: revert this change commit to restore the previous GitLab-first policy text and stable specs.
- validation_path: run `openspec validate replace-gitlab-first-with-local-main-first-publication --strict`, `openspec validate --all`, archive the change, re-run `openspec validate --all`, run `D:\PythonProject_langgraph\.venv\Scripts\python.exe tools\run_openspec_guard.py --root . --json`, run relevant unit tests, and run `git diff --check`.
- mainline_classification: existing repository governance mainline; this is a policy correction under the current Codex user-level orchestration repository, not a new product mainline.
