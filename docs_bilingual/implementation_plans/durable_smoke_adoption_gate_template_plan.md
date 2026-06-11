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
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for durable smoke adoption gate template.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: gate means the blocking checkpoint for adoption; `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `durable-smoke-adoption-gate-template`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with already accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
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

## Real Runtime Implementation Gap

Durable smoke/adoption is still template-only. Real runtime work must provide an executable durable smoke runner, apply-mode adoption helper, R3/R4/R5 receipts, and fail-closed evidence before any live adoption is claimed.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan for implementation.
- [x] Define R0.6.0 gate template fields and R0.6.1 gate field checker behavior.
- [x] Add negative checker fixtures that block R0.6.2 live smoke or apply-mode adoption without the gate template.
- [x] Document that runtime exercise, live smoke, and apply mode are delayed until after this gate passes.
- [x] Run durable gate tests and local gate.
- [x] Stage D real runtime: implement executable durable smoke runner that writes sanitized R4 smoke receipts and never collapses smoke success into adoption.
- [x] Stage D/R5 checker gate: implement apply-mode adoption helper that writes selected/running/adopted/released receipts and fail-closed rollback evidence.
- [x] Stage D/R5 checker gate: add live adoption handoff receipts with operator authorization, backend-family ownership, timeout release, and cleanup evidence.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python test/check_durable_routing_smoke_receipts.test.py -v` - validates the R4 smoke runner/checker.
- `python tools/check_durable_routing_smoke_receipts.py --root . --json` - validates the R4 smoke receipt checker self-test.
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
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for durable smoke adoption gate template. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-06 R4 smoke runtime implementation: branch `implement-durable-smoke-adoption-r4-20260605` adds `tools/run_durable_routing_smoke.py` and `tools/check_durable_routing_smoke_receipts.py`; the helper writes read-only `smoke-tested` receipts and the checker fails closed against adoption, mutation, durable-team launch, LangGraph thread start, and remote publication claims.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for real durable smoke, apply-mode adoption, and live adoption; this package updates plan governance only and does not run live runtime.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-30 implementation: extended `tools/check_durable_routing_smoke_gate_template.py` with candidate-template validation and default read-only self-test fixtures under `tools/fixtures/durable_routing_smoke_gate_template/`; the existing OpenSpec guard invocation covers these fixtures because the checker runs self-test by default.
- 2026-05-30 validation: `python tools\check_durable_routing_smoke_gate_template.py --root . --json`, `python tools\check_document_pair_policy.py --root . --json`, `python tools\check_name_clarity_rules.py --root . --json`, `python tools\check_precommit_update_archive.py --root . --json`, and `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` passed in the feature worktree before commit. Local MR review remains the pre-integration gate after the feature commit is clean.
<!-- EVIDENCE_INDEX_END -->
