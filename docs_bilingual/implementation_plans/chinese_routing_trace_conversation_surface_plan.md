---
doc_id: chinese_routing_trace_conversation_surface_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Chinese Routing Trace and Updated Plan Conversation Surface Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Require user-facing routing-trace and updated-plan conversation surfaces to use Chinese field labels, Chinese explanations, and Chinese status wording while saved structured evidence keeps machine-readable ASCII threshold tokens, blocker tokens, schema keys, file names, and CLI arguments.

## Source Plans

- `codex_governance_session_visibility_and_plan_lock_plan` - defines Chinese conversation visibility and plan-lock governance.
- `automatic_orchestration_routing_enforcement_plan` - defines automatic routing evidence and activation parity requirements.
- `multi_plan_parallel_session_orchestration_plan` - provides this Phase 4 child-plan family context.

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: this file is an active child implementation plan; this update was confirmed by the user for parent/child plan edits only, and later non-document runtime implementation still requires confirming the concrete implementation slice.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage B child-plan governance revision
Owner session: `codex-chinese-routing-updated-plan-20260530`
Current gate: this package updates only parent/child implementation plans; later runtime/checker implementation must proceed through a confirmed implementation slice
Stage C entry condition: explicit user confirmation for this child implementation plan's non-document implementation scope
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## File Ownership

- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - English parent plan that declares Phase 4 scope.
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - Chinese companion parent plan for Phase 4 scope.
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.md` - English primary child plan for this slice.
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.zh-CN.md` - Chinese companion child plan for this slice.

A later runtime/checker implementation slice may extend ownership to:

- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - future English governance target for examples.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` - future Chinese governance target for examples.
- `tools/check_orchestration_collaboration_evidenceguard.py` - future checker target for conversation-surface fixtures.
- `test/*routing_trace_chinese*` - future tests for user-facing routing-trace wording.
- `test/*updated_plan_chinese*` - future tests for user-facing updated-plan wording.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- user-facing routing-trace wording
- user-facing updated-plan wording
- routing evidence schema
- plan-progress evidence schema

## Parallel Session Contract

- All eligible child plans in this phase may run under Work-Conserving admission.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel implementation is allowed only with different child plans and disjoint write scopes, or after acquiring the relevant hotspot lease.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Update the parent plan Phase 4 so Chinese conversation surfaces cover both routing traces and updated plans.
- [x] Update this child plan's goal, scope, hotspots, tasks, and acceptance criteria.
- [x] Synchronize the English ASCII primary and Chinese companion files.
- [ ] Later runtime/checker implementation: add fixtures rejecting English-only user-facing routing traces.
- [ ] Later runtime/checker implementation: add fixtures rejecting English-only user-facing updated plans.
- [ ] Later governance implementation: update activation-policy examples to use Chinese equivalents of routing trace and updated plan.
- [ ] Later verification: run the routing evidence checker, implementation-plan checker, local gate, and local MR review.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .	ools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- Parent Phase 4 explicitly covers user-facing routing traces and user-facing updated plans.
- This child plan distinguishes user-facing Chinese surfaces from saved machine-readable ASCII evidence.
- Conversation output must not use English-only `Routing trace:` as the user-facing heading; use the Chinese routing-trace heading instead.
- Conversation output must not use English-only `Updated Plan` as the user-facing heading; use the Chinese updated-plan heading instead.
- English tool names, file names, schema keys, threshold tokens, blocker tokens, and CLI arguments may remain ASCII.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 Phase 4 Chinese conversation-surface governance update: branch `chinese-routing-updated-plan-20260530` updates this child plan and the parent plan to extend the user-facing Chinese requirement from routing traces to both routing traces and updated plans; this package updates implementation plans only and does not enter runtime/checker implementation.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
