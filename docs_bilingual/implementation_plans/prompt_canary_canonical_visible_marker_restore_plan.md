---
doc_id: prompt_canary_canonical_visible_marker_restore_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/prompt_canary_canonical_visible_marker_restore_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B follow-up child plan
phase: 2
batch: 2-followup
confirmation_required: true
---

# Prompt Canary Canonical Visible Marker Restore Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Restore the startup-summary-defined canonical visible canary to the requested non-ASCII start/end markers while keeping all non-startup authority, tool, launcher, worker handoff, and model-readable replay surfaces free of those literal markers.

## Source Plans

- codex_user_level_context_retention_canary_plan; context_retention_canary_literal_boundary_plan; startup_mojibake_utf8_recovery_plan; session_replay_context_filtering_plan; launcher_payload_context_boundary_plan

## Scope Decision

- Level: project-level governance, checker, helper, test, startup summary, and OpenSpec update for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2 follow-up.
- Phase: Phase 2 follow-up after implemented-local canary safety child plans.
- Status: active child implementation plan; the user has confirmed this follow-up plan and requested implementation after this plan package enters local `main`.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implementation-complete-local-candidate
Stage: implementation package restored the startup-summary-defined canonical visible canary, updated AGENTS/spec/governance wording, and hardened checkers/tests/session replay filtering before local `main` integration.
Owner session: implement-restore-nonascii-canary-20260602 (implementation package)
Current gate: run full repository validation, commit the implementation package, merge to local `main`, and stop at the remote-publication approval gate.
Evidence: focused RED tests failed before checker changes; focused tests and focused checkers now pass for canonical response evidence, legacy ASCII classification, and model-readable replay blocking without echoing marker literals.
Last updated: 2026-06-02
Follow-up Stage A: the operator requested a stricter response-position contract. Complete user-visible assistant responses must place the startup-summary-defined start marker as the first visible text and the startup-summary-defined end marker as the last visible text; all non-startup literal-placement and model-readable filtering rules remain unchanged.
<!-- CURRENT_STATUS_END -->

## File Ownership

- `docs_bilingual/project_startup_summary.md` - primary startup authority surface for the canonical visible canary.
- `docs_bilingual/project_startup_summary.zh-CN.md` - companion startup authority surface for the canonical visible canary.
- `AGENTS.md` - repository instruction surface that points back to startup summaries without marker literals.
- `tools/check_context_retention_canary_surface.py` - checker for marker literal placement and response/session diagnostics.
- `tools/check_startup_instruction_mojibake.py` - checker for UTF-8 and mojibake recovery behavior.
- `tools/session_replay_context_filtering.py` - helper that filters marker copies from model-readable replay context.
- `test/check_context_retention_canary_surface.test.py` - focused tests for canonical marker diagnostics and literal boundaries.
- `test/check_startup_instruction_mojibake.test.py` - focused tests for UTF-8 recovery and legacy marker classification.
- `test/check_session_replay_context_filtering.test.py` - focused tests for replay/session context filtering.
- `openspec/specs/codex-user-level-context-retention-canary-surface/spec.md` - stable OpenSpec authority for the canary surface contract.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- startup summary pair
- `AGENTS.md` - repository instruction surface that points back to startup summaries without marker literals. instruction surface
- context canary checkers and response diagnostics
- session replay filtering helper and tests
- stable context-retention canary OpenSpec spec

## Parallel Session Contract

- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Because this follow-up touches shared canary hotspots, its implementation package must run serially against other Phase 2 canary work.
- Local `main` integration remains serial through the repository local-main-first helper and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this follow-up child plan request from the user/operator.
- [x] Update the startup summary pair so the requested non-ASCII start/end markers are canonical again and the previous ASCII tokens become legacy/stale compatibility input.
- [x] Update `AGENTS.md` so complete user-visible assistant responses proactively use the startup-summary-defined canonical visible canary without copying marker literals into `AGENTS.md`.
- [x] Add failing tests proving the restored canonical marker is accepted in user-visible responses and blocked from model-readable session/replay context.
- [x] Update canary surface, mojibake, and session replay helpers so canonical marker literals are derived by codepoint or variable surfaces instead of direct source literals.
- [x] Update the stable OpenSpec canary spec and related plan status/evidence text.
- [x] Run focused tests and focused checkers before repository-level gates; full local gate and local MR review remain the final pre-integration evidence.
- [x] Record the response-position hardening contract in the parent and child plans before runtime implementation.
- [ ] Update the startup summary pair with the response-position rule while keeping English ASCII-only codepoint indirection and Chinese as the only literal visible marker source.
- [ ] Extend canary response diagnostics so canonical response evidence requires the start marker at the beginning and the end marker at the end; mispositioned markers fail closed without echoing marker literals.
- [ ] Add focused RED/GREEN tests and update the stable canary OpenSpec spec for the new response-position scenarios.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- Run `python test/check_context_retention_canary_surface.test.py` - prove canary surface diagnostics and literal boundaries.
- Run `python test/check_startup_instruction_mojibake.test.py` - prove UTF-8 recovery and mojibake handling.
- Run `python test/check_session_replay_context_filtering.test.py` - prove session replay marker filtering.
- Run `python tools/check_context_retention_canary_surface.py --root . --json` - inspect marker literal placement and response diagnostics.
- Run `python tools/check_startup_instruction_mojibake.py --root . --json` - inspect startup and instruction encoding safety.
- Run `python tools/session_replay_context_filtering.py --root . --json` - inspect replay filtering output.
- Run `python tools/run_openspec_guard.py --root . --json` - verify OpenSpec and document governance.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Json -StepTimeoutSeconds 600` - execute the shared local CI gate.
- Run `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - execute the local MR review gate.

## Acceptance Criteria

- The startup summary pair is the only active file pair containing canonical visible marker literals.
- Non-startup tracked files contain no canonical visible marker literals or corrupted variants.
- User-visible response diagnostics accept the restored canonical marker.
- Model-readable session, replay, compaction, and handoff contexts block or filter restored canonical marker copies before prompt-authority handoff.
- The previous ASCII token pair is classified as legacy/stale compatibility input, not canonical.
- Diagnostics report marker status and counts without echoing marker literals.

- Complete user-visible assistant responses count as canonical evidence only when the startup-summary-defined start marker is first visible text and the end marker is last visible text.
## Evidence Index

- 2026-06-06 response-position Stage A package: branch `plan-hardcode-canary-response-position-20260606` records the stricter complete-response start/end marker placement contract and leaves startup/checker/spec implementation to the follow-up runtime package.
<!-- EVIDENCE_INDEX_START -->
- 2026-06-02 plan package: created as a Phase 2 follow-up child plan to restore the startup-summary-defined canonical visible canary and add explicit model-readable session context blocking.
- 2026-06-02 implementation package: restored canonical marker authority to the startup summary pair, made legacy ASCII markers stale compatibility input, updated AGENTS/spec/governance text, and added checker/replay tests for canonical response acceptance plus replay/model-context blocking.
<!-- EVIDENCE_INDEX_END -->
