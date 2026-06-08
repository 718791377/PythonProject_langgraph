---
doc_id: parallel_plan_docs_registry_integration_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/parallel_plan_docs_registry_integration_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 7
batch: 5
confirmation_required: true
---

# Parallel Plan Docs Registry Integration Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Validate docs registry, bilingual pairs, active statuses, anchors, and evidence-index references across all parallel child plans.

## Source Plans

- multi_plan_parallel_session_orchestration_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 5.
- Phase: Phase 7.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; ready for validation, local commit, and local-main integration
Stage: Stage C implementation package for docs-registry integration
Owner session: codex-parallel-plan-docs-registry-integration-20260603
Current gate: run focused implementation-plan tests, implementation-plan rules checker, precommit/archive review, receipt checker, shared local gate, and local MR review before local `main` integration
Stage C entry condition: satisfied by the 2026-06-03 user request to continue this confirmed child implementation plan
Last updated: 2026-06-03
Status update: The extracted MCP/skills/browser/CLI child plans are already registered in `docs_bilingual/docs_registry.yaml`; this package adds checker-backed parent/source child-plan group reporting, bilingual `parent_plan`/`source_plan` companion consistency validation, implemented-child lightweight evidence-index validation, and UTF-8-safe checker output for Windows subprocess capture. No docs-registry schema change is required.
<!-- CURRENT_STATUS_END -->

## File Ownership

- docs_bilingual/docs_registry.yaml
- tools/check_implementation_plan_rules.py
- tools/implementation_plan_size_baseline.json
- test/*implementation_plan*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- docs_bilingual/docs_registry.yaml

## Parallel Session Contract

- Maximum parallel sessions for this phase: 1.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add integration fixtures for all child plan registry entries.
- [x] Run and, if needed, harden implementation-plan rules for bilingual pair consistency.
- [x] Ensure completed child plans record lightweight evidence indexes instead of large evidence packages.
- [x] Run implementation-plan checker and local gate.
- [x] Include extracted MCP/skills/browser/CLI child plans in docs registry and bilingual implementation-plan rule validation.
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
- 2026-06-03 registry/checker implementation: branch `implement-parallel-plan-docs-registry-integration-20260603` adds focused RED/GREEN fixtures for parent/source child-plan registry groups, bilingual source/parent companion consistency, and implemented-child lightweight evidence-index requirements; `tools/check_implementation_plan_rules.py --root . --json` now reports 43 registered child-plan links, a 39-child parent group for `multi_plan_parallel_session_orchestration_plan`, and a 4-child source group for `user_level_mcp_skills_browser_cli_governance_plan`, with zero errors before final local gates.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-06-01 port/browser-owner registry handoff: `user_level_port_browser_owner_isolation_plan` is implemented-local; its bilingual docs-registry entry already exists, the plan/status/evidence anchors are updated in place, and no docs-registry schema change is required for the local integration package.
- 2026-06-01 discovery facade lane handoff: `user_level_mcp_skills_discovery_facade_plan` is implemented-local; its bilingual docs-registry entries already exist, so this package updates status/evidence anchors without changing registry schema.
- 2026-06-01 browser/CLI adapter boundary handoff: `user_level_browser_cli_adapter_boundary_plan` is implemented-local; its bilingual docs-registry entry already exists, so this package updates status/evidence anchors without changing registry schema.
<!-- EVIDENCE_INDEX_END -->
