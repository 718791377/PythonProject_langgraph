---
doc_id: implementation_plan_registry_active_state_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/implementation_plan_registry_active_state_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 1
batch: 1
confirmation_required: true
---

# Implementation Plan Registry Active State Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Require implementation plans to be active, bilingual, registered, and confirmation-ready before implementation starts.

## Source Plans

- implementation_plan_confirmation_gate; multi_plan_parallel_session_orchestration_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 1.
- Phase: Phase 1.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage C implementation package
Owner session: implement-registry-active-state-20260528
Current gate: local git commit and local MR review
Stage C entry condition: satisfied by user confirmation on 2026-05-28
Last updated: 2026-05-28
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/docs_registry.yaml
- tools/check_implementation_plan_rules.py
- tools/implementation_plan_size_baseline.json
- test/*implementation_plan*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- docs_bilingual/docs_registry.yaml
- tools/check_implementation_plan_rules.py

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial and leader-owned.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add registry-state checks for active implementation plans and bilingual companions.
- [x] Add tests for missing companion, wrong status, missing anchors, and missing registry record.
- [x] Update implementation-plan checker messages with Chinese-facing operator guidance where appropriate.
- [x] Run implementation-plan checker, precommit review, and local gate.
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
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-28 Stage C implementation: claimed by `implement-registry-active-state-20260528`; added checker-backed active-plan registry state validation, bidirectional registry/front-matter status matching, regression tests for missing registry/wrong status/missing companion coverage, Chinese-facing guidance in checker findings, and repaired the pre-existing Project MOE active registry/front-matter mismatch.
- 2026-05-28 validation: targeted implementation-plan tests, claim-lock tests, `check_implementation_plan_rules.py --json`, precommit update/archive review, session-ownership check, worktree receipt check, `git diff --check`, and `tools/ci/local_gate.ps1` passed in `implement-registry-active-state-20260528`.
<!-- EVIDENCE_INDEX_END -->
