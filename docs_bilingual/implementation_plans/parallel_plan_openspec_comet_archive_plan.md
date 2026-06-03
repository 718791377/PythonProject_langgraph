---
doc_id: parallel_plan_openspec_comet_archive_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/parallel_plan_openspec_comet_archive_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 7
batch: 5
confirmation_required: true
---

# Parallel Plan OpenSpec Comet Archive Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Validate OpenSpec and Comet guard health and archive completed changes as one serial integration package when appropriate.

## Source Plans

- multi_plan_parallel_session_orchestration_plan; comet_runtime_agile_focus_area_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 5.
- Phase: Phase 7.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: archive package implemented locally; local `main` integration is handled by this package's complete local flow
Stage: Stage C Phase 7 OpenSpec/Comet archive package
Owner session: `codex-20260603-parallel-plan-openspec-comet-archive`
Current gate: local-main integration through `tools/complete_local_flow_to_remote_gate.py`; after local integration, stop at the remote-publication approval gate
Stage C entry condition: satisfied; the user confirmed this child implementation plan and requested local commit plus local `main` integration on 2026-06-03
Last updated: 2026-06-03
Status update: `refactor-user-level-mcp-governance-modern-structure` is archived to `openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure/`. Stable-spec sync is intentionally skipped because the current stable MCP/skills/browser/CLI specification already carries broader current coverage; overwriting it with the older narrow delta would regress stable coverage. Remaining complete active changes are deferred to later archive packages because their verify, branch-handling, source-plan, or archive-readiness evidence is not owned by this single serial archive package.
<!-- CURRENT_STATUS_END -->

## File Ownership

- openspec/changes/*
- openspec/specs/*
- docs/superpowers/*
- tools/run_openspec_guard.py

## Hotspot Serialization

Only one session may own each hotspot at a time:

- OpenSpec stable specs
- openspec archive directories

## Parallel Session Contract

- Maximum parallel sessions for this phase: 1.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration; the current user request is the implementation confirmation for this child plan.
- [x] Identify completed active OpenSpec changes that must archive before final integration; selected the eligible completed `refactor-user-level-mcp-governance-modern-structure` change.
- [x] Run official OpenSpec verification and Comet guard checks for the selected archive package.
- [x] Promote stable spec deltas only after implementation validation is complete; stable-spec sync is skipped because existing stable coverage is broader than the historical delta.
- [x] Run archive validation and local gate before local `main` integration.
- [x] Before archiving MCP/skills/browser/CLI OpenSpec work, record whether each extracted child lane is implemented, deferred, or still active. Receipt/redaction, port/browser-owner, discovery facade, and browser/CLI adapter boundary lane states are implemented-local; the broader source surface is partially archived by `refactor-user-level-mcp-governance-modern-structure`, while remaining complete active changes stay deferred for later evidence-owned archive packages.
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
- 2026-06-03 Phase 7 archive implementation: archived `refactor-user-level-mcp-governance-modern-structure` to `openspec/changes/archive/2026-06-03-refactor-user-level-mcp-governance-modern-structure/`; stable-spec sync was skipped to avoid replacing broader current stable MCP/skills/browser/CLI coverage with the older narrow delta; remaining complete active changes are deferred because their verify/branch/archive evidence is outside this package's write ownership.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-06-01 receipt/redaction archive note: `user_level_capability_receipt_rollback_redaction_plan` is implemented-local; no live user-level install or sensitive runtime action was performed, and the related stable spec already contains the generic receipt governance requirement. Archive timing remains a Phase 7 decision for the broader MCP/skills/browser/CLI source surface.
- 2026-06-01 port/browser-owner archive note: `user_level_port_browser_owner_isolation_plan` is implemented-local; the package hardens repository-local guards and tests only, performs no live browser start or sensitive runtime action, and leaves archive timing as a Phase 7 decision for the broader MCP/skills/browser/CLI source surface.
- 2026-06-01 discovery facade archive note: `user_level_mcp_skills_discovery_facade_plan` is implemented-local; it changes repo-local facade helpers/tests only, performs no live MCP/browser/runtime action, and leaves broader source-surface archive timing to Phase 7.
- 2026-06-01 browser/CLI adapter boundary archive note: `user_level_browser_cli_adapter_boundary_plan` is implemented-local; it changes repo-local checker/plan evidence only, performs no live browser start, GUI automation, install, cookie read, or sensitive runtime action, and leaves broader source-surface archive timing to a future Phase 7 archive package.
<!-- EVIDENCE_INDEX_END -->
