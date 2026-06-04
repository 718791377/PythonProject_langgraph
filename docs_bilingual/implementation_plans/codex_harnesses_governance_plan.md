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
Status: planned Stage A split target; no Pi or oh-my-pi runtime is enabled by this document package.
Owner session: the current main Codex session owns the parent-plan hotspot and this child-plan creation package.
Remote publication: not authorized.
Boundary: Codex harnesses must not replace Codex, native subagents, native_omx, LangGraph, `codex-ohmy`, or `apply_patch`.
<!-- CURRENT_STATUS_END -->

## Source References

| Reference | URL | What this Codex fork may reuse | What it must not do |
| --- | --- | --- | --- |
| The Harness Problem | https://blog.can.ac/2026/02/12/the-harness-problem | reliability ideas, recoverable editing, explicit failure surfacing | copy unknown code or bypass repo guards |
| oh-my-pi | https://github.com/can1357/oh-my-pi | sidecar UX, update/rollback concepts, Pi-oriented runtime ergonomics | replace Codex launcher or own provider secrets |
| Pi | https://pi.dev/ | Pi runtime/RPC reference and future smoke source | mutate current worktree without one-task authorization |
| Pi packages | https://pi.dev/packages | package discovery/update reference | install packages without pin/receipt/rollback evidence |

## Governance Level Split

| Stage | Governance level | Allowed work | Promotion gate |
| --- | --- | --- | --- |
| 0 | project-level | reference source ledger, taxonomy, no-takeover policy | docs/OpenSpec gate |
| 1 | project-level | harness state schema, read-only guard, write guard, fake Pi fixtures | focused tests and local gate |
| 2 | reusable project-level | portable harness guard/checker pattern for other repos | examples and redaction checks |
| 3 | user-level | Pi/oh-my-pi install-record, update-record, rollback-plan, smoke plan | explicit user authorization and passing project-level guard |
| 4 | user-level active-candidate | bounded read-only Pi/oh-my-pi smoke or sidecar handoff | isolated worktree, job state, no takeover, changed-path report |

## File Ownership

This child plan owns Codex harness governance docs, future `codex_harnesses_governance` checker/guard, Pi/oh-my-pi source ledgers, job-state schemas, and read-only/write guard tests. It does not own CLI-Anything, WXWork_CLI, chrome-devtools-mcp, cdp-bridge-mcp, or OpenCLI.

## Parallel Session Contract

One session may claim this implementation plan at a time. A separate session may work on CLI-Anything/WXWork_CLI or Browser/CLI adapters only when it does not edit this plan, future harness checker/tests, docs registry, CI manifest, or shared OpenSpec hotspots without a serialized lease.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Stage A: register this bilingual child plan in `docs_bilingual/docs_registry.yaml`.
- [x] Stage A: record all four harness source URLs for future refresh.
- [x] Stage A: state that only this lane is called Codex harnesses.
- [x] Stage A: keep Pi/oh-my-pi reference-sidecar content as migration input until Stage B checker migration.
<!-- TASK_BACKLOG_END -->

## Pending Stage B Migration Work

- Add `codex_harnesses_governance` checker/guard.
- Require source URL, pin/ref, retrieved_at, license note, and rollback pointer for source refresh.
- Require read-only guard and write guard evidence before any sidecar output is treated as actionable.
- Add fake Pi/oh-my-pi fixture tests for no takeover and no current-worktree mutation.
- Update CI manifest and OpenSpec guard registration.
- Migrate old Pi/harness references out of the deleted source plans.

## Acceptance Criteria

- Codex harnesses is a distinct lane from CLI-Anything/WXWork_CLI and Browser/CLI adapters.
- Pi/oh-my-pi is reference or user-level sidecar candidate only, never the Codex launcher.
- No user-level runtime is active without receipt, pin, smoke, rollback, redaction, and no-takeover evidence.
- Any future write-capable harness path requires isolated worktree ownership and changed-path reporting.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Pending Stage A evidence: this plan records the Codex harnesses split target and source links; implementation evidence is pending Stage B.
<!-- EVIDENCE_INDEX_END -->
