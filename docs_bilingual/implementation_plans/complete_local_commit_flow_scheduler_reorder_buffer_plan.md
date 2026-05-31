---
doc_id: complete_local_commit_flow_scheduler_reorder_buffer_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 1
phase_label: Phase 1A
batch: 1
priority: early-foundation
confirmation_required: true
---

# Complete Local Commit Flow Scheduler Reorder Buffer Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Make multi-session local commit flow safe by allowing sessions to execute in isolated worktrees while requiring ROB-style serial retirement into local `main`.
The retirement actor can be the session that owns the candidate package when it holds the repository-local local-main retire lock.

## Source Plans

- multi_plan_parallel_session_orchestration_plan
- complete local commit flow governance in the repository-root complete local commit-flow document
- portable_no_backend_parallel_session_plan
- worktree_receipt_claim_lifecycle_plan

## Scope Decision

- Level: project-level governance and future runtime/checker planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 1 supplemental child plan.
- Phase: Phase 1A, inside Phase 1 Construction Safety Base.
- Status: this file is an active child implementation plan. This package creates the governance plan only; runtime/checker implementation must wait for later user confirmation.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Stage: Phase 1A safety base is implemented and remains the downstream runtime contract through the repository-root complete local commit flow
Owner session: this update by `codex-align-complete-flow-parent-plans-20260530` only aligns governance status and does not reopen runtime implementation.
Current gate: the parent-plan family and downstream child plans are aligned to the complete-flow contract from `7e47af8`; later changes must continue to use ROB, claim/receipt state, `local-main-retire.lock`, and the remote-publication gate for local integration.
<!-- CURRENT_STATUS_END -->

## File Ownership

Current documentation package owns:

- the repository-root complete local commit-flow document
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md` - records the parent Phase 1A placement and scheduling dependency.
- `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md` - keeps the Chinese parent-plan companion aligned.
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.md` - defines this English primary child plan.
- `docs_bilingual/implementation_plans/complete_local_commit_flow_scheduler_reorder_buffer_plan.zh-CN.md` - keeps the Chinese companion for this child plan.
- `docs_bilingual/docs_registry.yaml` - registers the bilingual child-plan pair.

Runtime/checker implementation owns:

- `tools/commit_reorder_buffer.py` - will manage ROB entry prediction, queueing, status, retirement, and flushing.
- `tools/check_commit_reorder_buffer.py` - will validate ROB readiness, hotspot fences, and retirement evidence.
- `tools/local_main_retire_lock.py` - will serialize peer-session local-main writes with a nonce lock.
- `tools/check_local_main_retire_lock.py` - will validate active lock schema and stale-lock status.
- `tools/complete_local_flow_to_remote_gate.py` - will acquire/release the lock around local-main mutation and record ROB self-retirement evidence.
- local CI or local MR review wiring
- focused tests for ROB entry state, hotspot fences, and serial retirement

## Hotspot Serialization

Only one session may own each hotspot at a time:

- complete local commit flow policy
- parent orchestration plan pair
- docs registry
- future ROB helper/checker scripts
- claim and receipt lifecycle schema surfaces

## Scheduler Model

This child plan adapts scheduler and CPU commit principles into repository governance:

- Work-Conserving admission: every eligible session can enter when its claim, dependency, hotspot lease, resource backpressure, and local-main retire gates allow it.
- Reorder Buffer: candidate packages are buffered before local `main` retirement.
- Out-of-order execution: disjoint sessions may finish in any order.
- In-order retirement: local `main` integration is serial and lock-owned by the retiring session.
- Scoreboarding and Tomasulo-style readiness: dependencies, claims, receipts, write sets, and gates decide whether an entry is ready.
- Load/store queue and memory fences: shared governance files and schema surfaces force serialization.
- Branch prediction and speculation: sessions predict write sets and dependencies before work starts; failed predictions are blocked, flushed, split, or requeued.
- Backpressure and priority aging: concurrency is reduced when gates fail or retire queues grow, and long-ready entries must be surfaced.
- Checkpoint and rollback: every retire step needs rollback refs and evidence.

## Parallel Admission Terms

- Work-Conserving: the scheduler admits every `eligible` plan/session rather than enforcing a fixed phase cap.
- eligible: active, unclaimed, dependency-satisfied, clean-worktree work with either a disjoint write set or a valid `hotspot lease`.
- hotspot lease: the single-owner write permission for shared governance files, registries, CI manifests, checker scripts, and runtime state surfaces.
- resource backpressure: provider pacing, CPU, memory, terminals, failed gates, stale bases, and retire queues throttle runtime execution without changing the governance rule.
- local-main retire: serial lock-owned retirement of the current session's own ready package into local `main`.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Place this child plan in Phase 1A rather than a late phase or new Phase 8.
- [x] Update the repository-root complete local commit-flow document with ROB-style multi-session execution and serial retirement rules.
- [x] Update the parent orchestration plan pair with the Phase 1A child plan and Batch 1 supplemental status.
- [x] Register this bilingual child plan pair in `docs_bilingual/docs_registry.yaml`.
- [x] Link portable no-backend session and worktree receipt lifecycle plans as downstream consumers.
- [x] Confirm this child plan after local main integration before runtime/checker implementation.
- [x] Define the ROB entry schema and non-Git runtime state directory, defaulting to `.omx/commit-rob/`.
- [x] Implement `tools/commit_reorder_buffer.py` commands: `predict`, `enqueue`, `status`, `retire`, and `flush`.
- [x] Implement `tools/check_commit_reorder_buffer.py` for claim uniqueness, hotspot fences, ready entry validation, and retired evidence.
- [x] Add focused tests for disjoint ready entries, hotspot conflicts, branch-prediction failures, gate failures, and backpressure.
- [x] Wire the checker into local gate or local MR review after the runtime helper is implemented.
- [x] Extend ROB retirement with `retire_mode=self_retire_lock`, `retire_owner_session_id`, and `retire_lock_nonce` fields.
- [x] Add the repository-local local-main retire-lock helper and checker.
- [x] Update the complete local flow helper so an owning session can self-retire its own ready package while holding the local-main lock.
- [x] Replace fixed per-phase parallel caps with work-conserving all-eligible session admission in the parent plan and complete-flow governance.
- [x] Add checker/test coverage so future governance cannot reintroduce fixed 2/3/4/6 phase caps as hard limits.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless a later confirmed update narrows the command list with a justified reason:

```powershell
python tools/check_precommit_update_archive.py --root . --json
python tools/check_implementation_plan_rules.py --root . --json
python tools/check_local_flow_scripted_enforcement.py --root . --json
```

If available in the active branch, also run the shared local gate and local MR review before local-main integration.

## Acceptance Criteria

- the repository-root complete local commit-flow document explains ROB buffering, out-of-order execution, serial retirement, hotspot fences, branch-prediction failure handling, backpressure, rollback evidence, and peer-session self-retirement through the local-main lock.
- The parent plan lists this child plan under Phase 1A / Batch 1 supplemental safety-foundation work.
- Portable no-backend and receipt lifecycle plans reference this plan as an upstream scheduling contract.
- The English primary file remains ASCII-only and the Chinese companion is registered.
- No fixed controller session is required for every local-main retirement; each session can retire its own ready package when the lock and gates allow it.
- No fixed per-phase 2/3/4/6 session cap is treated as a governance hard limit; every eligible child plan can be admitted, with only claim, hotspot, resource-backpressure, and local-main retire locks serializing work.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-30 complete-flow alignment: `7e47af8` updated the repository-root complete local commit flow into the HOW contract for multi-session automatic local commit and local-main integration; this parent-plan-family alignment package replaces downstream fixed-leader serial semantics with session-owned self-retire.
- 2026-05-29 runtime/checker implementation: added `tools/commit_reorder_buffer.py`, `tools/check_commit_reorder_buffer.py`, focused tests, local gate manifest registration, and OpenSpec guard wiring; focused tests, Python manifest, precommit/update-archive, OpenSpec guard JSON, local MR review, and local gate passed; integrated into local `main` at `4479593` with rollback ref `refs/backup/local-main/20260529-1259-before-complete-flow-rob-runtime`, then post-merge local gate passed and the ROB entry was retired.
- 2026-05-29 documentation-governance package: created this active Phase 1A child plan and updated complete-flow/parent/consumer plan references; integrated into local `main` at `ebe5f69` before runtime/checker implementation.
- 2026-05-29 self-retire extension: added lock-backed peer-session local-main retirement semantics and linked to `self_retiring_peer_session_local_main_plan`; pending final local validation and integration evidence.
<!-- EVIDENCE_INDEX_END -->
