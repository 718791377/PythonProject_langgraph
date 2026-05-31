---
doc_id: session_replay_context_filtering_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/session_replay_context_filtering_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 2
batch: 2
confirmation_required: true
---

# Session Replay Context Filtering Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Filter resumed session context so stale canary text, mojibake, and legacy runtime assumptions do not re-enter prompts as current authority.

## Source Plans

- codex_user_level_context_retention_canary_plan; automatic_orchestration_routing_enforcement_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 2.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage C implementation package
Owner session: implement-session-replay-context-filtering-20260530
Current gate: local validation and local main integration in progress
Stage C entry condition: satisfied by the 2026-05-30 user request to continue, commit locally, and merge into local main
Last updated: 2026-05-30
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/*session*replay*
- tools/check_context_retention_canary_surface.py
- docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
- test/*session_replay*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- startup instruction rendering
- legacy-session compatibility wording

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Define replay filtering inputs and outputs for resumed legacy sessions.
- [x] Add tests for stale canary, mojibake, and stale MCP assumptions.
- [x] Implement or update filtering helper/checker boundaries.
- [x] Run context canary, mojibake, and local gate checks.
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
- 2026-05-30 Stage C implementation: added `tools/session_replay_context_filtering.py`, replay-filtering tests, CI manifest registration, and governance contract text; local validation evidence is kept in command output and git history.
- 2026-05-30 Local validation: `tools/session_replay_context_filtering.py`, context-retention canary, startup mojibake, replay-filtering tests, and `tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` passed before commit.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
