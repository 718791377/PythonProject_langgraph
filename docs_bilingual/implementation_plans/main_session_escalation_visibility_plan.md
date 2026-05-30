---
doc_id: main_session_escalation_visibility_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/main_session_escalation_visibility_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 1
batch: 1
confirmation_required: true
---

# Main Session Escalation Visibility Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Make main-session permission escalation, pending approval, and timeout risk visible before OMX or LangGraph workflows depend on it.

## Source Plans

- codex_governance_session_visibility_and_plan_lock_plan

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
Stage C entry condition: satisfied by user confirmation to continue this confirmed child plan
Last updated: 2026-05-29
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md
- tools/check_orchestration_collaboration_evidenceguard.py
- test/*escalation*visibility*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- orchestration activation evidence schema
- conversation routing trace wording

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define required fields for pending approval, approval timeout risk, and main-session-only escalation.
- [x] Add evidence fixtures for pending, granted, timed-out, and not-needed escalation states.
- [x] Update checker logic to reject invisible escalation waits.
- [x] Run routing evidence checks and local gate.
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
- 2026-05-29 Phase 1 closure: main-session escalation visibility is contained in local `main` at `e23c40b`; Phase 1 closure verification confirmed pending approval, timeout-risk, and approval-receipt evidence surfaces before remote publication.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-28 Stage C implementation: added trace/evidenceguard fields `main_session_escalation`, `approval_timeout_risk`, and `approval_receipt`; added pending/granted/timed-out/not-needed fixtures; updated governance/OpenSpec surfaces, checker snippets, and CI manifest. Validation evidence is recorded in the final assistant response for branch `implement-main-session-escalation-visibility-20260528`.
<!-- EVIDENCE_INDEX_END -->
