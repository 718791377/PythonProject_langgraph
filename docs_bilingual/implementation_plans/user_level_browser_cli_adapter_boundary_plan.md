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
Status: implemented-local; ready for repository local-main-first integration, with remote publication still closed.
Current gate: run focused adapter-governance validation, shared local gate, and local MR review; then self-retire this implementation package into local `main` and stop at the remote-publication approval gate.
Source relation: extracted from `user_level_mcp_skills_browser_cli_governance_plan.md`; do not add the source plan as a direct child of the parent.
Runtime boundary: this repo-local package does not install tools, start browsers, call sensitive MCP methods, read cookies, execute JavaScript, mutate browser/GUI state, or mutate user-level runtime state.
Implementation evidence: existing repo-local guards already keep chrome-devtools-mcp and OpenCLI as on-demand wrappers, CDP Bridge read-only by default, CLI-Anything generation-first/reference-only, and `wecom-cli` API/Webhook-first with GUI dry-run gates; this package makes that child-plan evidence checker-backed through `tools/check_user_level_mcp_skills_browser_cli_baseline.py`.
<!-- CURRENT_STATUS_END -->

## File Ownership

Future implementation may touch adapter guard helpers, OpenCLI guard tests, CDP/chrome-devtools governance tests, WeCom guard helpers, and docs. It must not perform live GUI or browser mutation by default.

A future implementation claim must list exact file ownership before edits. Workers are not alone in the codebase, must not revert other workers' changes, and must report changed paths.

## Parallel Session Contract

Adapter-specific work can run in parallel only with disjoint write sets. Live start, install, cookies, typing/clicking, JS execution, GUI write, and WeCom GUI automation remain blocked until receipt and owner evidence are merged.

Shared hotspots remain serialized through the parent plan, implementation-plan claim lock, ROB entry, and local-main retire lock.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Keep read-only tab inventory allowed without sensitive authorization.
- [x] Require authorization receipt for click, type, navigate, JavaScript execution, cookie read, and raw browser data access.
- [x] Require OpenCLI-style adapters to use `--port auto` and sanitized `codex-port` lease evidence.
- [x] Keep CLI-Anything generation-first and block hard-loading skills until receipt plus smoke evidence exists.
- [x] Keep `wecom-cli` API/Webhook-first and require global lease, operator confirmation, timeout release, and dry-run evidence for WXWork GUI dispatch.
- [x] Report every adapter lane as `reference-only`, `planned`, `on-demand`, or `active-candidate` before integration.
- [x] Run focused validation for this child lane.
- [x] Update the parent evidence index and Phase 7 integration plans after implementation evidence exists.
<!-- TASK_BACKLOG_END -->


## Implemented Contract

- `tools/chrome_devtools_mcp_managed.py` keeps chrome-devtools-mcp on-demand: isolated-session and project-profile plans are dry-run, live start requires install receipt evidence, and the repo-local MVP still defers actual browser startup.
- `tools/cdp_bridge_governance.py` allows read-only tab inventory without sensitive authorization, but click, type, navigate, JavaScript execution, cookie read, raw browser data access, and unknown actions require owner evidence plus an authorization receipt and fail closed otherwise.
- `tools/opencli_governance.py` keeps OpenCLI on-demand, requires `--port auto`, validates sanitized `codex-port` lease evidence, requires owner evidence for target-bound actions, requires authorization receipts for sensitive actions, and defers live start even after install receipt evidence.
- `tools/cli_anything_governance.py` keeps CLI-Anything generation-first/reference-only: pinned install/update receipts and rollback plans are evidence records only, hard-load skills is blocked, and harness generation remains separate from live control.
- `tools/wecom_cli_governance.py` keeps `wecom-cli` API/Webhook-first: GUI dispatch remains dry-run only and requires global lease, operator confirmation, timeout release, rollback pointer, and no message-content evidence before any future live handoff.
- `tools/check_user_level_mcp_skills_browser_cli_baseline.py` now validates this extracted child plan's implemented-local status, closed backlog, adapter lane status, and evidence markers so the boundary is not only prompt text.

## Adapter lane status

| Adapter lane | Status | Repo-local evidence | Live/runtime boundary |
| --- | --- | --- | --- |
| chrome-devtools-mcp | on-demand | `tools/chrome_devtools_mcp_managed.py`, `test/chrome_devtools_mcp_managed.test.py` | No live browser start without install receipt and owner evidence; repo-local MVP still defers actual start. |
| CDP Bridge | on-demand | `tools/cdp_bridge_governance.py`, `test/cdp_bridge_governance.test.py` | Read-only tab inventory allowed; sensitive actions require owner lease plus authorization receipt. |
| OpenCLI | on-demand | `tools/opencli_governance.py`, OpenCLI coverage in `test/cdp_bridge_governance.test.py` | Requires `--port auto`, sanitized `codex-port` lease evidence, owner evidence, and receipt-gated sensitive actions. |
| CLI-Anything | reference-only | `tools/cli_anything_governance.py`, CLI-Anything coverage in `test/cdp_bridge_governance.test.py` | Generation-first only; hard-load skills and live control remain blocked without receipt plus smoke evidence. |
| wecom-cli | on-demand | `tools/wecom_cli_governance.py`, `test/wecom_cli_governance.test.py` | API/Webhook-first; WXWork GUI dispatch is dry-run only and requires global lease, operator confirmation, timeout release, and rollback evidence. |

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
- 2026-06-01: `user_level_browser_cli_adapter_boundary_plan` implementation evidence records branch `implement-user-level-browser-cli-adapter-boundary-20260601`; it closes the adapter boundary backlog, keeps all live browser/GUI/install/cookie/runtime mutation out of scope, checker-backs adapter lane status in `tools/check_user_level_mcp_skills_browser_cli_baseline.py`, and relies on focused coverage for chrome-devtools-mcp, CDP Bridge, OpenCLI, CLI-Anything, `wecom-cli`, and receipt/lease guards.
<!-- EVIDENCE_INDEX_END -->
