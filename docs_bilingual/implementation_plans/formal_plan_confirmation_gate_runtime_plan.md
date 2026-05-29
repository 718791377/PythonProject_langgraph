---
doc_id: formal_plan_confirmation_gate_runtime_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/formal_plan_confirmation_gate_runtime_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 1
batch: 1
confirmation_required: true
---

# Formal Plan Confirmation Gate Runtime Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Enforce that chat-only plan confirmation is not enough for non-document implementation.

## Source Plans

- implementation_plan_confirmation_gate

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
Stage: Stage C implementation integrated into local main and verified
Owner session: main Codex leader session
Current gate: included in Phase 1 closure; remote publication is authorized after this closure package is locally integrated
Stage C entry condition: satisfied by confirmed receipt/claim for this active implementation plan
Last updated: 2026-05-29
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/governance/openspec_opsx_project_usage_policy.md
- docs_bilingual/governance/openspec_opsx_project_usage_policy.zh-CN.md
- tools/check_plan_exit_execution_governance.py
- tools/complete_local_flow_to_remote_gate.py
- test/*plan*confirmation*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- tools/complete_local_flow_to_remote_gate.py
- precommit helper surfaces

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial and leader-owned.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add negative tests for chat-only confirmation without a committed active implementation-plan file.
- [x] Add positive tests for active registered committed plan-file confirmation.
- [x] Implement the helper/checker gate with fail-closed behavior.
- [x] Update governance docs and run the plan-exit checker plus local gate.
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
- 2026-05-29 Phase 1 closure: implementation is contained in local `main` at `e81d840`; Phase 1 closure verification confirmed the formal plan confirmation gate is implemented, integrated, and covered by repository gates before remote publication.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-28 Stage C implementation: receipt/claim recorded explicit user confirmation for `docs_bilingual/implementation_plans/formal_plan_confirmation_gate_runtime_plan.md` against Stage B governance package `4a92f9fc673923a6fec9e31cbcee0526535531b7`; targeted tests and repository gates are recorded in the implementation session output.
<!-- EVIDENCE_INDEX_END -->
