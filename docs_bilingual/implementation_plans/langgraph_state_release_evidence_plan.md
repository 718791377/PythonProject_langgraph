---
doc_id: langgraph_state_release_evidence_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/langgraph_state_release_evidence_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# LangGraph State Release Evidence Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Reject stale running LangGraph state after completed work and require explicit close, release, or handoff evidence.

## Source Plans

- automatic_orchestration_routing_enforcement_plan; codex_user_level_cross_session_durable_state_isolation_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented and locally validated
Stage: Stage C implementation package
Owner session: `codex-langgraph-state-release-evidence-20260530`
Current gate: local validation complete before local main integration; remote publication remains out of scope
Stage C entry condition: satisfied by user confirmation message on 2026-05-30 after the child plan was already on local `main`
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/langgraph_durable_orchestrator/*
- tools/check_durable_artifact_state_surfaces.py
- test/*langgraph*state*release*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- .omx/state/langgraph
- LangGraph compatibility records

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for completed, running, released, and handoff LangGraph states.
- [x] Update durable state checker to flag stale running state after completion.
- [x] Document safe backend-family handoff requirements.
- [x] Run durable state and LangGraph checks plus local gate.
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
- 2026-05-30 Stage C implementation: branch `implement-langgraph-state-release-evidence-20260530` adds structured LangGraph state-release fixtures, extends `tools/check_durable_artifact_state_surfaces.py` to reject completed `running` state and missing release/handoff fields, registers `test/check_langgraph_state_release_evidence.test.py`, and documents backend-family handoff requirements; final local-main commit will be recorded after integration.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
