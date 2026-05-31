---
doc_id: role_routing_fanout_write_ownership_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/role_routing_fanout_write_ownership_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Role Routing Fanout Write Ownership Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Enforce smallest-sufficient expert roles, analyst-only first fan-out for bounded multi-face research, and explicit write ownership for parallel code-changing agents.

## Source Plans

- automatic_orchestration_routing_enforcement_plan; codex_governance_session_visibility_and_plan_lock_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented, locally validated, and merged into local `main`
Stage: Stage C local implementation package
Owner session: `main-codex-leader-role-routing-fanout-write-ownership-20260530`
Current gate: remote-publication approval gate; remote publication remains out of scope and unauthorized
Stage C entry condition: satisfied by user confirmation to continue this child implementation plan
Local main integration: local closeout commit `eeccff9` is preserved in current local `main`
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_role_routing_directive_evidence.py
- tools/check_fanout_write_ownership_evidence.py
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
- test/*fanout*ownership*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- role routing evidence
- fan-out ownership evidence

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for analyst-first research, over-broad role sets, and write-heavy fan-out with missing ownership.
- [x] Update checkers to reject unowned write scopes and hotspot collisions.
- [x] Document leader-owned fan-in and changed-path reporting.
- [x] Run role routing, fan-out ownership, and local gate checks.
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
- 2026-05-31 Phase 4 final closeout: `close-phase4-final-20260531` confirms this child plan has no open checklist items, its closeout evidence is preserved in current local `main`, and its remaining gate is explicit remote-publication approval.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-14 role routing implementation evidence: commit `1a45e87` added `tools/check_role_routing_directive_evidence.py` and `test/check_role_routing_directive_evidence.test.py`; commit `4814802` archived the OpenSpec change and promoted the stable spec requirements.
- 2026-05-14 fan-out/write-ownership implementation evidence: commit `1902d35` added `tools/check_fanout_write_ownership_evidence.py` and `test/check_fanout_write_ownership_evidence.test.py`; commit `43b4500` archived the OpenSpec change and kept the stable spec aligned.
- 2026-05-30 Stage C local closure package: session `main-codex-leader-role-routing-fanout-write-ownership-20260530` recorded claim/receipt/ROB metadata before writing, confirmed existing repository checks pass for role-routing and fan-out/write-ownership surfaces, and limits this package to plan closure before local `main` integration.
<!-- EVIDENCE_INDEX_END -->
