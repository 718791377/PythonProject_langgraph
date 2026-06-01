---
doc_id: user_level_browser_cli_adapter_boundary_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
source_plan: docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level Browser and CLI Adapter Boundary Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans`; use `superpowers:subagent-driven-development` only when the implementation slice has a disjoint write set. This child plan is extracted from the older MCP/skills/browser/CLI source plan and must be executed through normal claim, hotspot, and local-main retire gates.

## Goal

Keep chrome-devtools-mcp, CDP Bridge, OpenCLI, CLI-Anything, and `wecom-cli` as governed on-demand or reference adapters rather than competing governance layers.

## Source Extraction

Extracted from Slices 5 and 6 of `user_level_mcp_skills_browser_cli_governance_plan.md`.

This file is a decomposed child implementation plan under `multi_plan_parallel_session_orchestration_plan.md`. The source plan remains a historical and baseline-checker index; it is not the single execution package for this lane.

## Phase Placement

- Parent phase: Phase 6 subordinate adapter boundary.
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

Future implementation may touch adapter guard helpers, OpenCLI guard tests, CDP/chrome-devtools governance tests, WeCom guard helpers, and docs. It must not perform live GUI or browser mutation by default.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Adapter-specific work can run in parallel only with disjoint write sets. Live start, install, cookies, typing/clicking, JS execution, GUI write, and WeCom GUI automation remain blocked until receipt and owner evidence are merged.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [ ] Keep read-only tab inventory allowed without sensitive authorization.
- [ ] Require authorization receipt for click, type, navigate, JavaScript execution, cookie read, and raw browser data access.
- [ ] Require OpenCLI-style adapters to use `--port auto` and sanitized `codex-port` lease evidence.
- [ ] Keep CLI-Anything generation-first and block hard-loading skills until receipt plus smoke evidence exists.
- [ ] Keep `wecom-cli` API/Webhook-first and require global lease, operator confirmation, timeout release, and dry-run evidence for WXWork GUI dispatch.
- [ ] Report every adapter lane as `reference-only`, `planned`, `on-demand`, or `active-candidate` before integration.
- [ ] Run focused validation for this child lane.
- [ ] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
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
<!-- EVIDENCE_INDEX_END -->
