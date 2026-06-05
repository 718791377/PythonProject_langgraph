---
doc_id: worktree_receipt_claim_lifecycle_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/worktree_receipt_claim_lifecycle_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Worktree Receipt Claim Lifecycle Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Define and enforce active, paused, ready-to-merge, merged-local-main, completed, superseded, stale, and cleaned lifecycle states for worktree receipts and session claims.

## Source Plans

- codex_user_level_cross_session_durable_state_isolation_plan; codex_governance_session_visibility_and_plan_lock_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 3.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage C local implementation package
Owner session: implement-worktree-receipt-claim-lifecycle-20260530
Current gate: implement, validate, archive, commit, and merge to local main; stop at remote publication gate
Stage C entry condition: satisfied by explicit user request on 2026-05-30 to continue this plan
Last updated: 2026-05-30
Companion refresh note: the zh-CN companion was refreshed in this local package to replace English or mixed prose with Chinese prose while preserving runtime tokens; no runtime behavior changed.
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_worktree_task_receipt.py
- .omx/worktree-task-receipt.json fixtures
- .omx/session-claims fixtures
- test/*worktree*receipt*

## Upstream Scheduling Contract

Worktree receipt lifecycle is a state source for the Phase 1A scheduler/ROB model: ready-to-merge maps to ROB `ready`, merged-local-main maps to `retired`, and stale/superseded states map to blocked or flushed entries.


## Hotspot Serialization

Only one session may own each hotspot at a time:

- receipt lifecycle schema
- cleanup helper behavior

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

## Real Runtime Implementation Gap

Receipt/claim lifecycle validation is implemented, but lifecycle advancement is not automated. Real runtime work must safely advance active -> ready -> merged-local-main -> completed -> cleaned with receipts and rollback references.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add schema fixtures for every allowed lifecycle state.
- [x] Require completion fields for merged, completed, cleaned, and remote-sync-needed states.
- [x] Document cleanup and branch deletion evidence without forcing immediate cleanup.
- [x] Run receipt checker, local gate, local MR review, archive, and post-archive validation.
- [x] Align receipt lifecycle states with Phase 1A ROB entry states before runtime integration.
- [ ] Stage D real runtime: implement lifecycle advancement helper for active, paused, ready-to-merge, merged-local-main, completed, stale, superseded, and cleaned states.
- [ ] Stage D real runtime: require every state transition to record owner, previous state, next state, evidence paths, rollback ref, and cleanup decision.
- [ ] Stage D real runtime: integrate lifecycle advancement with local-main retire evidence without authorizing remote publication.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- The child plan is confirmed by the user after local `main` integration.
- The active session claim names this child plan path before write work starts.
- Tests or checker fixtures fail before the implementation when the change is behavior-changing.
- Governance docs, runtime helpers, checkers, tests, and CI registration stay aligned.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for active-to-ready-to-merged-to-cleaned lifecycle advancement; this package updates plan governance only and does not run live runtime.
- 2026-05-30 validation package: focused receipt tests, receipt checker, implementation-plan checker, OpenSpec spec validation, pre-commit update/archive review, local gate, and local MR review all passed before local main integration.
- 2026-05-30 implementation package: added `stale` receipt/claim lifecycle validation, all-state fixtures, and completion-evidence grouping; OpenSpec change `implement-worktree-receipt-claim-lifecycle-20260530` records stale as a classification state rather than cleanup or branch-deletion evidence.
- 2026-05-30 complete-flow alignment: receipt lifecycle remains the ROB state source; `ready-to-merge` maps to a ready candidate package, and `merged-local-main` maps to retired evidence after lock-backed self-retire.
- 2026-05-29 upstream contract supplement: referenced the Phase 1A scheduler/ROB model as the later portable/receipt runtime alignment source.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
