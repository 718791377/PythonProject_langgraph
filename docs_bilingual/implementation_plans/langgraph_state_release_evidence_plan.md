---
doc_id: langgraph_state_release_evidence_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/langgraph_state_release_evidence_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# LangGraph State Release Evidence Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Reject stale running LangGraph state after completed work and require explicit close, release, or handoff evidence.

## Source Plans

- automatic_orchestration_routing_enforcement_plan; codex_user_level_cross_session_durable_state_isolation_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R5 checker-backed active-candidate gate implemented locally; real sensitive live actions remain blocked unless a current lane receipt passes.
Stage: R5 runtime-governance receipt package for LangGraph state release evidence.
Owner session: `resume-019e8aa7-r5-runtime-governance-batch` in feature branch `implement-r5-runtime-governance-batch-20260607`.
Current gate: run focused tests, repository guard, precommit update/archive review, local CI, local MR review, then guarded local-main-first integration; remote publication remains unauthorized.
R5 evidence: `release-thread active-candidate receipt linkage and release projection evidence` is validated by `tools/check_r5_active_candidate_receipts.py` and the generic `tools/user_level_receipt_governance.py active-check` contract.
Runtime boundary: this R5 package validates fixture-backed receipts and checker wiring only; it does not install user-level tools, start browsers or GUI apps, send WXWork messages, launch durable workers, run live harness jobs, run Spec Kit live/apply modes, mutate user-level config, or mutate remote publication.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/langgraph_durable_orchestrator/*
- tools/check_durable_artifact_state_surfaces.py
- test/*langgraph*state*release*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- .omx/state/langgraph
- LangGraph compatibility records

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

## Real Runtime Implementation Gap

The earlier state-release runtime gap is closed by the Stage D/R4 package on this feature branch: the runtime now provides explicit close, release, and handoff receipts outside transient chat context. Until guarded local `main` integration finishes, treat the package as implemented and archived but still pending post-archive local gates.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for completed, running, released, and handoff LangGraph states.
- [x] Update durable state checker to flag stale running state after completion.
- [x] Document safe backend-family handoff requirements.
- [x] Run durable state and LangGraph checks plus local gate.
- [x] Stage D real runtime: implement LangGraph thread release helper that records thread id, backend family, previous state, release action, survivor queue, and handoff target.
- [x] Stage D real runtime: implement close/handoff receipts that prevent stale running state after completed work.
- [x] Stage D real runtime: add rollback/restore evidence for release mistakes without switching backend families implicitly.
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
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for LangGraph state release evidence. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-05 Stage D/R4 runtime implementation: branch `implement-langgraph-state-release-r4-20260605` adds `release-thread` for `close`, `release`, and `handoff`, persists receipts under `.omx/state/langgraph/store/releases/`, exposes release projections in status/inspect/backend records, adds runtime release-helper coverage to `test/check_langgraph_state_release_evidence.test.py`, and preserves rollback/restore and timeout release evidence without implicitly switching backend families. Targeted validation: `python test\check_langgraph_state_release_evidence.test.py` and `python tools\check_durable_artifact_state_surfaces.py --root . --json`.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for LangGraph thread release and handoff helpers; this package updates plan governance only and does not run live runtime.
- 2026-05-31 local-main status sync: recorded that the Stage C implementation is merged into local `main` at `32a5cfff3b977ba13ed6e215b4efb887679019b9`, the completed claim is preserved at `.omx/session-claims/completed/implement-langgraph-state-release-evidence-20260530.json`, and the remaining gate is explicit remote-publication approval.
- 2026-05-30 Stage C implementation: branch `implement-langgraph-state-release-evidence-20260530` added structured LangGraph state-release fixtures, extended `tools/check_durable_artifact_state_surfaces.py` to reject completed `running` state and missing release/handoff fields, registered `test/check_langgraph_state_release_evidence.test.py`, documented backend-family handoff requirements, and was integrated into local `main` at `32a5cfff3b977ba13ed6e215b4efb887679019b9`.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
