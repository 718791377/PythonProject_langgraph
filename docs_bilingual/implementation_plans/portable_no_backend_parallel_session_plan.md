---
doc_id: portable_no_backend_parallel_session_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/portable_no_backend_parallel_session_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Portable No Backend Parallel Session Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Support multi-session parallel implementation using only Git worktrees, registry entries, and portable claim files when OMX and LangGraph are unavailable.

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
Stage: Stage B child-plan creation package
Owner session: unclaimed until implementation begins
Current gate: wait for explicit user confirmation of this child plan before non-document implementation
Stage C entry condition: user confirms this child implementation plan after local main integration
Last updated: 2026-05-29
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/claim_implementation_plan.py
- tools/check_implementation_plan_claim_lock.py
- docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md
- test/*portable_parallel*

## Upstream Scheduling Contract

Portable no-backend sessions consume the Phase 1A scheduler/ROB contract: no-backend claims may execute in parallel only when their predicted and actual write sets can later retire through the leader-owned ROB queue.


## Hotspot Serialization

Only one session may own each hotspot at a time:

- claim lock helper
- worktree isolation policy

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial and leader-owned.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [ ] Confirm this child plan after local main integration.
- [ ] Define no-backend session startup, claim, release, and cleanup steps.
- [ ] Add tests proving two sessions cannot claim the same child plan but can claim different child plans.
- [ ] Update governance docs with the portable fallback path.
- [ ] Run claim lock, worktree receipt, and local gate checks.
- [ ] Align portable claim startup/status output with the Phase 1A scheduler/ROB entry model before runtime integration.
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
- 2026-05-29 upstream contract supplement: referenced the Phase 1A scheduler/ROB model as the later portable/receipt runtime alignment source.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
