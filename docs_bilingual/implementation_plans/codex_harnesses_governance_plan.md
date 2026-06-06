---
doc_id: codex_harnesses_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/codex_harnesses_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
supersedes:
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
  - docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md
---

# Codex Harnesses Governance Plan

> **For agentic workers:** use `superpowers:executing-plans`. This plan is the only child plan in this split that owns the word `harnesses`; CLI-Anything/WXWork_CLI and Browser/CLI adapters are not harnesses.

## Goal

Fork a Codex-specific harnesses governance model from the listed harness/Pi references while keeping Codex as the primary controller. The model emphasizes recoverable edits, explicit failures, stateful job handling, read-only/write guards, and isolated worktrees.

## Architecture

Project-level governance lands first in this repository as docs, guard contracts, tests, and state schemas. Reusable project-level helpers come next. User-level Pi or oh-my-pi runtime surfaces are allowed only after project-level guards pass and receipts prove pin, smoke, rollback, redaction, and no takeover of Codex launchers.

## Tech Stack

Codex CLI, Git worktrees, JSON job state, Python guard/checker scripts, OpenSpec, docs registry, Pi reference runtime, oh-my-pi reference UX, and user-level Codex state only after receipt-backed promotion.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local; Stage B source-ledger/checker/spec migration is complete; Stage C runtime-promotion ladder is documented and checker-backed; Stage D real-runtime implementation is planned but not executed; remote publication remains closed.
Runtime boundary: Codex harnesses are governance wrappers around future harness jobs; they do not replace Codex, native subagents, native_omx, LangGraph, codex-ohmy, apply_patch, or local-main-first publication gates. This package does not install Pi/oh-my-pi, start a Pi runtime, enable a harness sidecar, run a real harness job, or mark the lane installed-user-level/smoke-tested/active-candidate. Runtime promotion remains not installed/started/enabled in this package.
Runtime gap: real runtime work still requires a Pi/oh-my-pi sidecar install or pinned package candidate, a harness job runner, executable read/write guards, R3 install/update receipts, R4 read-only smoke receipts, and R5 bounded live handoff receipts with isolated worktree evidence. Current R4 helper/checker work does not install, start, or live-run Pi/oh-my-pi; blocked receipts remain not smoke-tested until an R3 receipt resolves a wrapper.
Implementation evidence: `tools/check_codex_harnesses_governance.py` requires source ledger rows, source pin, retrieved_at, license note, rollback pointer, no Codex takeover, unpinned Pi packages rejection, read guard, write guard, job state, isolated worktree, changed-path report markers, and R0-R5 runtime promotion markers. R4 local tooling now adds `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, and `codex_harnesses_smoke_receipts.test.py`; without R3 install/update receipts it writes honest blocked receipts that are accepted as evidence but are not smoke-tested.
Companion refresh note: the zh-CN companion was refreshed in this local package to replace English or mixed prose with Chinese prose while preserving runtime tokens; no runtime behavior changed.
<!-- CURRENT_STATUS_END -->

## Source Ledger

| Reference | URL | Source pin | retrieved_at | License note | Rollback pointer | What this Codex fork may reuse | What it must not do |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | source pin: URL snapshot | retrieved_at: 2026-06-04 | license note: article reference only | rollback pointer: remove derived harness rules | reliability ideas, recoverable editing, explicit failure surfacing | copy unknown code or bypass repo guards |
| oh-my-pi | https://github.com/can1357/oh-my-pi | source pin: commit/tag required before implementation | retrieved_at: 2026-06-04 | license note: inspect upstream license before reuse | rollback pointer: remove sidecar helper copy | sidecar UX, update/rollback concepts, Pi-oriented runtime ergonomics | replace Codex launcher or own provider secrets |
| Pi | https://pi.dev/ | source pin: docs version or snapshot required | retrieved_at: 2026-06-04 | license note: docs reference only | rollback pointer: remove Pi runtime assumptions | Pi runtime/RPC reference and future smoke source | mutate current worktree without one-task authorization |
| Pi packages | https://pi.dev/packages | source pin: package version required | retrieved_at: 2026-06-04 | license note: package license must be recorded per package | rollback pointer: remove package candidate | package discovery/update reference | install packages without pin/receipt/rollback evidence |

## Governance Level Split

| Stage | Governance level | Allowed work | Promotion gate |
| --- | --- | --- | --- |
| 0 | project-level | reference source ledger, taxonomy, no-takeover policy | docs/OpenSpec gate |
| 1 | project-level | harness state schema, read-only guard, write guard, fake Pi fixtures | focused tests and local gate |
| 2 | reusable project-level | portable harness guard/checker pattern for other repos | examples and redaction checks |
| 3 | user-level | Pi/oh-my-pi install-record, update-record, rollback-plan, smoke plan | explicit user authorization and passing project-level guard |
| 4 | user-level active-candidate | bounded read-only Pi/oh-my-pi smoke or sidecar handoff | isolated worktree, job state, no takeover, changed-path report |

## Runtime Promotion Ladder

This lane uses the shared R0-R5 ladder and remains not installed/started/enabled in this package.

| Runtime stage | Level | Codex harnesses scope | Evidence gate |
| --- | --- | --- | --- |
| R0 project-level preflight | project-level | Refresh the source ledger for The Harness Problem, oh-my-pi, Pi, and Pi packages; inspect package/runtime assumptions without installing Pi or oh-my-pi. | Source URLs, source pin plan, retrieved_at, license note, rollback pointer, no Codex takeover. |
| R1 project-level fake/dry-run runtime | project-level | Run fake Pi job fixtures and deterministic read guard/write guard checks only. | Fake job state, read guard, write guard, no live Pi runtime, no Codex launcher mutation. |
| R2 reusable project-level helper/guard | reusable project-level | Keep reusable harness guard/checker schemas for job state, isolated worktree, changed-path report, redaction, and rollback. | Guard schema, local tests, local gate, changed-path report. |
| R3 user-level install/update receipt | user-level | Record Pi/oh-my-pi install/update only after explicit authorization, immutable source/package pin, install/update receipt, smoke command, updater command, rollback pointer, owner lane, and path hashes. | `installed-user-level` receipt, package pin, no unpinned Pi packages, no launcher takeover. |
| R4 user-level smoke runtime | user-level | Run bounded read-only Pi/oh-my-pi smoke or sidecar status probe through `tools/run_codex_harnesses_smoke.py`; no write-capable harness job. | `smoke-tested` receipt validated by `tools/check_codex_harnesses_smoke_receipts.py`, read guard, job state, timeout release, redaction, rollback readiness; missing R3 install receipts produce blocked receipts that are not smoke-tested. |
| R5 active-candidate / bounded live handoff | user-level active-candidate | Active sidecar candidate may run one bounded harness job only under Codex leader ownership. | `active-candidate` receipt, isolated worktree, read guard, write guard, job state, no Codex takeover, changed-path report, rollback/cleanup evidence. |

A Codex harnesses active sidecar must not replace Codex, native subagents, native_omx, LangGraph, codex-ohmy, apply_patch, local-main-first publication gates, or the current main Codex CLI leader session.

Stage D pending runtime work list:

- Stage D real runtime: implement Pi/oh-my-pi sidecar install/update receipt with pinned source/package, rollback pointer, and no-Codex-takeover evidence.
- Stage D real runtime: implement harness job runner receipts with executable read/write guards, isolated worktree evidence, changed-path reporting, cleanup, and rollback.
- Stage D real runtime: run bounded R4 read-only smoke through `tools/run_codex_harnesses_smoke.py` and record a `smoke-tested` receipt before any R5 active-candidate handoff.
- Stage D real runtime: gate any R5 live harness job behind current operator authorization, owner lease, target/action allowlist, timeout release, and post-run cleanup evidence.

## File Ownership

This child plan owns Codex harness governance docs, future `codex_harnesses_governance` checker/guard, Pi/oh-my-pi source ledgers, job-state schemas, and read-only/write guard tests. It does not own CLI-Anything, WXWork_CLI, chrome-devtools-mcp, cdp-bridge-mcp, or OpenCLI.

## Parallel Session Contract

One session may claim this implementation plan at a time. A separate session may work on CLI-Anything/WXWork_CLI or Browser/CLI adapters only when it does not edit this plan, future harness checker/tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized lease.

## Real Runtime Implementation Gap

This plan is not complete at the real-runtime level. The implemented-local package covers governance, checker, test, source-ledger, and R0-R2 dry-run contracts only. A later runtime package must provide:

- Pi or oh-my-pi sidecar source pin, package/version pin, license record, install/update command, rollback pointer, and sanitized install/update receipt.
- A harness job runtime that records job id, isolated worktree, requested read/write scope, read guard result, write guard result, changed paths, timeout, cleanup, and rollback evidence.
- R3 receipt material for installed-user-level state, R4 smoke-tested read-only sidecar status/job fixture, and R5 active-candidate bounded live handoff evidence.
- Proof that Codex remains the leader and no sidecar replaces Codex launchers, native subagents, native_omx, LangGraph, `codex-ohmy`, `apply_patch`, or local-main-first gates.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: state that only this lane is called Codex harnesses.
- [x] Stage A: record The Harness Problem, oh-my-pi, Pi, and Pi packages reference links.
- [x] Stage A: state no Codex takeover, no replacement of native Codex/OMX/LangGraph/apply_patch, and no live Pi execution.
- [x] Stage B: add source ledger requirements for source pin, retrieved_at, license note, and rollback pointer.
- [x] Stage B: add checker/spec coverage for no Codex takeover, no unpinned Pi packages, read guard, write guard, job state, isolated worktree, and changed-path report.
- [x] Stage B: wire checker/tests into CI manifest, safety registry, and OpenSpec guard.
- [x] Stage C runtime promotion: add R0-R5 Codex harnesses ladder, fake Pi job dry-run boundary, installed-user-level/smoke-tested/active-candidate markers, and no-takeover active sidecar gates.
- [x] R4 local smoke receipt tooling: add `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, and `codex_harnesses_smoke_receipts.test.py`; blocked receipts are accepted but remain not smoke-tested.
<!-- TASK_BACKLOG_END -->

## Stage B Closure Notes

- Stage B adds `codex_harnesses_governance` checker coverage for the harness-only lane.
- R4 adds `codex_harnesses_smoke_receipts` checker coverage for bounded smoke receipts, including blocked receipts that do not count as smoke-tested.
- Source refresh now requires source URL, source pin/ref, retrieved_at, license note, and rollback pointer.
- Sidecar output remains non-actionable without read guard, write guard, job state, isolated worktree, and changed-path report evidence.
- CI manifest, safety registry, and OpenSpec guard wiring now reference the split harness checker.

## Acceptance Criteria

- Codex harnesses is a distinct lane from CLI-Anything/WXWork_CLI and Browser/CLI adapters.
- Pi/oh-my-pi is reference or user-level sidecar candidate only, never the Codex launcher.
- No user-level runtime is active without receipt, pin, smoke, rollback, redaction, and no-takeover evidence.
- Any future write-capable harness path requires isolated worktree ownership and changed-path reporting.
- Codex harnesses runtime promotion is explicit: R0/R1/R2 remain project-level or reusable project-level; R3 requires `installed-user-level`; R4 requires `smoke-tested`; R5 requires `active-candidate`, isolated worktree, job state, read/write guards, changed-path report, and no Codex takeover.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 R4 local tooling evidence: `tools/run_codex_harnesses_smoke.py`, `tools/check_codex_harnesses_smoke_receipts.py`, and `codex_harnesses_smoke_receipts.test.py` implement bounded read-only smoke receipt generation and validation; absent R3 install receipts produce blocked receipts that are accepted as evidence but are not smoke-tested; no Pi/oh-my-pi install, sidecar start, live harness job, active-candidate handoff, or Codex takeover occurs.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` reclassifies Pi/oh-my-pi sidecar, harness job runner, executable read/write guards, and R3/R4/R5 receipts as pending Stage D runtime work; no runtime is installed, started, smoked, or live-run.
- 2026-06-05 Stage C runtime promotion evidence: branch `runtime-promotion-plan-20260605` records R0-R5 promotion gates for Codex harnesses, keeps Pi/oh-my-pi sidecar runtime not installed/started/enabled, and checker-backs no-takeover active sidecar constraints.
- 2026-06-04 Stage B implementation evidence: `tools/check_codex_harnesses_governance.py` and `test/check_codex_harnesses_governance.test.py` verify the harness-only lane, source ledger, no-takeover boundary, read/write guards, job state, isolated worktree, changed-path report, and no unpinned Pi packages.
<!-- EVIDENCE_INDEX_END -->
