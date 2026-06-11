---
doc_id: durable_capability_readiness_projection_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/durable_capability_readiness_projection_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Durable Capability Readiness Projection Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Project durable lane state as installed, enabled, selected, and ready without collapsing those states.

## Source Plans

- codex_user_level_cross_session_durable_state_isolation_plan; automatic_orchestration_routing_enforcement_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 3.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for durable capability readiness projection.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `durable-capability-readiness-projection`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with already accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_capability_switch_chain.py
- tools/check_effective_lane_fit_evidence.py
- docs_bilingual/governance/langgraph_user_level_runtime_policy.md
- test/*capability*readiness*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- capability switch state schema
- LangGraph readiness evidence

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

## Runtime Refresh Scope

Stage D/R4 implements explicit readiness projection refresh through `codex-durable-state-status.ps1 -RefreshReadiness`. The default status path remains read-only. Refresh receipts preserve installed/enabled/selected/ready as distinct fields and may be extended later with deeper source evidence without collapsing readiness states.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for installed-only, enabled-not-selected, selected-not-ready, and ready states.
- [x] Update evidence checks to require distinct state fields.
- [x] Document user-facing wording for backend_default and backend_ready.
- [x] Run capability switch and effective-lane checks plus local gate.
- [x] Stage D real runtime: implement readiness probe helper that refreshes installed, enabled, selected, and ready for native_omx and LangGraph without collapsing states.
- [x] Stage D real runtime: record probe source, timestamp, backend family, selector evidence, version evidence, and blockers in sanitized projection receipts.
- [x] Stage D real runtime: wire projection refresh into activation evidence without claiming durable workflow adoption or persistent-team launch.
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
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for durable capability readiness projection. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-06 Stage D/R4 runtime refresh: branch `implement-durable-capability-readiness-r4-20260605` adds explicit `codex-durable-state-status.ps1 -RefreshReadiness -Json` receipt generation at `.omx/state/readiness/durable-capability-readiness-projection.json`, preserves distinct readiness fields and source/selector/version/blocker evidence, and records `durable_workflow_adopted=false` plus `persistent_team_launched=false`; targeted evidence: `python .\test\check_capability_switch_chain.test.py` and `powershell -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1` passed on 2026-06-06.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for installed/enabled/selected/ready probe refresh; this package updates plan governance only and does not run live runtime.
- 2026-05-30 Stage C implementation: `tools/check_capability_switch_chain.py` now validates durable capability readiness projections with distinct `installed`, `enabled`, `selected`, and `ready` fields, including the invariant `ready == installed && enabled && selected`.
- 2026-05-30 Stage C fixtures: `test/check_capability_switch_chain.test.py` covers installed-only, enabled-not-selected, selected-not-ready, ready, collapsed-ready, and missing-field readiness states.
- 2026-05-30 Stage C documentation: `docs_bilingual/governance/langgraph_user_level_runtime_policy.md` and `.zh-CN.md` document `backend_default` / `backend_ready` wording and clarify that readiness does not imply an adopted durable workflow, tracked thread, or persistent team.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
