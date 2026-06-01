---
doc_id: spec_kit_subordinate_adapter_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/spec_kit_subordinate_adapter_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Subordinate Adapter Governance Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Document GitHub Spec Kit as an optional subordinate adapter or template source, not a competing governance layer.

## Source Plans

- codex_governance_session_visibility_and_plan_lock_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 6.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Stage: Stage C implementation package
Owner session: codex-implement-spec-kit-subordinate-adapter-governance-20260601
Current gate: local validation, commit, local main integration, then stop at the remote-publication approval gate
Stage C entry condition: satisfied by current user instruction to continue this child plan
Last updated: 2026-06-01
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md
- docs_bilingual/governance/spec_kit_subordinate_adapter_policy.zh-CN.md
- docs_bilingual/docs_registry.yaml

## Hotspot Serialization

Only one session may own each hotspot at a time:

- new governance doc registry entries

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Document authority order: Comet controls OpenSpec WHAT and Superpowers HOW; Spec Kit may only provide subordinate templates unless a separate plan changes that.
- [x] Add usage boundaries for any future specify command.
- [x] Register the new governance pair if created.
- [x] Run docs registry and implementation-plan checks.
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
- 2026-06-01 Stage C implementation: reused the registered `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md` and `.zh-CN.md` governance pair, added future `specify` command boundary wording, and marked this child plan implemented-local; validation evidence is recorded in local command output and final assistant response.
<!-- EVIDENCE_INDEX_END -->
