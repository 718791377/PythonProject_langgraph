---
doc_id: user_level_mcp_skills_discovery_facade_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_mcp_skills_discovery_facade_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level MCP and Skills Discovery Facade Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only when the implementation slice has a disjoint write set. This child plan is extracted from the older MCP/skills/browser/CLI source plan and must be executed through normal claim, hotspot, and local-main retire gates.

## Goal

Provide compact `skills2cli` and `mcp2cli` discovery contracts that reduce startup context and keep sensitive calls risk-gated.

## Source Extraction

Extracted from Slices 1 and 2 of `user_level_mcp_skills_browser_cli_governance_plan.md`.

This file is a decomposed child implementation plan under `multi_plan_parallel_session_orchestration_plan.md`. The source plan remains a historical and baseline-checker index; it is not the single execution package for this lane.

## Phase Placement

- Parent phase: Phase 4 automatic routing and stable session surfaces.
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

Future implementation may touch skills facade helpers, MCP facade helpers, risk-profile fixtures, tests, and policy docs. It must not load full skill bodies by default.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Can run in parallel with receipt and port plans because default discovery is read-only. Any real MCP call behavior depends on the Phase 1 receipt/redaction contract.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [ ] Define compact `skills2cli` index, search, show, audit, and profile-suggest JSON outputs.
- [ ] Keep full skill bodies out of default output and summarize warning audits with redaction.
- [ ] Define compact `mcp2cli` list, search, show, and risk profile output.
- [ ] Make `mcp2cli call` fail closed for sensitive calls without authorization receipt evidence.
- [ ] Keep direct Codex MCP entries direct and do not use MCP Router as the default Codex bridge.
- [ ] Record routing evidence so skills and profiles are not mislabeled as native subagents.
- [ ] Run focused validation for this child lane.
- [ ] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- MCP baseline checker: `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` verifies source-plan baseline markers and guard registration.
- Agent/skill/profile boundary checker: `python tools/check_agent_skill_profile_surface_boundaries.py --root . --json` verifies skills are not mislabeled as native agents.
- MCP scope checker: `python tools/check_mcp_router_scope_policy.py --root . --json` verifies Codex direct MCP boundaries and Router isolation.
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
