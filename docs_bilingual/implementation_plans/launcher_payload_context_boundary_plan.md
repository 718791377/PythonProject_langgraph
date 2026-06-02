---
doc_id: launcher_payload_context_boundary_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/launcher_payload_context_boundary_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 2
batch: 2
confirmation_required: true
---

# Launcher Payload Context Boundary Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Preserve short launcher payload boundaries while passing startup context through file-backed references rather than long inline strings.

## Source Plans

- codex_user_level_context_retention_canary_plan; user_level_launcher_payload_policy

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 2.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Stage: Phase 2 status reconciliation closed; the launcher payload context-boundary package is already integrated into local `main`.
Owner session: reconcile-context-retention-canary-status-20260602 (status-only reconciliation)
Current gate: no remaining local implementation gate for this child plan; remote publication remains unauthorized unless the user explicitly requests it.
Evidence: local `main` contains `6f1ef48`, and the current launcher payload context-boundary checker reports `ok: true` with one documented allowed warning about native-agent TOML fields.
Last updated: 2026-06-02
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/governance/user_level_launcher_payload_policy.md
- docs_bilingual/governance/user_level_launcher_payload_policy.zh-CN.md
- tools/*launcher*payload*
- test/*launcher_payload*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- user-level launcher generation logic if later confirmed
- startup summary references

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Inventory current launcher payload references without editing user-level config in this child-plan creation stage.
- [x] Add tests for file-backed instruction references and command-line length safety.
- [x] Update helper generation only after explicit child-plan confirmation.
- [x] Run launcher payload checker and local gate.
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
- 2026-06-02 status reconciliation: local `main` ancestry confirms `6f1ef48`; `python tools/check_launcher_payload_context_boundary.py --root . --json` reports `ok: true` with the documented native-agent TOML warning; previously unchecked backlog rows are now synchronized to the implemented-local evidence.
<!-- EVIDENCE_INDEX_END -->
