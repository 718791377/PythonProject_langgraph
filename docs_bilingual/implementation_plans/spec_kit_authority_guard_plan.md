---
doc_id: spec_kit_authority_guard_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/spec_kit_authority_guard_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Authority Guard Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Block Spec Kit authority migration commands such as specify init --force, .specify creation, or governance takeover without a separate active plan.

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
Status: implemented; validating local integration package
Stage: Stage C implementation package
Owner session: codex-20260601-spec-kit-authority-guard
Current gate: run focused checks, local gate, and local MR review before local main integration
Stage C entry condition: satisfied by current user implementation request on 2026-06-01
Last updated: 2026-06-01
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_spec_kit_authority_guard.py
- test/*spec_kit*authority*
- docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md

## Hotspot Serialization

Only one session may own each hotspot at a time:

- Spec Kit guard checker
- .specify path handling

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add tests for safe references to Spec Kit docs and unsafe authority-changing operations.
- [x] Implement a checker that fails closed on .specify governance takeover without an active plan.
- [x] Register the checker in the local gate only after implementation confirmation.
- [x] Run Spec Kit guard tests and local gate.
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
- 2026-06-01 implementation package: added `tools/check_spec_kit_authority_guard.py`, `test/spec_kit_authority_guard.test.py`, subordinate-adapter governance docs, CI manifest registration, safety-rule registry backing, and OpenSpec guard integration; focused tests passed before local gate.
<!-- EVIDENCE_INDEX_END -->
