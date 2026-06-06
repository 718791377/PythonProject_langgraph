---
doc_id: user_level_cli_anything_wxwork_cli_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/user_level_cli_anything_wxwork_cli_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
supersedes:
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
  - docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md
---

# User-Level CLI-Anything and WXWork_CLI Governance Plan

> **For agentic workers:** use `superpowers:executing-plans`. Use parallel subagents only after assigning disjoint write sets. This plan owns CLI-Anything and WXWork_CLI surfaces only; Browser/CLI adapters and Codex harnesses are separate sibling plans.

## Goal

Govern `CLI-Anything` and `WXWork_CLI` as a user-level lane where `WXWork_CLI` may later use CLI-Anything to control enterprise WeChat `WXWork.exe`. This lane is not Codex harnesses.

## Architecture

Codex keeps project-level guard source in this repository first, then promotes to user-level wrappers only when receipts, pins, smoke evidence, rollback pointers, redaction, and operator authorization exist. `CLI-Anything` generation/control and `WXWork_CLI` GUI actions remain blocked until the relevant guard proves the request is safe.

## Tech Stack

Python guard scripts, JSON receipts, local tests, CI manifest entries, docs registry, OpenSpec requirements, user-level Codex state under `C:\Users\lenovo\.codex`, CLI-Anything reference source, and future WXWork_CLI wrapper receipts.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; Stage B checker/test/spec migration is complete; Stage C runtime-promotion ladder is documented and checker-backed; Stage D R4 local smoke receipt tooling is implemented; real GUI/live WXWork runtime remains pending; remote publication remains closed.
Runtime boundary: this repo-local package does not install CLI-Anything, fork or uncontrolled-run WXWork_CLI, start or control `WXWork.exe`, send messages, click GUI controls, mutate enterprise WeChat state, mutate user-level runtime state, or mark the lane active-candidate. R4 `smoke-tested` receipts are written only for bounded help/status/safe-discovery smoke after a prior `installed-user-level` receipt resolves an existing wrapper; if a GUI target is named, a valid global lease is required.
Runtime gap: real live runtime work still requires CLI-Anything install/update, WXWork_CLI fork/adaptation, actual user-level R3 install receipts, authorized R4 smoke execution, and R5 send/action handoff receipts guarded by current operator authorization, GUI owner lease, target/action allowlist, timeout, redaction, and rollback evidence.
Implementation evidence: `tools/wxwork_cli_governance.py smoke-record` writes sanitized R4 `smoke-tested` receipts without process probing, GUI control, send actions, or message body capture; `smoke-check` validates those receipts, and `tools/check_user_level_cli_anything_wxwork_cli_governance.py` checker-backs the R4 helper surface.
Companion refresh note: the zh-CN companion is refreshed with the same R4 local smoke tooling status while preserving runtime tokens.
<!-- CURRENT_STATUS_END -->

## Source References

| Surface | Reference source | Update evidence required later |
| --- | --- | --- |
| CLI-Anything | https://github.com/HKUDS/CLI-Anything | source URL, immutable pin or commit, retrieved_at, license note, rollback pointer |
| WXWork_CLI | local Codex governance fork for WXWork.exe control through CLI-Anything | wrapper path hash, owner lane, operator receipt, dry-run smoke, rollback pointer |
| WXWork.exe target | enterprise WeChat desktop process controlled only through a gated future WXWork_CLI lane | global lease, session match, expiry, no message-content evidence |

## Governance Level Split

| Stage | Governance level | Allowed work | Promotion gate |
| --- | --- | --- | --- |
| 0 | project-level | taxonomy, source references, docs registry, OpenSpec wording | local docs gate |
| 1 | project-level | guard/checker/tests for receipts, path redaction, no hard-load, no live control | focused tests and local gate |
| 2 | reusable project-level | generic receipt and authorization schema usable by other repos | checker-backed evidence and examples |
| 3 | user-level | install/update receipt and wrapper dry-run for CLI-Anything / WXWork_CLI | explicit user-level authorization, smoke pass, rollback pointer |
| 4 | user-level active-candidate | bounded WXWork.exe dry-run or live handoff candidate | operator confirmation, global lease, expiry, rollback, no message body exposure |

## Runtime Promotion Ladder

This lane uses the shared R0-R5 ladder and remains not installed/started/enabled in this package.

| Runtime stage | Level | CLI-Anything/WXWork_CLI scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | Inventory CLI-Anything source, planned WXWork_CLI wrapper shape, Windows path assumptions, and `WXWork.exe` availability without cloning, installing, probing processes, or reading messages. | Source URL, source pin plan, retrieved_at, non-mutating environment probe, no install/run transcript. |
| R1 project-level fake/dry-run runtime | project-level | Use fake receipts and dry-run adapter-plan / gui-plan / gui-check fixtures only. | Dry-run dispatch evidence, `gui_control_performed=false`, `runs_cli_anything=false`, no message-content. |
| R2 reusable project-level helper/guard | reusable project-level | Keep `tools/cli_anything_governance.py` and `tools/wxwork_cli_governance.py` as reusable guard patterns with redaction, lease, authorization, timeout release, and rollback pointer checks. | Focused tests, local gate, reusable receipt schema, changed-path report. |
| R3 user-level install/update receipt | user-level | Record CLI-Anything or WXWork_CLI wrapper install/update only after explicit authorization, immutable source pin, install/update receipt, smoke command, updater command, rollback pointer, owner lane, and path hashes. | `installed-user-level` receipt; no raw install/wrapper/state paths; no automatic Codex config mutation. |
| R4 user-level smoke runtime | user-level | Run only bounded help/status/dry-run smoke for the installed wrapper. WXWork GUI remains no-send and no-message-content. | `smoke-tested` receipt, bounded transcript, global lease if GUI target is named, timeout release, rollback readiness. |
| R5 active-candidate / bounded live handoff | user-level active-candidate | A one-task WXWork_CLI live handoff may include a send action allowed only at R5. | `active-candidate` receipt, global WXWork lease, explicit operator authorization, target/action allowlist, message redaction, ephemeral message handling, session match, future expiry, timeout release, rollback/stop evidence, and post-run action report. |

R5 send boundary: any WXWork_CLI send action remains forbidden before R5; even at R5 it must not expose raw message-content in repository evidence, must use a target/action allowlist, must keep message payloads ephemeral/redacted, and must preserve rollback/stop evidence.

Stage D pending runtime work list:

- Stage D real runtime: install CLI-Anything with source/package pin, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: fork/adapt WXWork_CLI from CLI-Anything with explicit source pin, delta notes, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence.
- Stage D real runtime: implement WXWork.exe discovery/start/status smoke that records R4 `smoke-tested` receipt without sending messages or mutating GUI state.
- Stage D real runtime: define R5 WXWork_CLI send/action handoff guarded by operator authorization, GUI owner lease, target/action allowlist, expiry, timeout release, transcript redaction, and rollback/cleanup evidence.

## File Ownership

This child plan owns future CLI-Anything and WXWork_CLI governance docs, guards, tests, receipts, and source-reference checks. It does not own chrome-devtools-mcp, cdp-bridge-mcp, OpenCLI, Pi, oh-my-pi, or Codex harnesses.

## Parallel Session Contract

One session may claim this implementation plan at a time. Other sessions may work on Browser/CLI adapters or Codex harnesses in parallel only when they do not edit this plan, its future checker, its tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized hotspot lease.

## Task Backlog

## Real Runtime Implementation Gap

This lane is still governance-only for real GUI automation. The next runtime package must install CLI-Anything, create or pin the WXWork_CLI fork/adaptation that drives `WXWork.exe`, and record safe receipts before any enterprise WeChat interaction. Required later evidence:

- CLI-Anything source/package pin, install/update command, wrapper path hash, updater command, rollback pointer, and sanitized R3 receipt.
- WXWork_CLI fork/adaptation commit or package pin, clear delta from upstream CLI-Anything usage, wrapper path hash, rollback pointer, and sanitized R3 receipt.
- WXWork.exe discovery/start/status receipts for R4 smoke that do not send messages or mutate enterprise WeChat state.
- R5 send/action handoff receipts with current operator authorization, GUI owner lease, target/action allowlist, expiry, timeout release, transcript redaction, and rollback/cleanup evidence.

<!-- TASK_BACKLOG_START -->
- [x] Stage A: register this bilingual child plan in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: record CLI-Anything source URL `https://github.com/HKUDS/CLI-Anything`.
- [x] Stage A: state that WXWork_CLI controls `WXWork.exe` through CLI-Anything and is not Codex harnesses.
- [x] Stage A: keep old source plans as migration inputs until Stage B checker migration.
- [x] Stage B: split CLI-Anything tests out of generic CDP/OpenCLI coverage.
- [x] Stage B: rename active WeCom helper/test surfaces to canonical `WXWork_CLI`.
- [x] Stage B: add checker coverage for source URL, adapter-plan semantics, no-message-content, global lease, operator authorization, timeout release, rollback pointer, and dry-run boundaries.
- [x] Stage B: update CI manifest, safety registry, and OpenSpec guard registration.
- [x] Stage C runtime promotion: add R0-R5 project-first/user-level ladder, installed-user-level/smoke-tested/active-candidate markers, and R5-only WXWork_CLI send-action gates.
- [x] Stage D R4 local smoke tooling: add `smoke-record` / `smoke-check` receipt support for bounded help/status/safe-discovery smoke with no GUI control, no send action, no message body, timeout release, redaction, rollback readiness, and global lease when `WXWork.exe` is named.
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- Dedicated CLI-Anything/WXWork_CLI surface checker coverage is in place.
- CLI-Anything tests are split out of generic CDP/OpenCLI coverage.
- Active WeCom surfaces have moved to canonical `WXWork_CLI` naming while archive history remains preserved.
- No-message-content, global lease, operator authorization, timeout-release, rollback, and dry-run checks are checker-backed.
- CI manifest and OpenSpec guard registration are updated.
- Old source plans have been removed after checkers no longer require them.

## Implemented Contract

- `tools/cli_anything_governance.py` is a repo-local receipt and adapter-generation boundary guard for CLI-Anything; it records the reference source `https://github.com/HKUDS/CLI-Anything`, requires pinned receipt/update evidence, and reports `adapter_generation_only=true`.
- `adapter-plan` replaces the former harness wording for this lane; it is adapter-generation only and reports `wxwork_cli_control_surface=WXWork_CLI`.
- `tools/wxwork_cli_governance.py` is the canonical WXWork_CLI guard for future `WXWork.exe` control through CLI-Anything.
- WXWork_CLI GUI prechecks require global lease, operator authorization, session match, future expiry, timeout release, rollback pointer, and no message-content evidence.
- Valid WXWork_CLI receipts allow dry-run dispatch eligibility only in this repo-local MVP; they never perform live GUI control.

## Acceptance Criteria

- CLI-Anything/WXWork_CLI is never described as Codex harnesses.
- Active docs use `WXWork_CLI` for the future WXWork.exe control lane.
- No helper installs, clones, runs, probes, reads messages, sends messages, or controls WXWork.exe without receipt-backed authorization.
- User-level promotion is blocked until project-level guards pass locally.
- Runtime promotion is explicit: R0/R1/R2 stay project-level or reusable project-level; R3 requires `installed-user-level`; R4 requires `smoke-tested`; R5 requires `active-candidate` and is the only stage where a WXWork_CLI send action may be considered.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 Stage D R4 local smoke tooling evidence: branch `implement-cli-anything-wxwork-r4-20260606` adds `tools/wxwork_cli_governance.py smoke-record` / `smoke-check` and focused tests; generated R4 receipts validate through both the WXWork helper and generic `tools/user_level_receipt_governance.py smoke-check`, remain sanitized, and record no GUI control, no send action, no message body, timeout release, rollback readiness, and global lease when `WXWork.exe` is named.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` classifies CLI-Anything install, WXWork_CLI fork/adaptation, WXWork.exe control, R4 smoke, and R5 send/action handoff as pending Stage D runtime work; no GUI runtime is installed, started, controlled, smoked, or live-run.
- 2026-06-05 Stage C runtime promotion evidence: branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for CLI-Anything/WXWork_CLI, keeps this package not installed/started/enabled, and checker-backs R5-only send action controls.
- 2026-06-04 Stage B implementation evidence: `tools/cli_anything_governance.py`, `tools/wxwork_cli_governance.py`, `test/cli_anything_governance.test.py`, `test/wxwork_cli_governance.test.py`, and `tools/check_user_level_cli_anything_wxwork_cli_governance.py` implement and verify the split lane.
<!-- EVIDENCE_INDEX_END -->
