---
doc_id: durable_smoke_adoption_gate_template_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/durable_smoke_adoption_gate_template_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable Smoke Adoption Gate Template Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Create the durable smoke and adoption gate template before any live durable runtime exercise or apply-mode adoption is allowed.

## Source Plans

- codex_user_level_cross_session_durable_state_isolation_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 3.
- Status: this file is an active child implementation plan; the user has confirmed implementation of the read-only gate-template package.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: implementation package validated in feature worktree
Owner session: main Codex leader session
Current gate: implementation confirmed by user; runtime exercise, live smoke, and apply mode remain delayed until this gate passes and a later reviewed change explicitly authorizes them
Stage C entry condition: local validation is green; local MR review and local main integration of the read-only gate-template package remain next
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/governance/langgraph_user_level_runtime_policy.md
- tools/*durable*gate*
- test/*durable*gate*
- codex-durable-state-status.ps1

## Hotspot Serialization

Only one session may own each hotspot at a time:

- codex-durable-state-status.ps1
- tools/install-codex-user-level-team-mode.ps1

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan for implementation.
- [x] Define R0.6.0 gate template fields and R0.6.1 gate field checker behavior.
- [x] Add negative checker fixtures that block R0.6.2 live smoke or apply-mode adoption without the gate template.
- [x] Document that runtime exercise, live smoke, and apply mode are delayed until after this gate passes.
- [x] Run durable gate tests and local gate.
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
- 2026-05-30 implementation: extended `tools/check_durable_routing_smoke_gate_template.py` with candidate-template validation and default read-only self-test fixtures under `tools/fixtures/durable_routing_smoke_gate_template/`; the existing OpenSpec guard invocation covers these fixtures because the checker runs self-test by default.
- 2026-05-30 validation: `python tools\check_durable_routing_smoke_gate_template.py --root . --json`, `python tools\check_document_pair_policy.py --root . --json`, `python tools\check_name_clarity_rules.py --root . --json`, `python tools\check_precommit_update_archive.py --root . --json`, and `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` passed in the feature worktree before commit. Local MR review remains the pre-integration gate after the feature commit is clean.
<!-- EVIDENCE_INDEX_END -->
