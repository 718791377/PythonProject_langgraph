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
Status: implemented-local; remote publication remains unauthorized.
Current gate: local validation evidence is bound to branch `implement-mcp-skills-discovery-facade-20260601`; after serial local-main integration, only the remote-publication approval gate remains.
Source relation: extracted from `user_level_mcp_skills_browser_cli_governance_plan.md`; the source plan remains a baseline/history index, not a direct child execution package.
Runtime boundary: the implementation only adds/extends repo-local compact discovery facades and tests; it does not install tools, start browsers, invoke live MCP servers, mutate user-level runtime state, or authorize remote publication.
Implementation evidence: `skills2cli` now emits compact index/search/show/audit/profile-suggest JSON with routing evidence that skill/profile surfaces are not native subagents; `mcp2cli` now emits compact list/search/show/risk-profile/call JSON, keeps Codex direct MCP entries direct, and fail-closes sensitive calls without receipt evidence.
<!-- CURRENT_STATUS_END -->

## File Ownership

Future implementation may touch skills facade helpers, MCP facade helpers, risk-profile fixtures, tests, and policy docs. It must not load full skill bodies by default.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Can run in parallel with receipt and port plans because default discovery is read-only. Any real MCP call behavior depends on the Phase 1 receipt/redaction contract.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Define compact `skills2cli` index, search, show, audit, and profile-suggest JSON outputs.
- [x] Keep full skill bodies out of default output and summarize warning audits with redaction.
- [x] Define compact `mcp2cli` list, search, show, and risk profile output.
- [x] Make `mcp2cli call` fail closed for sensitive calls without authorization receipt evidence.
- [x] Keep direct Codex MCP entries direct and do not use MCP Router as the default Codex bridge.
- [x] Record routing evidence so skills and profiles are not mislabeled as native subagents.
- [x] Run focused validation for this child lane.
- [x] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
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
- 2026-06-01: branch `implement-mcp-skills-discovery-facade-20260601` implements the compact discovery facade lane. Evidence includes `tools/skills2cli.py`, `tools/mcp2cli.py`, `tools/mcp2cli_allowed_profiles.json`, focused tests `test/skills2cli.test.py` and `test/mcp2cli.test.py`, RED/GREEN coverage for MCP risk-profile output and skill/profile routing evidence, and no live MCP/browser/user-level runtime mutation.
<!-- EVIDENCE_INDEX_END -->
