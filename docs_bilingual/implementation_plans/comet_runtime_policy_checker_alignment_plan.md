---
doc_id: comet_runtime_policy_checker_alignment_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/comet_runtime_policy_checker_alignment_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Runtime Policy Checker Alignment Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Align Comet runtime behavior, governance policy, OpenSpec specs, checker coverage, and local integration gates.

## Source Plans

- comet_runtime_agile_focus_area_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 5.
- Status: confirmed and implemented as a minimal closeout/alignment package; existing Comet policy, stable spec, checker, runtime test, and CI registration evidence already agree, so no runtime/test source edits are needed in this package.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented, locally validated, and ready for local `main` integration
Stage: Stage C minimal policy/checker alignment closeout package
Owner session: `main-codex-leader-comet-runtime-policy-checker-alignment-20260531`
Current gate: feature-branch validation and local `main` integration; stop at the remote-publication approval gate afterward
Stage C entry condition: satisfied by user confirmation on 2026-05-31 after the Stage B child-plan package was merged to local `main`
Scope note: source checker/test/spec/policy surfaces were verified already aligned; write scope narrowed to this plan pair to avoid active Comet runtime/test hotspots
Last updated: 2026-05-31
<!-- CURRENT_STATUS_END -->

## File Ownership

- openspec/specs/*comet*/spec.md
- openspec/specs/*comet*/spec.zh-CN.md
- tools/run_openspec_guard.py
- test/*comet*policy*alignment*
- docs_bilingual/governance/*comet*

## Hotspot Serialization

Only one session may own each hotspot at a time:

- OpenSpec stable specs
- Comet checker registration

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Map Comet runtime requirements to stable OpenSpec spec statements.
- [x] Add checker coverage for policy/runtime drift.
- [x] Update CI/local gate registration if new checker or tests are added.
- [x] Run verify_official_openspec, run_openspec_guard, and local gate.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- The child plan is confirmed by the user after local `main` integration.
- The active session claim names this child plan path before write work starts.
- Tests or checker fixtures fail before the implementation when the change is behavior-changing.
- Governance docs, runtime helpers, checkers, tests, and CI registration stay aligned.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-31 Stage C minimal closeout: user confirmed implementation; existing alignment evidence passed `python tools/check_openspec_comet_superpowers_policy.py --root . --json`, `python test/comet_runtime_management_flow.test.py`, `python tools/check_implementation_plan_rules.py --root . --json`, and `python tools/check_worktree_task_receipt.py --root . --json`; source edits were not needed beyond this plan pair because the checker reported `Spec source: stable` and no missing policy/spec/runtime terms.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
<!-- EVIDENCE_INDEX_END -->
