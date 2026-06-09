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
Status: implemented-local
Status: CLI-Anything installed user-level and smoke-tested; WXWork_CLI integration delegated to the operator-designated external consumer project and remains out of scope for this repository package.
Stage: R6 CLI-Anything user-level install evidence plus existing R5 WXWork_CLI governance handoff.
Owner session: `resume-019e8aa7-cli-anything-install` in feature branch `install-cli-anything-user-level-20260609`.
Current gate: run focused tests, repository guard, precommit update/archive review, local CI, local MR review, then guarded local-main-first integration; remote publication remains unauthorized.
Install evidence: `CLI-Anything` skills were installed at user level from `https://github.com/HKUDS/CLI-Anything`; `cli-anything-hub==0.3.0` exposes `cli-hub`; ignored receipt `.omx/cli-anything/cli-anything.lock.json` validates as `installed-user-level`, `install_performed=true`, `network_fetch_performed=true`, `wxwork_cli_installed=false`, and `wxwork_cli_controlled=false`.
R5 evidence: `wxwork-cli active-candidate lane profile` remains validated by `tools/check_r5_active_candidate_receipts.py` and the generic `tools/user_level_receipt_governance.py active-check` contract, but WXWork_CLI live/send implementation is handed off to the operator-designated external consumer project.
Runtime boundary: this package installs/smoke-tests CLI-Anything only; it does not install/start/control WXWork_CLI in this repository, start WXWork.exe, send WXWork messages, launch durable workers, run live harness jobs, run Spec Kit live/apply modes, mutate user-level Codex config, or mutate remote publication. Historical R5 governance packages remained not installed/started/enabled in this package.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-09
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

This lane uses the shared R0-R5 ladder. Historical governance-only packages remained not installed/started/enabled in this package; the current R6 install package promotes CLI-Anything only to installed-user-level / smoke-tested while WXWork_CLI stays delegated to the operator-designated external consumer project.

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

- Stage D real runtime: install CLI-Anything with source/package pin, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence. Completed for CLI-Anything on 2026-06-09 with `cli-hub 0.3.0`, installed-user-level receipt, and `cli-hub --help` smoke.
- Stage D real runtime: fork/adapt WXWork_CLI from CLI-Anything with explicit source pin, delta notes, R3 receipt, wrapper hash, updater command, rollback pointer, and redaction evidence. Delegated to the operator-designated external consumer project; this repository package does not install/start/control WXWork_CLI.
- Stage D real runtime: implement WXWork.exe discovery/start/status smoke that records R4 `smoke-tested` receipt without sending messages or mutating GUI state.
- Stage D real runtime: define R5 WXWork_CLI send/action handoff guarded by operator authorization, GUI owner lease, target/action allowlist, expiry, timeout release, transcript redaction, and rollback/cleanup evidence.

## File Ownership

This child plan owns future CLI-Anything and WXWork_CLI governance docs, guards, tests, receipts, and source-reference checks. It does not own chrome-devtools-mcp, cdp-bridge-mcp, OpenCLI, Pi, oh-my-pi, or Codex harnesses.

## Parallel Session Contract

One session may claim this implementation plan at a time. Other sessions may work on Browser/CLI adapters or Codex harnesses in parallel only when they do not edit this plan, its future checker, its tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized hotspot lease.

## Task Backlog

## Real Runtime Implementation Gap

This lane has now installed CLI-Anything user-level and remains governance-only for real WXWork GUI automation. the operator-designated external consumer project owns future WXWork_CLI integration that drives `WXWork.exe`; this repository records safe CLI-Anything receipts before any Enterprise WeChat interaction. Required later evidence:

- CLI-Anything source/package pin, install/update command, wrapper path hash, updater command, rollback pointer, and sanitized R3 receipt. Completed locally for CLI-Anything on 2026-06-09; ignored receipt `.omx/cli-anything/cli-anything.lock.json` validates without raw path output.
- WXWork_CLI fork/adaptation commit or package pin, clear delta from upstream CLI-Anything usage, wrapper path hash, rollback pointer, and sanitized R3 receipt. Delegated to the operator-designated external consumer project.
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
- [x] Stage E CLI-Anything user-level install: install `CLI-Anything` skills from `HKUDS/CLI-Anything`, install `cli-anything-hub==0.3.0`, create `cli-hub` wrappers, pass `cli-hub --help`, validate `installed-user-level` receipt, and keep WXWork_CLI delegated to the operator-designated external consumer project.
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
- 2026-06-09 CLI-Anything user-level install evidence: branch `install-cli-anything-user-level-20260609` installed user-level skills from `https://github.com/HKUDS/CLI-Anything`, installed `cli-anything-hub==0.3.0`, exposed `cli-hub 0.3.0`, passed `cli-hub --help`, and wrote ignored receipt `.omx/cli-anything/cli-anything.lock.json`. Receipt validation reports `installed-user-level`, `install_performed=true`, `network_fetch_performed=true`, `user_level_config_mutated=false`, `wxwork_cli_installed=false`, `wxwork_cli_controlled=false`, source URL preserved, raw private paths redacted, and rollback pointer hashed. WXWork_CLI integration is handed off to the operator-designated external consumer project; no WXWork.exe start/control/send occurred.
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for CLI-Anything / WXWork_CLI governance. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-06 Stage D R4 local smoke tooling evidence: branch `implement-cli-anything-wxwork-r4-20260606` adds `tools/wxwork_cli_governance.py smoke-record` / `smoke-check` and focused tests; generated R4 receipts validate through both the WXWork helper and generic `tools/user_level_receipt_governance.py smoke-check`, remain sanitized, and record no GUI control, no send action, no message body, timeout release, rollback readiness, and global lease when `WXWork.exe` is named.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` classifies CLI-Anything install, WXWork_CLI fork/adaptation, WXWork.exe control, R4 smoke, and R5 send/action handoff as pending Stage D runtime work; no GUI runtime is installed, started, controlled, smoked, or live-run.
- 2026-06-05 Stage C runtime promotion evidence: branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for CLI-Anything/WXWork_CLI, keeps this package not installed/started/enabled, and checker-backs R5-only send action controls.
- 2026-06-04 Stage B implementation evidence: `tools/cli_anything_governance.py`, `tools/wxwork_cli_governance.py`, `test/cli_anything_governance.test.py`, `test/wxwork_cli_governance.test.py`, and `tools/check_user_level_cli_anything_wxwork_cli_governance.py` implement and verify the split lane.
<!-- EVIDENCE_INDEX_END -->
