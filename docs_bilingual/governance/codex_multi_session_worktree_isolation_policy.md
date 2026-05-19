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

The primary main worktree freshness rule is mandatory: `D:\PythonProject_langgraph` is the primary main worktree, must stay checked out on local `main`, and its HEAD must not lag behind the local `main` branch reference. In normal operation, its HEAD should exactly equal local `main`. Local `main` must not lag behind the latest fetched `gitlab/main` before new writable work, release-timing judgment, remote push, MR creation or update, or mainline-state claims unless the user explicitly accepts stale-base risk. Local `main` may intentionally lead `gitlab/main` and `github/main` after approved local integration; report that remote lag until publication or mirror sync catches up. If the primary directory is dirty or not on `main`, stop writable work and resolve the hygiene issue first. `D:\PythonProject_langgraph` is the primary directory for coordination and local mainline integration, not a feature-task workspace.

## 2. Authority Boundary

This policy is repository governance. It applies to all Codex sessions that edit this repository, including normal Codex, oh-my-codex wrapped sessions, native subagents, durable-team workers, and future LangGraph-driven execution contexts.

It authorizes only checker-backed cleanup of already-integrated local feature worktrees and local feature branches when the cleanup helper proves that the worktree is clean, the branch is contained in local `main`, a completed local claim is preserved, and a local rollback backup ref exists. It does not authorize reset, force deletion, remote ref deletion, backup-ref deletion, or discarding local edits; those destructive actions still need an explicit preservation-first plan and operator confirmation.

## 3. Required Worktree Model

- `main` - local branch used as the primary local integration surface after approved local validation; do not use it as a writable task branch.
- `gitlab/main` - remote-tracking branch used as the upstream freshness baseline and GitLab publication target.
- `github/main` - GitHub mirror/sync target for the intended local `main` commit.
- `.worktrees/` - local container for secondary Git worktrees; it is local Git workspace infrastructure, not a documentation or source directory.
- `backup/*` - preservation branch namespace for local dirty-worktree snapshots before risky alignment operations.

Every writable task must use:

1. A dedicated feature branch whose name describes the task.
2. A dedicated worktree under `.worktrees/`.
3. A local-main-first integration decision before the result enters local `main`, followed by remote publication/sync when the user approves it.

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
- After local integration, confirm the primary directory `D:\PythonProject_langgraph` is on local `main` at the intended commit. If remote publication is used later, reconcile GitLab/GitHub to that intended local `main` commit.

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


## 5.1 Feature Worktree Release And Branch Cleanup

A feature worktree is a temporary execution surface. After local validation passes, all intended tracked changes are committed, `git status` is clean, no unhandled `.local/`, untracked, evidence, cache, OCR-output, private, copyrighted, or large files remain, local `main` contains the branch result, a rollback backup ref exists, and the completed claim has been preserved into the primary directory, the local feature worktree may be released before GitLab publication finishes. Releasing the worktree means removing the local filesystem worktree with Git worktree commands.

A local feature branch is also temporary after local `main` contains the intended result and a rollback backup ref exists. The local branch may be deleted with `git branch -d` after `tools/cleanup_integrated_worktree.py` passes and preserves the completed claim. Remote publication branches, remote refs, and backup refs remain protected: they must not be deleted by local cleanup, and remote publication still requires explicit user approval.

File-class tasks must be handled before worktree release:

- Tracked files: commit them before releasing the worktree.
- Untracked files that belong in the repository: add and commit them before releasing the worktree.
- `.local/`, extraction evidence, caches, OCR output, and other local generated files: do not commit them by default; move them to an explicit local evidence location or generate a tracked run summary when they are still needed.
- Private, copyrighted, or large files: do not commit the raw payload; commit only a manifest, summary, path, hash, quality metric, or provenance record when repository evidence is needed.
- Unclear files: do not delete them with the worktree; ask the operator to choose keep, commit, move, summarize, or discard.

The safe summary is: after local `main` integration, a clean `.worktrees/` feature worktree and its merged local feature branch can be cleaned automatically by the guarded cleanup helper; remote refs and backup refs are not cleaned automatically.

## 5.2 Worktree Task Receipts and Lifecycle States

Every newly created feature worktree must carry durable task metadata before writable work begins. The metadata has two local-only surfaces:

1. `.omx/session-claims/<session>.json` declares session ownership for conflict checks.
2. `.omx/worktree-task-receipt.json` is a short receipt inside the worktree so any resumed session can immediately see why the worktree exists.

Both surfaces must record at least: task name, task summary, worktree path, branch, creating or taking-over session, creation time, whether the work is document-plan-only, whether later code implementation is required, touched paths, next action, whether local `main` integration is required, whether remote sync is required, and the expected merge-or-pause point.

Allowed lifecycle labels are: `active`, `paused`, `ready-to-merge`, `merged-local-main`, `cleaned`, `remote-sync-needed`, `completed`, and `superseded`. A worktree that cannot be merged immediately must be left with one of these explicit lifecycle labels and a concrete next action. Document-plan-only worktrees should not be kept long term: write the plan, run local validation, merge to local `main`, create a rollback ref, preserve a completed receipt, and clean the worktree plus local feature branch.

After each local `main` merge or remote publication/sync, the operator workflow must scan `git worktree list --porcelain`, active session claims, and residual worktree classifications. Future "what next" reports must list residual worktrees separately from the main task instead of letting them disappear inside a broad backlog. Completed receipts must preserve rollback ref, merged local-main commit, cleaned worktree path, deleted branch, and remote-sync status.

The checker `tools/check_worktree_task_receipt.py` is the script-backed control for this lifecycle. In normal guard mode it reports missing receipts as warnings for legacy worktrees, while new worktrees created by the current workflow must write the receipt immediately. In strict mode (`--require-all-feature-worktrees`) it can be used to migrate or audit all residual worktrees.

## 6. Script Control

Prompt reminders are not sufficient for this safety boundary.

The repository provides:

- `tools/check_worktree_session_hygiene.py` - read-only checker that inspects registered Git worktrees, dirty states, duplicate dirty paths, branch cleanup readiness, rollback backup ref presence, and `main` alignment risk.
- `tools/cleanup_integrated_worktree.py` - guarded local-only cleanup helper that removes a clean, already-integrated `.worktrees/` feature worktree and deletes its merged local feature branch with `git branch -d` only after preserving the completed claim and confirming a rollback backup ref.
- `tools/check_session_ownership_claims.py` - read-only checker that inspects local `.omx/session-claims/*.json` claim files and fails on duplicate OpenSpec-change or overlapping path ownership.
- `tools/check_worktree_task_receipt.py` - read-only checker for feature worktree task receipts, lifecycle labels, branch-matching claims, document-plan-only cleanup intent, and completed receipt fields.

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

The hygiene checker also reports `worktree_release_candidates` in JSON output. `worktree_release_candidates` is a read-only status list that separates `worktree_release_ready`, which means the feature worktree is clean enough to remove after local validation and file classification, from `branch_cleanup_ready`, which means the feature branch is merged into local `main` and a rollback backup ref exists. Remote GitLab/GitHub alignment is reported separately as publication state; it is no longer a blocker for local-only branch cleanup.

The checker now has two read-only modes:

- Default claim mode verifies explicit `.omx/session-claims/*.json` collisions. `.omx/session-claims/*.json` means local ignored JSON claim files that declare which session owns an OpenSpec change or path scope.
- Task precheck mode scans worktrees, branches, remote-tracking branches, active OpenSpec changes, active claim files, target paths, and ignored or local-only guard-scanned files before a new write scope is created. Task precheck mode is the checker-backed form of the manual precheck rule above.

Recommended task precheck command before creating a new task worktree or fixing a guard failure:

```powershell
python .\tools\check_session_ownership_claims.py --root . --precheck-task "<task-slug-or-description>" --target-path "<repo-relative-path>" --openspec-change "<change-id>" --json
```

The command above runs the checker in task precheck mode. `--precheck-task` names the intended task, `--target-path` names a repository-relative hotspot path, `--openspec-change` names the OpenSpec change id being considered, and `--json` emits machine-readable output for cold-start review. Use `--check-gitlab-mrs` to include open GitLab MR inspection when a token is available; use `--require-gitlab-mrs` only when the workflow must fail closed if GitLab MRs cannot be inspected.

## 7. Local-First Mirrored CI/MR Integration

All repository changes use local-main-first integration plus mirrored local/remote CI evidence. GitLab is a remote publication, clean-environment confirmation, backup, and audit surface after local gates have already run; it is not the default authority gate before local `main` integration. This is not a requirement to push every local checkpoint commit to the remote server.

Runner-budget and publication-package rules:

- Use local-first batching to conserve GitLab runner minutes. GitLab runner minutes are the finite remote CI quota consumed by GitLab pipelines.
- Local CI is the primary check logic. Run `tools/ci/local_gate.ps1` before local `main` integration or remote publication; `tools/ci/local_gate.ps1` is the shared repository CI gate that runs OpenSpec guard checks, repository checker or guard scripts, optional local tests, and whitespace diff checks.
- CI-managed tests must be registered in `tools/ci/ci_test_manifest.json`; `tools/ci/ci_test_manifest.json` is the stable test manifest that prevents local or remote CI from accidentally running historical, environment-specific, or experimental tests that are not part of the publication gate.
- Local MR review is the local pre-integration review surface. Run `tools/ci/local_mr_review.ps1` after all intended changes are committed and the feature worktree is clean, before local `main` integration or remote publication; `tools/ci/local_mr_review.ps1` summarizes the feature branch diff, commit log, diff stat, and merge simulation against the selected base branch, and fails closed when `git status --porcelain` reports dirty worktree entries.
- Remote CI must mirror the local CI gate. GitLab CI and GitHub mirror workflows may install required tools and invoke `tools/ci/local_gate.ps1`, but must not carry a separate checker sequence that can drift from local CI.
- Remote MR review and remote CI remain as clean-environment confirmation, permission, backup, mirror-state, and audit-record layers.
- If local gate results and remote CI results disagree, fix the shared script, environment setup, or CI configuration drift. Do not bypass either evidence layer.
- Keep local `main` from starting from a stale upstream baseline. Before new writable work, release-timing judgment, remote push, MR creation/update, or mainline-state claims, refresh `gitlab/main`; if local `main` is behind, fast-forward it before continuing unless the user explicitly accepts stale-base risk. If a feature branch was prepared on a stale base, rebase or merge it onto the refreshed base before local integration or publication unless the user explicitly accepts the stale-base risk.
- Allow intentional remote lag after approved local integration. Local `main` may lead `gitlab/main` and `github/main`; sessions must report that state clearly until remote publication or mirror sync catches up.
- Treat local integration approval and remote publication approval as separate release decisions. After local `main` integration, the session must stop at the remote-publication approval gate and must not push GitLab, create/update/merge GitLab MRs, sync GitHub, delete remote publication branches, or mutate remote refs unless the current user message or an approved release record explicitly authorizes that remote publication action. Generic continuation such as `continue`, `go on`, `proceed`, or a localized equivalent is not remote publication approval unless it names the remote action.
- A current user message saying `push remote` Chinese wording, `publish remote`, `push remote`, `remote publication`, `use GitLab MR then sync GitHub` Chinese wording, or equivalent explicit remote-publication wording is a single approval for the normal green-path remote publication flow: push or update the GitLab publication branch, create or update the GitLab MR, wait for GitLab CI, merge the MR after CI is green, fetch and confirm GitLab `main`, sync the same intended commit to GitHub `main`, and run post-publication state checks. Do not ask for separate approvals inside that green path.
- Prefer sandbox-approved commands and existing approved command prefixes during the approved remote publication flow. If the Codex sandbox still requires escalation for GitLab push/MR/CI/merge or GitHub sync commands that are inside the already approved flow, request one scoped escalation for the whole `push GitLab / open MR / merge MR / sync GitHub` flow instead of asking once per command. Stop for a new approval if the flow needs force push, protected-branch setting changes, remote ref deletion, history rewrite, scope expansion, or credential/security changes.
- Keep the primary main worktree from falling behind local `main`. `D:\PythonProject_langgraph` is the primary directory; it must be on local `main`, its HEAD must not lag behind the local `main` branch reference, and in normal operation its HEAD should exactly match local `main`. `tools/check_worktree_session_hygiene.py` must fail if the primary directory is dirty, not on `main`, behind local `main`, or if local `main` is behind `gitlab/main` without explicit stale-base acceptance.
- Before every local repository commit, run `tools/check_precommit_update_archive.py --root . --json` or rely on the installed `.githooks/pre-commit` hook that invokes `tools/run_openspec_guard.py`. This pre-commit review must inspect whether existing governance, CI manifest, checker registration, or OpenSpec lifecycle files require updates or archive movement. Required updates and completed OpenSpec archives must be resolved before `git commit`; a two-step exception must record both `x_archive_deferred_reason` and `x_archive_follow_up`.
- Do local commits, local checker runs, local MR review, local rework, and local cleanup before local `main` integration or the first remote push.
- For a locally completed OpenSpec change that is ready for integration, prefer a single integration package. A single integration package means the same feature branch contains the implementation or documentation change, the archived OpenSpec change under `openspec/changes/archive/`, and the promoted stable spec under `openspec/specs/`.
- Use the single integration package for small governance, documentation, checker, and test changes when local validation already proves completion and the review scope shares one rollback boundary.
- Use a two-step flow only when the implementation is large or risky, remote CI or MR review should confirm the implementation before archive, archive promotion would create heavy stable-spec conflicts, or the user explicitly requests an implementation-only publication. A two-step flow must record the archive follow-up instead of treating the completed active change as closed.
- Batch related small changes into one package only when they share the same topic, validation surface, and rollback boundary. A rollback boundary is the smallest unit that can be reverted safely without mixing unrelated work.
- Do not combine unrelated topics just to reduce runner usage; reviewability and rollback safety still take priority.
- Before local integration or remote publication, the active session's model must judge release timing from local validation state, active-change state, archive-package state, review scope, rollback boundary, and runner-budget value, then recommend integrate/publish or wait to the user. The user remains the release decision authority.
- Push to GitLab only when local CI and local MR review pass, unless the user explicitly asks for an early remote pipeline check.

Default local-main-first sequence:

1. Refresh `gitlab/main`, fast-forward local `main` if it is behind unless stale-base risk is explicitly accepted, and confirm the primary directory `D:\PythonProject_langgraph` is clean, on local `main`, and not behind local `main`.
2. Create a feature branch from the latest acceptable local `main` baseline.
3. Use a dedicated `.worktrees/<task>` worktree for that branch.
4. Implement the OpenSpec change and run the local implementation validation while the change is still active.
5. If the completed change fits the single-package path, archive it on the same feature branch, promote reusable delta specs into stable specs, and re-run the local validation commands.
6. Before each local commit, run the pre-commit update/archive checker and resolve any required existing-file update, CI manifest registration, checker registration, or completed-change archive; then commit all intended tracked changes and classify every untracked, ignored, local evidence, cache, OCR-output, private, copyrighted, or large-file artifact before integration review.
7. Run `tools/ci/local_gate.ps1` from the clean feature worktree. This script is the local CI gate and the remote CI mirror entrypoint.
8. Run `tools/ci/local_mr_review.ps1` against the selected base branch to inspect what local integration and any later remote MR will show; the script must fail if the feature worktree is dirty.
9. If the completed change needs the two-step path, state the exception reason, keep the active change or follow-up archive task visible, and ask the user before implementation-only publication.
10. Have the active session's model recommend integrate/publish or wait, including the single-package or two-step archive decision and the local gate results, then ask the user to confirm the release decision.
11. After user approval, integrate the validated feature branch into local `main` first, preferably by fast-forward when the branch is linear from local `main`.
12. Verify the primary directory `D:\PythonProject_langgraph` is on local `main`, clean, and at the intended local `main` commit.
13. Create or verify the local rollback backup ref for the pre-merge local `main` state, then use `tools/cleanup_integrated_worktree.py --execute` to preserve the completed claim, remove the clean integrated feature worktree, and delete the merged local feature branch with `git branch -d`.
14. If local `main` now leads `gitlab/main` or `github/main`, report intentional remote lag. Recreate a publication branch from local `main` later only when explicit remote publication approval is given.
15. Ask for explicit remote-publication approval when local `main` leads GitLab or GitHub; do not treat generic continuation as approval. A current user message such as `push remote` Chinese wording, `publish remote`, `push remote`, `remote publication`, or `use GitLab MR then sync GitHub` Chinese wording authorizes the whole normal green path once: push or update the GitLab publication branch, create or update the GitLab MR, wait for GitLab CI, merge the MR after CI is green, fetch and confirm GitLab `main`, sync the exact intended local `main` commit to GitHub `main`, and run post-publication checks.
16. Prefer sandbox-approved commands and existing approved command prefixes during that approved green path. If the Codex sandbox still requires escalation for GitLab push/MR/CI/merge or GitHub sync inside the flow, request one scoped escalation for the complete `push GitLab / open MR / merge MR / sync GitHub` flow instead of one escalation per command.
17. Reconcile any remote CI discrepancy by fixing the local/shared gate or environment drift, not by bypassing evidence. Stop for a new approval before force push, protected-branch setting changes, remote ref deletion, history rewrite, scope expansion, or credential/security changes.
18. Keep remote publication branches, remote refs, and backup refs protected until a separate explicit cleanup approval is given.

GitHub PRs are not the default workflow for this repository.

## 8. OpenSpec Lifecycle

Changes that create or alter this policy are structural repository-governance changes and must follow the repository OpenSpec lifecycle.

Required lifecycle:

1. Create or update an OpenSpec change before implementation.
2. Keep the governance policy, checker behavior, and guard integration aligned with that change.
3. Run the repository validation commands after implementation while the change is still active.
4. For completed local changes that are ready for integration or publication, archive the OpenSpec change on the same feature branch by default so its delta spec becomes a stable spec before local `main` integration.
5. Re-run the repository validation commands after archive promotion.
6. Integrate the implementation, archive movement, and stable spec through one local-main-first package unless a two-step exception is explicitly chosen.

Archive isolation rule:

- For changes that affect code, executable checks, CI, stable specs, startup instructions, repository instruction surfaces, or structural governance rules, perform the archive in the same isolated feature worktree when the single-MR path applies. If a separate archive worktree is safer, it must still be integrated back into the same publication branch before the MR is opened.
- The archive worktree or feature worktree must pass the relevant validation commands before the archive result is committed. After the archive result is integrated into the publication branch, that branch must pass validation again.
- Purely explanatory text edits may use a lighter archive flow when they do not change enforceable repository behavior, but unclear cases should use the archive-before-publication package flow.
- Do not leave a completed worktree-isolation OpenSpec change active after the implementation has already merged to `main`. A completed active change is a lifecycle gap, even when its tasks are all checked.
- If a two-MR exception is used, the implementation MR must say why archive is deferred and must leave a visible follow-up archive path; it must not claim the OpenSpec lifecycle is closed.
