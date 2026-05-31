---
doc_id: comet_management_record_bootstrap_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/comet_management_record_bootstrap_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Management Record Bootstrap Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Create and validate Comet management records that capture focus-area checklist evidence for each phase.

## Source Plans

- comet_runtime_agile_focus_area_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 5.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: completed and locally integrated; included in the current remote-publication carrier
Stage: Phase 5 final closeout package
Owner session: `codex-implement-comet-management-record-bootstrap-20260531`
Current gate: remote publication authorized by the current user message; no further local Phase 5 work remains
Stage C entry condition: satisfied by current user confirmation on 2026-05-31 after Stage B child-plan creation
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- .codex/skills/comet/scripts/comet-state.sh or installed Comet script source
- .codex/skills/comet/scripts/comet-guard.sh or installed Comet script source
- openspec/changes/*/management.md fixtures
- test/*comet*management*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- comet-state.sh
- comet-guard.sh

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add management-record fixture examples for Open, Design, Build, Verify, Archive, and Monitoring.
- [x] Implement bootstrap behavior only after script ownership is clear.
- [x] Validate required management record path fields and safe path constraints.
- [x] Run Comet script tests, OpenSpec guard, and local gate.
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
- 2026-05-31 Stage C implementation closeout: current user confirmation authorized this child-plan implementation; branch `implement-comet-management-record-bootstrap-20260531` closes the plan by confirming that Comet runtime management records, checklist gates, monitoring return state, path validation, and archive closing evidence are already implemented and covered by focused tests. Final local-main commit and validation evidence are recorded in the assistant response and local git history.
- 2026-05-28 runtime baseline: `.codex/skills/comet/scripts/comet-state.sh` creates `management.md` and records `management_record`, `monitoring_status`, `control_decision`, `target_phase`, `rework_reason`, and `iteration_count`; `.codex/skills/comet/scripts/comet-yaml-validate.sh`, `comet-guard.sh`, and `comet-archive.sh` validate management-record paths, checklist evidence, Monitoring-loop clearance, and closing evidence.
- 2026-05-28 test coverage baseline: `test/comet_runtime_management_flow.test.py` covers Open, Design, Build, Verify, Archive, and Monitoring management evidence, return-transition invariants, UTF-8/legacy label compatibility, required field validation, and safe path constraints; the test is registered in `tools/ci/ci_test_manifest.json`.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-31 remote-publication carrier: this Phase 5 child plan is included in local `main` and the current user-authorized GitLab/GitHub publication package; no further local Phase 5 implementation work remains before Phase 6 admission.
<!-- EVIDENCE_INDEX_END -->
