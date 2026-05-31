---
doc_id: prompt_independent_activation_parity_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/prompt_independent_activation_parity_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 4
batch: 3
confirmation_required: true
---

# Prompt Independent Activation Parity Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Ensure automatic collaboration routing does not depend on the user saying parallel, experts, subagents, OMX, or LangGraph.

## Source Plans

- automatic_orchestration_routing_enforcement_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 3.
- Phase: Phase 4.
- Status: implementation has been confirmed, completed through checker, fixture, documentation, and CI-manifest updates on local `main`, and this file now records the closeout package.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented, locally validated, and merged into local `main`
Stage: Stage C closeout package locally integrated
Owner session: `codex-close-prompt-independent-activation-parity-20260531`
Current gate: remote-publication approval gate; remote publication remains out of scope and unauthorized
Stage C entry condition: satisfied on 2026-05-30 after user confirmation
Local main integration: implementation commit `453dba4` and closeout commit `517d816` are preserved in current local `main`
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/check_role_routing_directive_evidence.py
- tools/check_orchestration_collaboration_evidenceguard.py
- test/*prompt_independent*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- activation policy docs
- role routing checker

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for qualified tasks with and without user collaboration keywords.
- [x] Require concrete blockers instead of missing-user-reminder excuses.
- [x] Update checker messages and policy docs.
- [x] Run role routing and orchestration evidence checks plus local gate.
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
- 2026-05-31 Phase 4 final closeout: `close-phase4-final-20260531` confirms this child plan has no open checklist items, its implementation and closeout evidence are preserved in current local `main`, and its remaining gate is explicit remote-publication approval.
- 2026-05-31 Stage C closeout: branch `close-prompt-independent-activation-parity-20260531` records that prompt-independent activation parity is implemented through the role-routing checker, collaboration evidence guard, prompt-independent fixtures, activation-policy documentation, CI manifest registration, and local validation gates; final local-main commit is recorded in the assistant response and local git history.
- 2026-05-30 Stage C implementation: added qualified prompt-independent parity fixtures, missing-reminder negative fixture handling, role evidence rejection, policy doc notes, and CI manifest registration; final validation evidence is recorded in local gate and commit output.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
