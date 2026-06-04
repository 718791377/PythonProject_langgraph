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
Status: implemented-local; Stage B checker/test/spec migration is complete and remote publication remains closed.
Owner session: the main Codex leader owns this implementation package and the shared CI/spec/docs-registry hotspots.
Runtime boundary: no helper installs, clones, runs CLI-Anything, probes WXWork.exe, reads message content, sends messages, controls GUI state, mutates user-level Codex config, or performs live API/Webhook calls.
Implementation evidence: `tools/cli_anything_governance.py` now exposes `adapter-plan` and `adapter-generation` fields; `tools/wxwork_cli_governance.py` is the canonical WXWork_CLI guard; focused tests cover no hard-load skills, no message-content, global lease, operator authorization, timeout release, rollback pointer, and dry-run-only dispatch.
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

## File Ownership

This child plan owns future CLI-Anything and WXWork_CLI governance docs, guards, tests, receipts, and source-reference checks. It does not own chrome-devtools-mcp, cdp-bridge-mcp, OpenCLI, Pi, oh-my-pi, or Codex harnesses.

## Parallel Session Contract

One session may claim this implementation plan at a time. Other sessions may work on Browser/CLI adapters or Codex harnesses in parallel only when they do not edit this plan, its future checker, its tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized hotspot lease.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: register this bilingual child plan in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: record CLI-Anything source URL `https://github.com/HKUDS/CLI-Anything`.
- [x] Stage A: state that WXWork_CLI controls `WXWork.exe` through CLI-Anything and is not Codex harnesses.
- [x] Stage A: keep old source plans as migration inputs until Stage B checker migration.
- [x] Stage B: split CLI-Anything tests out of generic CDP/OpenCLI coverage.
- [x] Stage B: rename active WeCom helper/test surfaces to canonical `WXWork_CLI`.
- [x] Stage B: add checker coverage for source URL, adapter-plan semantics, no-message-content, global lease, operator authorization, timeout release, rollback pointer, and dry-run boundaries.
- [x] Stage B: update CI manifest, safety registry, and OpenSpec guard registration.
<!-- TASK_BACKLOG_END -->

## Pending Stage B Migration Work

- Add a dedicated CLI-Anything/WXWork_CLI surface checker.
- Split CLI-Anything tests out of generic CDP/OpenCLI coverage.
- Rename active WeCom surfaces to canonical `WXWork_CLI` while preserving archive history.
- Add no-message-content, global lease, operator authorization, timeout-release, rollback, and dry-run checks.
- Update CI manifest and OpenSpec guard registration.
- Remove old source plans after checkers no longer require them.

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

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-04 Stage B implementation evidence: `tools/cli_anything_governance.py`, `tools/wxwork_cli_governance.py`, `test/cli_anything_governance.test.py`, `test/wxwork_cli_governance.test.py`, and `tools/check_user_level_cli_anything_wxwork_cli_governance.py` implement and verify the split lane.
<!-- EVIDENCE_INDEX_END -->
