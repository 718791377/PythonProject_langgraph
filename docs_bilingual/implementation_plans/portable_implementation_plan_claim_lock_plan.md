---
doc_id: portable_implementation_plan_claim_lock_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/portable_implementation_plan_claim_lock_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage C implementation
phase: 1
batch: 1
confirmation_required: true
confirmed_for_implementation_at: 2026-05-28
---

# Portable Implementation Plan Claim Lock Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Implement a Git and filesystem portable single-active-session claim lock for each child implementation plan without requiring OMX or LangGraph.

## Source Plans

- codex_governance_session_visibility_and_plan_lock_plan; codex_user_level_cross_session_durable_state_isolation_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage C implementation slice for Phase 1 Batch 1.
- Phase: Phase 1.
- Status: confirmed for Stage C implementation in the main Codex leader session; non-document implementation may proceed inside the declared feature worktree.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage C implementation validated; ready for local main integration
Owner session: main Codex leader session
Current gate: local gate and local MR review passed; merge this feature branch serially into local `main`
Stage C entry condition: satisfied by user confirmation after local `main` integration of the Stage B child-plan package
Last updated: 2026-05-28
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_implementation_plan_claim_lock.py
- tools/claim_implementation_plan.py
- .omx/session-claims/ examples or fixtures
- test/*claim*lock*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- claim file format
- docs_bilingual/docs_registry.yaml if registry fields are added

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial and leader-owned.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define the portable claim schema with plan path, branch, worktree, session id, and expiry or release state.
- [x] Add tests for one active claim, stale claim, released claim, and conflicting active claim.
- [x] Implement the claim helper and checker without depending on OMX or LangGraph.
- [x] Run claim-lock tests, worktree receipt checker, and local gate.
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
- 2026-05-28 Stage C validation: `python test/check_implementation_plan_claim_lock.test.py`, `tools/ci/local_gate.ps1 -StepTimeoutSeconds 600`, and `tools/ci/local_mr_review.ps1` passed in branch `implement-portable-plan-claim-lock-20260528`.
- 2026-05-28 Stage C implementation: added `tools/check_implementation_plan_claim_lock.py`, `tools/claim_implementation_plan.py`, focused tests, and local guard registration for portable implementation-plan claim locking.
- 2026-05-28 Stage C entry: user confirmed continued implementation of this child plan; governance status updated in branch `implement-portable-plan-claim-lock-20260528` before runtime/checker work.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
