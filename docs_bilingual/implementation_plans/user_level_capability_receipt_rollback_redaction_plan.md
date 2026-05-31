---
doc_id: user_level_capability_receipt_rollback_redaction_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_capability_receipt_rollback_redaction_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level Capability Receipt, Rollback, and Redaction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only when the implementation slice has a disjoint write set. This child plan is extracted from the older MCP/skills/browser/CLI source plan and must be executed through normal claim, hotspot, and local-main retire gates.

## Goal

Provide the shared authorization receipt, update receipt, rollback pointer, and redaction contract before any user-level MCP, browser, or CLI harness lane can become an active runtime surface.

## Source Extraction

Extracted from Slice 7 plus the sensitive-lane gates in Slices 2, 5, and 6 of `user_level_mcp_skills_browser_cli_governance_plan.md`.

This file is a decomposed child implementation plan under `multi_plan_parallel_session_orchestration_plan.md`. The source plan remains a historical and baseline-checker index; it is not the single execution package for this lane.

## Phase Placement

- Parent phase: Phase 1 construction safety base.
- Execution model: as-needed multi-phase work, with parallel sessions only when write sets are disjoint or hotspots are explicitly serialized.
- Remote publication: not authorized by this plan.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active and unclaimed for implementation.
Current gate: child-plan confirmation, clean feature worktree, branch-matching claim, and hotspot declaration before any non-document implementation.
Source relation: extracted from `user_level_mcp_skills_browser_cli_governance_plan.md`; do not add the source plan as a direct child of the parent.
Runtime boundary: this plan creation does not install tools, start browsers, call sensitive MCP methods, or mutate user-level runtime state.
<!-- CURRENT_STATUS_END -->

## File Ownership

Future implementation may touch `tools/user_level_receipt_governance.py`, receipt/redaction tests, OpenSpec deltas, and user-level governance docs. This plan creation changes documentation only.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Can run in parallel with port/browser-owner and discovery-facade work while it only edits this plan, specs, or tests. If it edits shared receipt helpers, it owns that hotspot and adapter plans must consume the merged contract afterward.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [ ] Freeze the minimal authorization receipt fields: action, target, scope, expiry, session, and operator confirmation.
- [ ] Freeze the update receipt fields for tool name, installed version, source URL, install path, wrapper path, state path, smoke test command, updater command, rollback pointer, owner lane, and redaction status.
- [ ] Keep raw secrets, cookies, tokens, browser data, message contents, and plugin description dumps out of stored receipts.
- [ ] Define rollback pointer output as hash-first by default, with raw paths visible only in local evidence under explicit authorization.
- [ ] Register any checker or CI changes in the shared guard if implementation later changes runtime or tests.
- [ ] Hand Phase 6 adapter plans the merged receipt contract before any live install, live start, GUI write, cookie read, or sensitive MCP call is allowed.
- [ ] Run focused validation for this child lane.
- [ ] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- OpenSpec aggregate guard: `python tools/run_openspec_guard.py --root . --json` verifies official workflow, document policy, and name clarity rules.
- Pre-commit update/archive review: `python tools/check_precommit_update_archive.py --root . --json` verifies required related-file updates and archive state.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.

## Acceptance Criteria

- The lane keeps discovery, receipts, leases, or adapters separate according to its phase boundary.
- No sensitive runtime action is enabled without the required receipt, owner, rollback, and redaction evidence.
- Any checker, test, or OpenSpec change is registered in the shared guard before local main integration.
- Local main integration remains serial and remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: child plan created by the MCP/skills/browser/CLI decomposition package; implementation evidence is pending future claims.
<!-- EVIDENCE_INDEX_END -->
