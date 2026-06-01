---
doc_id: parallel_plan_checker_ci_integration_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/parallel_plan_checker_ci_integration_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 7
batch: 5
confirmation_required: true
---

# Parallel Plan Checker CI Integration Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Ensure every new checker, test, and helper introduced by child plans is registered in local and mirrored CI gates.

## Source Plans

- multi_plan_parallel_session_orchestration_plan; automatic_orchestration_routing_enforcement_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 5.
- Phase: Phase 7.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active
Stage: Stage B child-plan creation package
Owner session: unclaimed until implementation begins
Current gate: wait for explicit user confirmation of this child plan before non-document implementation
Stage C entry condition: user confirms this child implementation plan after local main integration
Last updated: 2026-05-28
Status update: MCP/skills/browser/CLI decomposition keeps the baseline checker as a required guard. The receipt/redaction lane and port/browser-owner lane helper/test coverage are registered in the CI manifest and OpenSpec aggregate guard; other extracted sibling lanes still need registration review if they change runtime behavior.
<!-- CURRENT_STATUS_END -->

## File Ownership

- tools/ci/local_gate.ps1
- tools/ci/local_mr_review.ps1
- tools/check_local_mirrored_ci_gate.py
- test/*ci*integration*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- local gate script
- CI manifest or workflow config

## Parallel Session Contract

- Maximum parallel sessions for this phase: 1.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [ ] Confirm this child plan after local main integration.
- [ ] Inventory new checkers and tests from completed child plans.
- [ ] Add missing local gate registrations and mirrored CI checks.
- [ ] Detect divergence between local and remote CI command sequences.
- [ ] Run local gate and local MR review.
- [x] Verify MCP baseline, receipt/redaction, browser-owner, MCP/skills discovery, and adapter guard checks are registered when their extracted lanes change runtime behavior.
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
- 2026-06-01 receipt/redaction lane handoff: `user_level_capability_receipt_rollback_redaction_plan` confirms `tools/user_level_receipt_governance.py`, `test/user_level_receipt_governance.test.py`, the MCP baseline checker, OpenSpec guard registration, and `tools/ci/ci_test_manifest.json` coverage for the receipt lane; future sibling lane changes still need their own registration review.
- 2026-06-01 port/browser-owner lane handoff: `user_level_port_browser_owner_isolation_plan` confirms existing CI-manifest registration for `test/codex_port.test.py`, `test/browser_owner_registry.test.py`, `test/cdp_bridge_governance.test.py`, and `test/chrome_devtools_mcp_managed.test.py`; the CDP/OpenCLI ambiguity regression coverage extends an already registered test file, so no CI-manifest edit is required.
<!-- EVIDENCE_INDEX_END -->
