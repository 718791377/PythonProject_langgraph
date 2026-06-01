---
doc_id: user_level_port_browser_owner_isolation_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_port_browser_owner_isolation_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level Port and Browser Owner Isolation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only when the implementation slice has a disjoint write set. This child plan is extracted from the older MCP/skills/browser/CLI source plan and must be executed through normal claim, hotspot, and local-main retire gates.

## Goal

Make `codex-port` leases, `pending_bind`, `registry_revision`, and the browser owner registry safe across sessions, worktrees, and consumer projects.

## Source Extraction

Extracted from Slices 3 and 4 plus OpenCLI lease requirements from Slice 5 of `user_level_mcp_skills_browser_cli_governance_plan.md`.

This file is a decomposed child implementation plan under `multi_plan_parallel_session_orchestration_plan.md`. The source plan remains a historical and baseline-checker index; it is not the single execution package for this lane.

## Phase Placement

- Parent phase: Phase 3 durable state and cross-session isolation.
- Execution model: as-needed multi-phase work, with parallel sessions only when write sets are disjoint or hotspots are explicitly serialized.
- Remote publication: not authorized by this plan.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; ready for repository local-main-first integration.
Current gate: run focused tests, repository checkers, shared local gate, and local MR review; then self-retire this ready package into local `main` and stop at the remote-publication approval gate.
Source relation: extracted from `user_level_mcp_skills_browser_cli_governance_plan.md`; do not add the source plan as a direct child of the parent.
Runtime boundary: this repository-local safety hardening does not install tools, start browsers, call sensitive MCP methods, mutate user-level runtime state, or authorize remote publication.
Implementation evidence: existing `codex-port` and browser-owner registry helpers already cover range ordering, `--port auto`, atomic writes, `pending_bind`, monotonic revision, owner classes, cleanup protection, and sanitized receipts; this package adds fail-closed ambiguous-owner rejection in CDP Bridge and OpenCLI consumer guards with RED/GREEN regression coverage.
<!-- CURRENT_STATUS_END -->

## File Ownership

Future implementation may touch port allocator helpers, browser owner registry helpers, fixtures, tests, and policy docs. It must not touch human-owned browser data.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Can run in parallel with the receipt and discovery plans when it owns only port/browser-owner files. Any shared state path or cleanup behavior must be serialized with durable-state isolation work.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Keep Codex user-level port ranges before downstream consumer project ranges and require `--port auto` for OpenCLI-style adapters.
- [x] Define atomic registry writes for `codex-port`, including recoverable `pending_bind` and monotonic `registry_revision`.
- [x] Separate isolated-session-managed, project-profile, and human-owned browser assets in the owner registry.
- [x] Require exactly one owner for an automated browser target and fail closed on ambiguous ownership.
- [x] Block automated cleanup of project-profile and human-owned browser assets unless a later plan supplies explicit authorization evidence.
- [x] Expose sanitized lease evidence for Phase 6 adapter plans without leaking cookies, tokens, or raw browser data.
- [x] Run focused validation for this child lane.
- [x] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- MCP scope checker: `python tools/check_mcp_router_scope_policy.py --root . --json` verifies Codex direct MCP boundaries and Router isolation.
- OpenSpec aggregate guard: `python tools/run_openspec_guard.py --root . --json` verifies official workflow, document policy, and name clarity rules.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.

## Acceptance Criteria

- The lane keeps discovery, receipts, leases, or adapters separate according to its phase boundary.
- No sensitive runtime action is enabled without the required receipt, owner, rollback, and redaction evidence.
- Any checker, test, or OpenSpec change is registered in the shared guard before local main integration.
- Local main integration remains serial and remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: child plan created by the MCP/skills/browser/CLI decomposition package; implementation evidence is pending future claims.
- 2026-06-01: branch `implement-port-browser-owner-isolation-20260601` confirms the existing `codex-port`, browser-owner registry, and OpenCLI `--port auto` controls, adds `owner_lease_ambiguous` fail-closed enforcement to CDP Bridge and OpenCLI consumers, adds RED/GREEN regression coverage in `test/cdp_bridge_governance.test.py`, updates the parent and Phase 7 handoff indexes, and remains local-only pending repository gates and local-main integration.
<!-- EVIDENCE_INDEX_END -->
