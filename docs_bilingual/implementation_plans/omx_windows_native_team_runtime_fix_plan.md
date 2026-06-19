---
doc_id: omx_windows_native_team_runtime_fix_plan
doc_class: implementation_plan
status: active
change: fix-omx-windows-native-team-runtime-20260618
base_ref: 2d53bd73c8a8b9202d6643fe26985960c7a740a0
---

# OMX Windows Native Team Runtime Fix Plan

> For agentic workers: use subagent-driven-development or executing-plans to implement this plan task-by-task. Stage A and Stage B are separate local-main integration packages. Do not use the currently broken tmux-pane path as proof of durable-team runtime success.

**Goal:** make user-level OMX usable for all local projects on native Windows when `tmux` is absent and the shell is not inside a `tmux` session, without redefining `native_omx` as `tmux`.

**Architecture:** Stage A freezes the contract and corrects false completion claims. Stage B uses TDD to separate readiness from operational launchability, add Windows runtime-backend preflight, implement or fail closed around a native prompt/process controller, and prove cross-project operation from installed user-level assets.

**Tech Stack:** PowerShell installer and generated wrappers, repo-local `.omx/state/...` selectors, Node patch helpers where needed, OpenSpec artifacts, PowerShell and Node tests, local-main-first Git workflow.

## Vocabulary

- `native_omx`: worker-centric durable backend family.
- `unix_tmux`: Unix/tmux runtime backend inside the `native_omx` family.
- `windows_prompt_process_controller`: native Windows runtime backend inside the `native_omx` family.
- `capability switches`: `subagent_routing`, `oh_my_codex`, and `langgraph` enable layers.
- `backend family`: durable family such as `native_omx` or `langgraph`.
- `effective lane`: task-flow choice based on current work shape.
- `operational ability`: whether the current lane can actually launch, reuse, status, await, resume, and shutdown now.

## Stage A: Freeze Plan Package

Files:

- Create `openspec/changes/fix-omx-windows-native-team-runtime-20260618/` with proposal, design, tasks, management, and delta spec files.
- Create this implementation plan and the `.zh-CN.md` companion.
- Update `docs_bilingual/docs_registry.yaml`.
- Correct `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` and `.zh-CN.md` so P6 is not falsely claimed complete.

Steps:

1. Freeze the four-layer model:
   - capability switches;
   - backend family;
   - task-flow effective lane;
   - operational ability.
2. Freeze runtime-backend vocabulary:
   - `windows_prompt_process_controller`;
   - `unix_tmux`;
   - `unknown` - fallback marker used when no concrete runtime backend is proven.
3. Freeze blocker vocabulary:
   - `blocked:windows_backend_not_implemented` - Windows controller backend is not implemented yet.
   - `blocked:backend_not_ready` - selected durable backend is not ready for the requested operation.
   - `blocked:tmux_only_backend` - only a Unix/tmux runtime backend is available.
   - `blocked:not_in_tmux_session` - a tmux-specific operation is running outside a tmux session.
   - `blocked:controller_launch_failed` - the Windows controller launch attempt failed.
   - `blocked:breakaway_process_unavailable` - the required Windows breakaway process path is unavailable.
   - `blocked:runtime_backend_unavailable` - no concrete runtime backend can be used now.
   - `blocked:selector_refresh_gap` - selector state must be refreshed before launch.
4. Validate Stage A:
   - `openspec validate fix-omx-windows-native-team-runtime-20260618 --strict` - validates the active OpenSpec change.
   - `python .\tools\check_document_pair_policy.py --root . --base-ref main --json` - checks bilingual Markdown pair coverage.
   - `python .\tools\check_precommit_update_archive.py --root . --json` - checks commit readiness and archive deferral.
   - `python .\tools\run_openspec_guard.py --root . --tool codex --json` - runs the repository OpenSpec guard stack.
5. Commit Stage A and integrate it into local `main` using the governance-confirmation local flow.

## Stage B: Runtime Implementation Package

Primary files:

- `tools/install-codex-user-level-team-mode.ps1` - installer and generated wrapper source.
- `test/install-codex-user-level-team-mode.test.ps1` - generated wrapper and readiness regression tests.
- a focused Stage B PowerShell test file if needed for faster RED/GREEN loops
- existing `tools/openclaw-omx-windows-*.mjs` and `test/openclaw-omx-windows-*.test.mjs` only when runtime patch replay is touched

TDD order:

1. RED: readiness false-ready.
   - A selected/tracked `native_omx` state without Windows runtime evidence must not produce `backend_ready=true`.
2. RED: Windows backend selection.
   - Windows no-tmux planning must not select a tmux-only persistent-team launch path.
3. RED: `omx-team-auto.ps1 -Apply` preflight.
   - Failed operational preflight must not create a tracked team record or active native selector.
4. RED: live runtime evidence fields.
   - Tracked records and selectors must be separated from live controller/process evidence.
5. GREEN: add runtime fields and fail-closed preflight.
6. GREEN: implement the Windows prompt/process controller backend or preserve named blockers until controller launch is possible.
7. GREEN: wire launch/reuse/switch/shutdown and cross-project cwd validation.

## Stage B Acceptance

Stage B is accepted only when fresh verification proves:

- `runtime_backend`, `preflight_passed`, `operational_ready`, and `blockers` appear in readiness and auto-helper output.
- `selected=true` and `ready=true` are not used as launch evidence.
- Windows without `tmux` and without a `tmux` session does not route into a tmux-only backend.
- `omx-team-auto.ps1 -Apply` fails closed before mutation when operational preflight fails.
- A successful Windows run, when claimed, has real lifecycle evidence for launch, status, await, resume, and shutdown.
- Installed user-level assets can be used from another repository cwd while durable state remains in that repository's `.omx/state/...`.

## Verification Plan

Focused commands:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1
node --test .\test\openclaw-omx-windows-prompt-startup-evidence-fix.test.mjs
node --test .\test\openclaw-omx-windows-prompt-controller-startup-status-fix.test.mjs
```

Repository gates:

```powershell
openspec validate fix-omx-windows-native-team-runtime-20260618 --strict
python .\tools\check_document_pair_policy.py --root . --base-ref main --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root . --tool codex --json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 1500 -Json
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Root . -BaseRef main -HeadRef HEAD -Json
```

## Collaboration Plan

- Stage A: leader writes and integrates the frozen plan. Experts are advisory because no frozen plan exists yet and the durable-team runtime is the bug target.
- Stage B: after Stage A lands on local `main`, use the smallest safe expert/durable surface. Runtime readiness and lifecycle work can be separated from tests/documentation, with leader-owned fan-in.
- If the existing persistent team launcher cannot safely start before the fix, record the named blocker and use native expert subagents plus main-session implementation instead of treating a broken team as evidence.

## Current Status

<!-- CURRENT_STATUS_START -->
- Stage A has been validated, committed, and integrated into local `main`.
- Stage B implementation is in worktree `implement-omx-windows-native-team-runtime-20260619`; focused PowerShell and Node verification has passed.
- Stage B local gate, local MR review, and local-main integration are pending.
- Remote publication is not authorized.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage A: complete - OpenSpec deltas, bilingual implementation plan, docs registry entry, and corrected P6 runtime wording were frozen and integrated.
- Stage B TDD: complete - PowerShell tests cover false-ready readiness, Windows backend selection, Apply preflight fail-closed behavior, and live runtime evidence fields.
- Stage B runtime: complete - runtime backend/preflight fields, Windows prompt/process controller behavior, lifecycle status/exit/shutdown replay patches, and cross-project cwd evidence are implemented.
- Stage B verification/integration: run repository governance checks, commit the runtime package, run local gate/local MR review, merge into local `main`, and stop at the remote-publication gate.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- `openspec/changes/fix-omx-windows-native-team-runtime-20260618/` - Stage A OpenSpec and management evidence.
- `test/install-codex-user-level-team-mode.test.ps1` - Stage B generated-wrapper and readiness regression evidence.
- `test/codex-official-update-patch-replay-template.test.ps1` - official-install replay gate, patch filtering, ordering, and fail-closed evidence.
- `test/openclaw-omx-windows-prompt-*-fix.test.mjs` - Windows prompt controller lifecycle/startup/status/shutdown replay evidence.
- `tools/ci/ci_test_manifest.json` - CI registration for the new Node and PowerShell regression surfaces.
- `.omx/state/selectors/active.json` - per-repository selector authority.
- `.omx/state/team/codex-auto-managed-team.json` - compatibility tracked native team record, not sufficient by itself as launch evidence.
<!-- EVIDENCE_INDEX_END -->
