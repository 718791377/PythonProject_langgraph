---
doc_id: plan_inventory_registry_alignment_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/plan_inventory_registry_alignment_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 0
batch: 1
confirmation_required: true
---

# Plan Inventory Registry Alignment Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Inventory active implementation plans, registry entries, stable anchors, and evidence-index health before parallel execution starts.

## Source Plans

- multi_plan_parallel_session_orchestration_plan; implementation_plan_confirmation_gate

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 1.
- Phase: Phase 0.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Phase 0 closure implemented in local feature branch
Owner session: `phase0-plan-index-closure-20260530`
Current gate: validate inventory evidence, local gates, local MR review, then merge to local `main` and stop at the remote publication gate.
Stage C entry condition: user confirmed Phase 0 must complete before Phase 2; this closure records the inventory result.
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/docs_registry.yaml
- docs_bilingual/implementation_plans/*
- tools/implementation_plan_size_baseline.json

## Hotspot Serialization

Only one session may own each hotspot at a time:

- docs_bilingual/docs_registry.yaml
- tools/check_implementation_plan_rules.py

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial and leader-owned.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after it is integrated into local main.
- [x] Read the registry and produce a machine-checkable inventory of implementation-plan pairs.
- [x] Add or update checker coverage for missing registry entries, missing stable anchors, and missing evidence index references.
- [x] Repair only registry or anchor issues assigned to this child plan; no blocking registry or bilingual-pair defect was found.
- [x] Run implementation-plan rules, precommit update/archive review, local gate, and local MR review.
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
- 2026-05-30 Phase 0 inventory closure: machine-readable evidence is recorded in `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.json`; readable evidence is recorded in `docs_bilingual/implementation_evidence/phase0_plan_inventory_registry_alignment_20260530.md`. The inventory found 59 implementation-plan registry entries, 52 active entries, no missing registered paths, and no missing bilingual companion paths.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
