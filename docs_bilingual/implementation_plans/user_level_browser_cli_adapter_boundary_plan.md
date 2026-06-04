---
doc_id: user_level_browser_cli_adapter_boundary_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# User-Level Browser and CLI Adapter Boundary Plan

> **For agentic workers:** use `superpowers:executing-plans`; use parallel subagents only for disjoint write sets. This child plan owns Browser/CLI adapters only. CLI-Anything/WXWork_CLI and Codex harnesses are sibling plans, not adapter lanes.

## Goal

Keep the Browser/CLI adapter lane limited to `chrome-devtools-mcp`, `cdp-bridge-mcp` / `CDP Bridge`, and `OpenCLI`. These adapters are not Codex harnesses, and this plan does not own CLI-Anything, WXWork_CLI, WXWork.exe, Pi, or oh-my-pi.

## Architecture

Project-level governance first: browser owner leases, port leases, isolated profile rules, sensitive-action authorization, redaction, and dry-run/live-start gates are validated in this repository before any user-level adapter wrapper is promoted. User-level governance follows only after install/update receipts, smoke evidence, rollback pointers, and owner evidence exist.

## Tech Stack

Python adapter guards, `codex-port`, browser owner registry, chrome-devtools-mcp reference source, cdp-bridge-mcp reference source, OpenCLI reference source, JSON receipts, OpenSpec, local tests, CI manifest, and optional user-level wrapper state under `C:\Users\lenovo\.codex` after promotion.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; Stage B checker/test/spec migration is complete and remote publication remains closed.
Current gate: validate the new split adapter checker, focused adapter tests, precommit/archive review, OpenSpec guard, local gate, and local MR review before local `main` integration.
Canonical adapter set: exactly `chrome-devtools-mcp`, `cdp-bridge-mcp` / `CDP Bridge`, and `OpenCLI`.
Runtime boundary: this repo-local package does not install tools, start browsers, call sensitive MCP methods, read cookies, execute JavaScript, mutate browser/GUI state, or mutate user-level runtime state.
Implementation evidence: `tools/check_user_level_browser_cli_adapter_boundary.py` rejects CLI-Anything, WXWork_CLI, WXWork.exe, wecom-cli, and harness wording in adapter lane tables; `test/check_user_level_browser_cli_adapter_boundary.test.py` and existing chrome/CDP/OpenCLI tests cover the lane.
<!-- CURRENT_STATUS_END -->

## Source References

| Adapter | Reference source | Update evidence required later |
| --- | --- | --- |
| chrome-devtools-mcp | https://github.com/ChromeDevTools/chrome-devtools-mcp | source URL, package/pin, install receipt, smoke, rollback pointer |
| cdp-bridge-mcp / CDP Bridge | https://github.com/Unagi-cq/cdp-bridge-mcp | source URL, pin, port/owner lease evidence, redaction evidence |
| OpenCLI | https://github.com/jackwener/OpenCLI | source URL, pin, `--port auto` evidence, owner lease, authorization receipt |

## Governance Level Split

| Stage | Governance level | Allowed work | Promotion gate |
| --- | --- | --- | --- |
| 0 | project-level | taxonomy, source references, no-harness boundary | docs/OpenSpec gate |
| 1 | project-level | adapter checkers/tests, owner/port lease checks, sensitive action fail-closed behavior | focused tests and local gate |
| 2 | reusable project-level | portable adapter guard contracts for other repos | checker-backed examples |
| 3 | user-level | wrapper install/update receipt, smoke, rollback plan | explicit authorization and passing project-level guard |
| 4 | user-level active-candidate | bounded adapter live start or action handoff | owner lease, authorization receipt, expiry, redaction, rollback evidence |

## File Ownership

This child plan owns Browser/CLI adapter docs, future adapter scope checker updates, chrome-devtools-mcp/CDP/OpenCLI guard tests, and source-reference checks. It does not own CLI-Anything, WXWork_CLI, enterprise WeChat, Pi, oh-my-pi, or Codex harnesses.

## Parallel Session Contract

One session may claim this implementation plan at a time. Other sessions may work on CLI-Anything/WXWork_CLI or Codex harnesses in parallel only when they do not edit this plan, its future checker/tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized hotspot lease.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Keep read-only tab inventory allowed without sensitive authorization where the specific guard allows it.
- [x] Require authorization receipt for click, type, navigate, JavaScript execution, cookie read, and raw browser data access.
- [x] Require OpenCLI-style adapters to use `--port auto` and sanitized `codex-port` lease evidence.
- [x] Stage A: record the canonical Browser/CLI adapter set and reference source links.
- [x] Stage A: state that CLI-Anything/WXWork_CLI and Codex harnesses are sibling plans, not adapters.
- [x] Stage B: replace the old mixed baseline checker with the split adapter checker.
- [x] Stage B: add negative coverage for CLI-Anything, WXWork_CLI, WXWork.exe, wecom-cli, and harness terms in adapter lane tables.
- [x] Stage B: update CI manifest, safety registry, and OpenSpec guard wiring.
<!-- TASK_BACKLOG_END -->

## Pending Stage B Migration Work

- Update adapter checker/tests so only the three canonical adapters are accepted.
- Add negative coverage for CLI-Anything, WXWork_CLI, WXWork.exe, wecom-cli, and harness wording in adapter lane tables.
- Update CI manifest, safety registry, and OpenSpec guard wiring.
- Remove temporary legacy compatibility markers after checker migration.


## Implemented Contract

- `tools/chrome_devtools_mcp_managed.py` keeps chrome-devtools-mcp on-demand: isolated-session and project-profile plans are dry-run, live start requires install receipt evidence, and the repo-local MVP still defers actual browser startup.
- `tools/cdp_bridge_governance.py` allows read-only tab inventory without sensitive authorization, but click, type, navigate, JavaScript execution, cookie read, raw browser data access, and unknown actions require owner evidence plus an authorization receipt and fail closed otherwise.
- `tools/opencli_governance.py` keeps OpenCLI on-demand, requires `--port auto`, validates sanitized `codex-port` lease evidence, requires owner evidence for target-bound actions, requires authorization receipts for sensitive actions, and defers live start even after install receipt evidence.
- Temporary migration note: `tools/cli_anything_governance.py` keeps CLI-Anything generation-first, blocks hard-load skills, and is moving to the CLI-Anything/WXWork_CLI child plan.
- Temporary migration note: `tools/wecom_cli_governance.py` previously kept `wecom-cli` API/Webhook-first with global lease, operator confirmation, timeout release, and dry-run evidence; Stage B will rename active surfaces to `WXWork_CLI` and move them to the CLI-Anything/WXWork_CLI child plan.

## Adapter lane status

| Adapter lane | Status | Repo-local evidence | Live/runtime boundary |
| --- | --- | --- | --- |
| chrome-devtools-mcp | on-demand | `tools/chrome_devtools_mcp_managed.py`, `test/chrome_devtools_mcp_managed.test.py` | No live browser start without install receipt and owner evidence; repo-local MVP still defers actual start. |
| CDP Bridge / cdp-bridge-mcp | on-demand | `tools/cdp_bridge_governance.py`, `test/cdp_bridge_governance.test.py` | Read-only tab inventory allowed; sensitive actions require owner lease plus authorization receipt. |
| OpenCLI | on-demand | `tools/opencli_governance.py`, OpenCLI coverage in `test/cdp_bridge_governance.test.py` | Requires `--port auto`, sanitized `codex-port` lease evidence, owner evidence, and receipt-gated sensitive actions. |

## Validation Gates

- Split checker: `python tools/check_user_level_browser_cli_adapter_boundary.py --root . --json` verifies the canonical adapter boundary.
- OpenSpec aggregate guard: `python tools/run_openspec_guard.py --root . --json` verifies official workflow, document policy, and name clarity rules.
- Whitespace check: `git diff --check` verifies the patch has no whitespace errors.

## Acceptance Criteria

- The canonical adapter set is exactly chrome-devtools-mcp, cdp-bridge-mcp / CDP Bridge, and OpenCLI.
- CLI-Anything/WXWork_CLI and Codex harnesses are referenced only as sibling plans or temporary migration inputs.
- No sensitive runtime action is enabled without receipt, owner, rollback, and redaction evidence.
- Local main integration remains serial and remote publication remains behind explicit approval.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-01: `user_level_browser_cli_adapter_boundary_plan` implementation evidence recorded branch `implement-user-level-browser-cli-adapter-boundary-20260601` for the earlier mixed adapter package.
- 2026-06-04 Stage B implementation evidence: `tools/check_user_level_browser_cli_adapter_boundary.py` and `test/check_user_level_browser_cli_adapter_boundary.test.py` enforce the three-adapter boundary and reject sibling-lane terms in adapter tables.
<!-- EVIDENCE_INDEX_END -->
