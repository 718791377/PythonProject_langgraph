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

The primary main worktree freshness rule is mandatory: `D:\PythonProject_langgraph` is the primary main worktree, must stay checked out on local `main`, and its HEAD must not lag behind the local `main` branch reference. In normal operation, its HEAD should exactly equal local `main`. Local `main` must not lag behind the latest fetched `gitlab/main` before new writable work, release-timing judgment, push, MR creation or update, or mainline-state claims. If local `main` is behind `gitlab/main`, fast-forward local `main` before continuing. If the primary directory is dirty or not on `main`, stop writable work and resolve the hygiene issue first. `D:\PythonProject_langgraph` is the primary directory for coordination and local mainline mirroring, not a feature-task workspace.

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
- Keep the primary directory `D:\PythonProject_langgraph` checked out on local `main`; its HEAD must not lag behind local `main`, and normally should equal local `main`. Use `.worktrees/` for writable feature branches instead of leaving the primary directory on an old branch.
- Do not manually delete `.worktrees/`; use Git worktree commands after preservation checks.
- Do not assume a dirty file belongs to the current session.
- Do not reset, checkout, clean, move, or delete unknown dirty files until their owning session or backup branch is identified.

- Treat legacy resumed sessions as compatibility-scoped sessions. A legacy resumed session is an older Codex `/resume` thread that may keep stale context, stale MCP assumptions, or stale launcher behavior.
- Do not let a legacy resumed session claim new governance implementation, dirty-file ownership, or release authority unless the current session explicitly revalidates the repository startup summary, OpenSpec state, Git state, and session-ownership claims.
- If an old resumed session disagrees with current repository files, current repository files and current local Git state win until an operator-approved reconciliation plan says otherwise.
- Before a writable session dirties a feature worktree, create an active `.omx/session-claims/<session>.json` claim file. `.omx/session-claims/` is the ignored local coordination directory for declaring the OpenSpec change or path scope owned by the current session.
- Before creating a new task worktree, editing files, fixing guard failures, or taking over OpenSpec or governance artifacts, run a task ownership precheck. A task ownership precheck is a read-only scan for semantic ownership signals before any new write scope is created.
- The task ownership precheck must inspect registered Git worktrees, local branches, remote-tracking branches, open GitLab MRs, active OpenSpec changes, local `.omx/session-claims/*.json` claim files, and target paths including ignored files.
- A semantic match in a worktree name, branch name, MR title, MR source branch, OpenSpec change id, claim path, or target file path is an ownership signal even when the matched worktree is clean and has no commits beyond `main`.
- If a matching ownership signal exists, treat the task as claimed until the leader explicitly serializes a handoff, continues the existing worktree, or classifies the signal as completed stale residue.
- Ignored or local-only files inside guard-scanned directories are still task objects when they affect repository checks. Classify their intended ownership before fixing, moving, excluding, or deleting them.
- Do not let two live sessions claim the same OpenSpec change or overlapping hotspot path scope unless the current leader explicitly serializes the handoff.
- After a GitLab MR merges, fast-forward local `main` to the exact GitLab main commit, confirm the primary directory `D:\PythonProject_langgraph` is on local `main` at that commit, then sync that exact commit to GitHub.

## 5. Dirty File Classification

Dirty files must be classified before action:

- current-task edits - files intentionally changed by the current session.
- other-session edits - files likely owned by another live or recently interrupted session.
- generated artifacts - files produced by checks, refreshes, or reports.
- scratch notes - local notes that are not yet approved formal documentation.
- stale residue - abandoned worktree or generated output that needs a preservation-first cleanup plan.

If ownership is unknown, keep the file and report it. Do not delete it as a shortcut.

Task ownership states must be classified before takeover:

- unclaimed - no semantic match exists in worktrees, branches, MRs, OpenSpec changes, claim files, or target paths.
- claimed-not-started - a matching worktree, branch, MR, OpenSpec change, claim file, or ignored target path exists, but there is no dirty diff, extra commit, or open MR progress yet.
- in-progress - a matching worktree has dirty files, ahead commits, an open MR, an active OpenSpec change, or an active claim with overlapping paths.
- completed-stale - a matching branch or claim belongs to work already merged or archived; the leader may reuse it only after explicitly treating the handoff as serialized and preservation-safe.

## 6. Script Control

Prompt reminders are not sufficient for this safety boundary.

The repository provides:

- `tools/check_worktree_session_hygiene.py` - read-only checker that inspects registered Git worktrees, dirty states, duplicate dirty paths, and `main` alignment risk.
- `tools/check_session_ownership_claims.py` - read-only checker that inspects local `.omx/session-claims/*.json` claim files and fails on duplicate OpenSpec-change or overlapping path ownership.

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

Before a feature worktree becomes dirty, create a local claim such as:

```json
{
  "schema_version": 1,
  "session_id": "session-ownership-claims",
  "status": "active",
  "branch": "feature/session-ownership-claims",
  "worktree": "D:\\PythonProject_langgraph\\.worktrees\\session-ownership-claims",
  "task_type": "implementation",
  "openspec_changes": ["formalize-session-ownership-claims"],
  "paths": [
    "tools/check_session_ownership_claims.py",
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md",
    "openspec/changes/formalize-session-ownership-claims"
  ]
}
```

`session_id` is the local operator-readable owner name, `openspec_changes` lists the OpenSpec changes owned by the session, and `paths` lists repository-relative hotspot scopes owned by the session.

Then run:

```powershell
python .\tools\check_session_ownership_claims.py --root . --allow-current-dirty --json
```

The command above runs the read-only claim checker and emits a JSON report showing active local claims and collisions.

The checker now has two read-only modes:

- Default claim mode verifies explicit `.omx/session-claims/*.json` collisions. `.omx/session-claims/*.json` means local ignored JSON claim files that declare which session owns an OpenSpec change or path scope.
- Task precheck mode scans worktrees, branches, remote-tracking branches, active OpenSpec changes, active claim files, target paths, and ignored or local-only guard-scanned files before a new write scope is created. Task precheck mode is the checker-backed form of the manual precheck rule above.

Recommended task precheck command before creating a new task worktree or fixing a guard failure:

```powershell
python .\tools\check_session_ownership_claims.py --root . --precheck-task "<task-slug-or-description>" --target-path "<repo-relative-path>" --openspec-change "<change-id>" --json
```

The command above runs the checker in task precheck mode. `--precheck-task` names the intended task, `--target-path` names a repository-relative hotspot path, `--openspec-change` names the OpenSpec change id being considered, and `--json` emits machine-readable output for cold-start review. Use `--check-gitlab-mrs` to include open GitLab MR inspection when a token is available; use `--require-gitlab-mrs` only when the workflow must fail closed if GitLab MRs cannot be inspected.

## 7. GitLab-First Integration

All repository changes still follow the GitLab-first publication workflow. GitLab-first is the final review and merge authority; it is not a requirement to push every local checkpoint commit to the remote server.

Runner-budget and publication-package rules:

- Use local-first batching to conserve GitLab runner minutes. GitLab runner minutes are the finite remote CI quota consumed by GitLab pipelines.
- Keep local `main` from falling behind the authoritative remote. Before new writable work, release-timing judgment, push, MR creation/update, or mainline-state claims, refresh `gitlab/main`; if local `main` is behind, fast-forward it before continuing. If a feature branch was prepared on a stale base, rebase or merge it onto the refreshed base before publication unless the user explicitly accepts the stale-base risk.
- Keep the primary main worktree from falling behind local `main`. `D:\PythonProject_langgraph` is the primary directory; it must be on local `main`, its HEAD must not lag behind the local `main` branch reference, and in normal operation its HEAD should exactly match local `main`. `tools/check_worktree_session_hygiene.py` must fail if the primary directory is dirty, not on `main`, behind local `main`, or if local `main` is behind `gitlab/main`.
- Do local commits, local checker runs, local rework, and local cleanup before the first push.
- For a locally completed OpenSpec change that is ready for publication, prefer a single-MR archive package. A single-MR archive package means the same feature branch contains the implementation or documentation change, the archived OpenSpec change under `openspec/changes/archive/`, and the promoted stable spec under `openspec/specs/`.
- Use the single-MR archive package for small governance, documentation, checker, and test changes when local validation already proves completion and the review scope shares one rollback boundary.
- Use a two-MR flow only when the implementation is large or risky, remote CI or MR review should confirm the implementation before archive, archive promotion would create heavy stable-spec conflicts, or the user explicitly requests an implementation-only MR. A two-MR flow must record the archive follow-up instead of treating the completed active change as closed.
- Batch related small changes into one MR only when they share the same topic, validation surface, and rollback boundary. A rollback boundary is the smallest unit that can be reverted safely without mixing unrelated work.
- Do not combine unrelated topics just to reduce runner usage; reviewability and rollback safety still take priority.
- Before remote publication, the active session's model must judge release timing from local validation state, active-change state, archive-package state, review scope, rollback boundary, and runner-budget value, then recommend publish or wait to the user. The user remains the release decision authority.
- Push to GitLab only when local validation passes, unless the user explicitly asks for an early remote pipeline check.

Default local-first sequence:

1. Refresh `gitlab/main`, fast-forward local `main` if it is behind, and confirm the primary directory `D:\PythonProject_langgraph` is clean, on local `main`, and not behind local `main`.
2. Create a feature branch from the latest local `main` after it has been checked against `gitlab/main`.
3. Use a dedicated `.worktrees/<task>` worktree for that branch.
4. Implement the OpenSpec change and run the local implementation validation while the change is still active.
5. If the completed change fits the single-MR path, archive it on the same feature branch, promote reusable delta specs into stable specs, and re-run the local validation commands.
6. If the completed change needs the two-MR path, state the exception reason, keep the active change or follow-up archive task visible, and ask the user before publishing an implementation-only MR.
7. Refresh `gitlab/main` again and confirm the feature branch is not based on stale remote state.
8. Have the active session's model recommend publish or wait, including the single-MR or two-MR archive decision, then ask the user to confirm the release decision.
9. Push to GitLab and open or update a GitLab MR.
10. Wait for the GitLab pipeline to pass.
11. Merge into GitLab `main`.
12. Sync the exact GitLab main commit to GitHub.
13. Fast-forward the local `main` branch reference to GitLab `main`.
14. Check out local `main` in `D:\PythonProject_langgraph`, verify it is clean, and verify its HEAD is not behind the local `main` branch reference; normal state is exact equality.

GitHub PRs are not the default workflow for this repository.

## 8. OpenSpec Lifecycle

Changes that create or alter this policy are structural repository-governance changes and must follow the repository OpenSpec lifecycle.

Required lifecycle:

1. Create or update an OpenSpec change before implementation.
2. Keep the governance policy, checker behavior, and guard integration aligned with that change.
3. Run the repository validation commands after implementation while the change is still active.
4. For completed local changes that are ready for publication, archive the OpenSpec change on the same feature branch by default so its delta spec becomes a stable spec before the GitLab MR is opened.
5. Re-run the repository validation commands after archive promotion.
6. Publish the implementation, archive movement, and stable spec through one GitLab-first MR unless a two-MR exception is explicitly chosen.

Archive isolation rule:

- For changes that affect code, executable checks, CI, stable specs, startup instructions, repository instruction surfaces, or structural governance rules, perform the archive in the same isolated feature worktree when the single-MR path applies. If a separate archive worktree is safer, it must still be integrated back into the same publication branch before the MR is opened.
- The archive worktree or feature worktree must pass the relevant validation commands before the archive result is committed. After the archive result is integrated into the publication branch, that branch must pass validation again.
- Purely explanatory text edits may use a lighter archive flow when they do not change enforceable repository behavior, but unclear cases should use the archive-before-publication package flow.
- Do not leave a completed worktree-isolation OpenSpec change active after the implementation has already merged to `main`. A completed active change is a lifecycle gap, even when its tasks are all checked.
- If a two-MR exception is used, the implementation MR must say why archive is deferred and must leave a visible follow-up archive path; it must not claim the OpenSpec lifecycle is closed.
