---
doc_id: mainline_sync_langgraph_capability_gap_after_migration_aware_live_primary_engine_compatibility_state_startup_summary
lang: en
status: active
doc_class: startup_summary
---

# Mainline `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` Startup Summary

## Scope

This summary covers the current maintenance lane inside the repository mainline:

- official update compatibility for `oh-my-codex`
- local patch replay workflow standardization
- Windows-safe durable-team operator workflow continuity

Use this file when a new session needs to continue the updater / replay / gated-checkpoint work rather than the broader archived LangGraph rollout history.

## Current Handoff Snapshot

Use this snapshot before the older implementation command card when deciding what to do next.

- `automate-task-ownership-precheck-checker` - latest archived OpenSpec change in this mainline-adjacent maintenance lane; it landed checker-backed task ownership precheck behavior.
- `tools/check_session_ownership_claims.py` - session ownership checker that now supports task ownership precheck signals before repository writes.
- `openspec status` - current active-change check command; it currently reports no active changes on `main`.
- `main`, `gitlab/main`, and `github/main` - repository publication refs that currently point at the same commit `460f813` in the local clone checked during this handoff refresh.

Current interpretation:

- the decision-lock plus diff-approval replay increment is already implemented
- the task ownership precheck checker increment is also already implemented and archived
- a new session does not need to reopen either design unless new evidence appears
- the next safe actions are to choose a fresh small OpenSpec change, automate remaining replay smoke checks, or continue durable-state status hardening

## Implementation Command Card

Use this front card first when a new session needs to take over implementation quickly.

### Do now

- continue the frozen next-change increment in `tools/codex-official-update-patch-replay-template.ps1`
- implement the decision-lock plus diff-approval additions that are already frozen in the bilingual docs
- treat the current script as already usable and extend it rather than redesigning the workflow

### Edit these files

- `tools/codex-official-update-patch-replay-template.ps1` - PowerShell replay-template script being extended by this increment.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - English active implementation plan that records the user-level team-mode behavior.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md` - Chinese companion for the active user-level team-mode implementation plan.
- update the bilingual Appendix C text from “planned” to “implemented” only after the code lands

### Run these verifications

Verification card 1 — happy path

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-lock-happy'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root -ApproveDiff
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result — `precheck` succeeds, `diff -ApproveDiff` writes approval state, and `replay` is no longer blocked by the diff-approval gate
- failure triage pointer — inspect:
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when stage-gate or approval behavior fails.
- `$root\checkpoint.json` - snapshot checkpoint file that records completed stages and approvals.
- `$root\patch-decision-table.json` - JSON decision table that records patch decisions and manual overrides.

Verification card 2 — replay blocked without `precheck`

```powershell
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot 'D:\PythonProject_langgraph\.tmp\verify-missing-precheck' -WhatIf
```

- expected result — the command stops with an error saying `precheck` is required
- failure triage pointer — inspect:
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when replay incorrectly skips the precheck gate.
  - the stage-gate logic in `<snapshot-root>\checkpoint.json` if the root already exists

Verification card 3 — replay blocked without `diff`

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-missing-diff'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result — `replay` stops with an error saying `diff` is required
- failure triage pointer — inspect:
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when replay incorrectly skips the diff gate.
- `$root\checkpoint.json` - snapshot checkpoint file that should record whether the diff stage completed.

Verification card 4 — replay blocked without approved diff

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-unapproved-diff'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay -SnapshotRoot $root -WhatIf
```

- expected result — `replay` stops with an error saying `approvals.diff_review.approved = true` is required
- failure triage pointer — inspect:
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when replay incorrectly skips diff approval.
- `$root\checkpoint.json` - snapshot checkpoint file that should record diff approval state.

Verification card 5 — `test` blocked without `replay`

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-missing-replay'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root -ApproveDiff
.\tools\codex-official-update-patch-replay-template.ps1 -Stage test -SnapshotRoot $root -WhatIf
```

- expected result — `test` stops with an error saying `replay` is required
- failure triage pointer — inspect:
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when the test stage incorrectly skips replay.
- `$root\checkpoint.json` - snapshot checkpoint file that should record whether replay completed.

Verification card 6 — decision-row overrides survive reruns

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-row-rerun'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
# manually edit $root\patch-decision-table.json here
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
```

- expected result — manual JSON overrides remain preserved across the second `diff` run
- failure triage pointer — inspect:
- `$root\patch-decision-table.json` - JSON decision table that should preserve manual decision overrides.
- `$root\patch-decision-table.csv` - CSV companion decision table generated for reviewer-friendly inspection.
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when decision table reruns overwrite manual choices.

Verification card 7 — locked rows stay preserved once `decision_locked` lands

```powershell
$root = 'D:\PythonProject_langgraph\.tmp\verify-decision-lock-rerun'
if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -SnapshotRoot $root
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
# manually set decision_locked=true in $root\patch-decision-table.json here
.\tools\codex-official-update-patch-replay-template.ps1 -Stage diff -SnapshotRoot $root
```

- expected result — rows marked with `decision_locked = true` remain preserved after the rerun
- failure triage pointer — inspect:
- `$root\patch-decision-table.json` - JSON decision table that should preserve locked rows after reruns.
- `tools/codex-official-update-patch-replay-template.ps1` - script to inspect when locked decision rows are not preserved.

### Do not touch

- do not modify the official npm-installed `oh-my-codex` runtime files as part of this increment
- do not move this work out of the repo-local lane unless a specific upstream-install patch is intentionally required
- do not rewrite the frozen contract surface before implementing it

## Immediate Implementation Handoff

If a new session needs more context after reading the command card, continue here.

### Where the lane currently stands

- the operator-surface maintenance lane is already active and usable
- `tools/codex-official-update-patch-replay-template.ps1` is already implemented
- the script already supports:
  - staged execution
  - checkpoint continuity
  - decision-table exports
  - hard stage gates
- the frozen decision-lock plus diff-approval increment is now implemented in `tools/codex-official-update-patch-replay-template.ps1`

### What the latest increment implemented

The frozen decision-lock plus diff-approval increment is now implemented in `tools/codex-official-update-patch-replay-template.ps1`.

Implemented items:

- `decision_locked` — the lock flag that stops the script from overwriting a manually frozen decision row
- `decision_lock_reason` — the short note that explains why the row was intentionally locked
- `approvals.diff_review` — the checkpoint approval block that stores explicit diff-review approval state
- `approved` — the boolean that means diff review passed
- `approved_at` — the timestamp that records when diff review passed
- `approval_note` — the short reviewer note
- `-Stage diff -ApproveDiff` — the command form that writes diff approval into the checkpoint manifest
- `replay requires approvals.diff_review.approved = true` — the stronger replay gate

## Drift-prone repository context moved down from the project startup summary

Current working-stage snapshot for this mainline:

- the initial LangGraph deepening queue is already closed
- the earlier capability-gap sync pass is also already closed
- the current active named repository mainline remains `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`
- the current active maintenance lane inside that mainline is the operator-surface update / diff / replay / gate work

Archived rollout context retained here for cold starts:

- the bounded graph-kernel rollout is closed
- the bounded primary-runtime engine rollout is closed
- the bounded compiled-invocation rollout is closed
- the bounded live-execution rollout is closed
- the generalized live-routing rollout is closed
- the subgraph persistence and state-inspection rollout is closed
- the fuller live primary-execution-engine rollout is closed
- the richer automatic runtime-policy rollout is closed
- the broader automatic runtime-policy rollout is closed
- the deeper live primary-engine rollout is closed
- the superstep live primary-engine rollout is closed
- the stateful live primary-engine rollout is closed
- the graph-resident live primary-engine boundary-state rollout is closed
- the subgraph-aware live primary-engine handoff-state rollout is closed
- the approval-aware live primary-engine resume-state rollout is closed
- the post-approval-aware-resume-state capability-gap sync pass is closed
- the recovery-aware live primary-engine provenance-state rollout is closed
- the durable-artifact-aware live primary-engine state rollout is closed
- the post-durable-artifact-aware capability-gap sync pass is closed
- the reducer-aware live primary-engine merge-state rollout is closed
- the post-reducer-aware capability-gap sync pass is closed
- the command-aware live primary-engine control-state rollout is closed
- the post-command-aware capability-gap sync pass is closed
- the runtime-aware live primary-engine context-store-state rollout is closed
- the post-runtime-aware capability-gap sync pass is closed
- the memory-aware live primary-engine semantic-state rollout is closed
- the post-memory-aware capability-gap sync pass is closed
- the migration-aware live primary-engine compatibility-state rollout is closed

Current execution priority inherited from the former project startup summary:

1. sync the bilingual LangGraph capability-gap appendix with the validated post-migration-aware state
2. keep startup-facing repository summaries aligned with the archived migration-aware work and the current operator-surface maintenance lane
3. keep future-work narrative limited to the real post-migration-aware gaps only
4. close the current sync pass with OpenSpec validation before opening any later LangGraph-deepening candidate

## Implementation Background From This Session

This session completed the following repository-local cold-start surfaces:

- standardized a documented **official update + diff check + local patch replay** workflow in `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
- implemented `tools/codex-official-update-patch-replay-template.ps1`
- added stage-based execution to that script:
  - `precheck` — the pre-update inventory stage
  - `update` — the official update stage
  - `diff` — the post-update review stage
  - `replay` — the patch reapplication stage
  - `test` — the regression verification stage
  - `all` — the end-to-end convenience lane
- added checkpoint continuity:
  - latest pointer file: `.tmp/official-update-patch-replay-latest.json`
  - per-run checkpoint manifest: `<snapshot-root>/checkpoint.json`
- added generated cold-start artifacts:
  - `report.json` — machine-readable run summary
  - `checklist.md` — human-readable operator checklist
  - `patch-decision-table.md` — Markdown review view
  - `patch-decision-table.json` — JSON read-back source of truth
  - `patch-decision-table.csv` — spreadsheet-oriented export view
- added machine-readable decision rows with `decision_status`:
  - `auto_prefilled` — script-generated default decision
  - `manually_overridden` — human-changed decision
  - `unresolved` — still awaiting explicit human decision
- added hard stage gates already implemented in code:
  - no `precheck` -> `update / diff / replay / test` blocked
  - no `diff` -> `replay / test` blocked
  - no `replay` -> `test` blocked
- updated the bilingual Appendix C text so critical terms and variable names now include brief explanations instead of being left as bare identifiers

## Detailed Frozen Next-Change Contract Ready For Implementation

The following next-change items were frozen in the bilingual docs and are now implemented in the script:

- `decision_locked` — a lock flag that stops the script from overwriting a manually frozen row
- `decision_lock_reason` — a short explanation for why the row was intentionally locked
- `approvals.diff_review` — the checkpoint approval block that stores explicit diff-review approval state
- `approved` — the boolean that means diff review passed
- `approved_at` — the timestamp that records when diff review passed
- `approval_note` — the short reviewer note
- `-Stage diff -ApproveDiff` — the command form that writes diff approval into the checkpoint manifest
- `replay requires approvals.diff_review.approved = true` — the stronger replay gate

## Current Change-Readiness Verdict

The implementation side has now landed the frozen increment; the documentation side remains aligned with the shipped behavior:

- scope is frozen
- English and Chinese startup summaries are aligned
- critical terms and variables are briefly explained
- the latest implementation target has landed

That means a new session does **not** need to reopen the design question for this increment.

## Next Action For A New Session

If a new session continues this lane, do this next:

1. read this file
2. read `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md`
3. inspect or extend the implemented decision-lock plus diff-approval behavior in `tools/codex-official-update-patch-replay-template.ps1` if more follow-up is needed
4. keep the bilingual Appendix C text in implemented-state wording
5. rerun smoke checks for:
- `precheck -> diff` - smoke-check stage sequence for validating precheck-to-diff progression.
   - replay blocking without required prior stages
   - test blocking without replay
   - JSON decision-row override preservation across reruns

## Important Non-Drift Notes

- this session did **not** modify the official npm-installed `oh-my-codex` runtime files
- this session focused on repo-local tooling and startup-facing documentation only
- PowerShell console mojibake on the Chinese docs is an output-encoding issue, not evidence of source-file corruption
