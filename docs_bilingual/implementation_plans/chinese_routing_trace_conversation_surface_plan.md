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

# Routing trace and Updated Plan Conversation Surface Stability Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Require user-facing conversation surfaces to keep the fixed literal labels `Routing trace` and `Updated Plan`; those labels must not be replaced with localized headings. Explanatory content under the labels may be Chinese. `Updated Plan` must remain a checklist/status-list surface rather than prose-only text, while saved structured evidence keeps machine-readable ASCII threshold tokens, blocker tokens, schema keys, file names, and CLI arguments.

## Source Plans

- `codex_governance_session_visibility_and_plan_lock_plan` - defines conversation-surface visibility and plan-lock governance.
- `automatic_orchestration_routing_enforcement_plan` - defines automatic routing evidence and activation parity requirements.
- `multi_plan_parallel_session_orchestration_plan` - provides this Phase 4 child-plan family context.

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: this child implementation plan has completed the fixed English labels and `Updated Plan` checklist semantics runtime/checker slice; this file now records the closeout package for the final validation checklist item.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented and locally validated
Stage: Stage C closeout package
Owner session: `codex-close-chinese-routing-trace-conversation-surface-plan-20260531`
Current gate: closeout documentation pending local validation, local commit, local MR review, local `main` integration, and stop at the remote publication gate
Stage C entry condition: satisfied by the fixed-label runtime/checker slice already merged to local `main`; this package closes the remaining validation checklist item
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - English parent plan that declares Phase 4 scope.
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - Chinese companion parent plan for Phase 4 scope.
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.md` - English primary child plan for this slice.
- `docs_bilingual/implementation_plans/chinese_routing_trace_conversation_surface_plan.zh-CN.md` - Chinese companion child plan for this slice.

This runtime/checker implementation slice also owns:

- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - English governance target for fixed-label examples.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` - Chinese governance target for fixed-label examples.
- `tools/check_orchestration_collaboration_evidenceguard.py` - checker target for conversation-surface fixtures.
- `test/fixtures/orchestration_prompt_independent_collaboration_parity/conversation_surface_*` - fixtures for stable labels and checklist semantics.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- user-facing `Routing trace` label and explanatory wording
- user-facing `Updated Plan` label and checklist semantics
- routing evidence schema
- plan-progress evidence schema

## Parallel Session Contract

- All eligible child plans in this phase may run under Work-Conserving admission.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel implementation is allowed only with different child plans and disjoint write scopes, or after acquiring the relevant hotspot lease.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Update the parent plan Phase 4 so conversation surfaces cover both `Routing trace` and `Updated Plan`.
- [x] Update this child plan's goal, scope, hotspots, tasks, and acceptance criteria.
- [x] Synchronize the English ASCII primary and Chinese companion files.
- [x] Record that localized replacement of the fixed `Routing trace` label is prohibited.
- [x] Record that localized replacement of the fixed `Updated Plan` label is prohibited.
- [x] Add checker/fixture coverage that rejects localized replacement of the fixed labels and rejects prose-only `Updated Plan` output.
- [x] Run the routing evidence checker, implementation-plan checker, local gate, and local MR review.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- Parent Phase 4 explicitly covers the fixed user-facing `Routing trace` and `Updated Plan` surfaces.
- This child plan distinguishes user-facing fixed-label surfaces from saved machine-readable ASCII evidence.
- Conversation output must keep `Routing trace` as the user-facing routing decision label; explanatory content may be Chinese.
- Conversation output must keep `Updated Plan` as the user-facing plan-progress label.
- `Updated Plan` must preserve checklist/status-list semantics, such as checkbox lines or pending / in_progress / completed items, rather than being replaced by ordinary prose.
- English tool names, file names, schema keys, threshold tokens, blocker tokens, and CLI arguments may remain ASCII.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-31 Stage C closeout: branch `close-chinese-routing-trace-conversation-surface-plan-20260531` records the final validation checklist item as complete for the already-implemented fixed `Routing trace` and `Updated Plan` conversation surface contract; final local-main commit and validation evidence are recorded in the assistant response and local git history.
- 2026-05-30 implementation baseline: local `main` contains the fixed-label runtime/checker package in `implement-routing-updated-plan-fixed-labels-20260530c`, including checker/fixture coverage for stable `Routing trace` and `Updated Plan` labels and checklist semantics.
- 2026-05-30 stable-label correction: user confirmed that `Routing trace` and `Updated Plan` remain English user-facing labels; `Updated Plan` keeps checklist semantics. This slice updates the parent/child plan constraints and adds checker/fixture coverage for that corrected contract.
- 2026-05-30 Phase 4 conversation-surface governance update: branch `chinese-routing-updated-plan-20260530` previously extended the surface scope from routing traces to both routing traces and updated plans; this correction supersedes the mistaken label-localization requirement.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
