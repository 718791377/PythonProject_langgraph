---
doc_id: routing_trace_structured_evidence_schema_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/routing_trace_structured_evidence_schema_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Routing Trace Structured Evidence Schema Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Separate conversation display from structured ASCII evidence fields for routing traces. User-visible `Routing trace` remains a plain-text diagnostic line with the fixed label and `key=value` fields; the structured evidence schema and checkers are saved-evidence contracts, not a Codex CLI progress-panel API.

## Source Plans

- automatic_orchestration_routing_enforcement_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: implementation has been confirmed, completed through existing checker and documentation packages on local `main`, and this file now records the closeout package.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented and locally validated
Stage: Stage C closeout package merged to local `main`
Owner session: `codex-update-routing-trace-structured-evidence-schema-status-20260531` means the local status-only closeout session claim for this plan update.
Current gate: closeout documentation is integrated into local `main`; stop at the remote publication gate until the user explicitly authorizes GitLab/GitHub publication
Stage C entry condition: satisfied by user confirmation and by local `main` integration of the closeout documentation
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_orchestration_trace_evidence.py
- test/check_orchestration_trace_evidence.test.py
- tools/check_orchestration_collaboration_evidenceguard.py
- test/fixtures/orchestration_*
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md

## Hotspot Serialization

Only one session may own each hotspot at a time:

- orchestration evidence fixtures
- trace schema fields

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define required structured fields for phase, capability_chain, backend_default, backend_ready, experts, durable workflow, persistent team, and reason.
- [x] Add invalid checker cases/fixtures with missing blockers or collapsed capability states.
- [x] Update checker logic and docs examples.
- [x] Run orchestration evidence tests and local gate.
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
- 2026-06-01 progress-surface boundary confirmation: branch `document-progress-surface-boundary-20260601` records that routing trace structured evidence/checker data does not imply a user-visible Codex CLI panel; `Routing trace` remains the plain-text diagnostic line.
- 2026-05-31 local-main status closeout: branch `update-routing-trace-structured-evidence-schema-status-20260531` means the status-only closeout branch used to record the transition from pending local integration to the remote-publication gate after the closeout documentation was integrated into local `main`.
- 2026-05-31 Stage C closeout: branch `close-routing-trace-structured-evidence-schema-20260531` records that the structured routing trace schema is implemented through `tools/check_orchestration_trace_evidence.py`, `test/check_orchestration_trace_evidence.test.py`, `tools/check_orchestration_collaboration_evidenceguard.py`, and the activation-policy documentation surface; final local-main commit is recorded in the assistant response and local git history.
- 2026-05-30 implementation baseline: local `main` contains the structured trace and collaboration evidence packages, including fixed `Routing trace` / `Updated Plan` label evidence and expert lifecycle non-evidence handling; validation evidence is in the checker test history and local CI records.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
