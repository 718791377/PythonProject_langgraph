---
doc_id: comet_superpowers_visibility_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/comet_superpowers_visibility_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 5
batch: 4
confirmation_required: true
---

# Comet Superpowers Visibility Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Make Superpowers HOW-layer skill usage explicit in Comet Design, Build, Verify, and branch-finishing phases.

## Source Plans

- comet_runtime_agile_focus_area_plan; codex_governance_session_visibility_and_plan_lock_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 5.
- Status: this file is an active child implementation plan; the user confirmed implementation in the 2026-05-31 cold-start continuation request.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: completed and locally integrated
Stage: Phase 5 final closeout package
Owner sessions: main-codex-leader-comet-superpowers-visibility-20260531; main-codex-refine-comet-superpowers-visibility-plan-closure-20260607
Current gate: remote-publication approval gate; remote publication is not authorized by the current request, and no further local Phase 5 implementation work remains
Stage C entry condition: satisfied by the user's 2026-05-31 cold-start continuation request
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## File Ownership

- `.codex/skills/comet/SKILL.md` - declares the Comet entry workflow and required Superpowers HOW-layer evidence.
- `.codex/skills/comet-design/SKILL.md` - records Design-phase HOW-layer invocation expectations.
- `.codex/skills/comet-build/SKILL.md` - records Build-phase HOW-layer planning, execution, and verification expectations.
- `.codex/skills/comet-verify/SKILL.md` - records Verify and branch-finishing HOW-layer evidence expectations.
- `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` - English governance policy for the OpenSpec WHAT and Superpowers HOW split.
- `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md` - Chinese companion for the Comet/Superpowers workflow policy.
- `tools/check_comet_superpowers_visibility.py` - checker that enforces required Superpowers visibility terms.
- `tools/run_openspec_guard.py` - shared OpenSpec guard entry that includes the visibility checker.
- `tools/safety_rule_script_backing_registry.json` - registry entry proving script-backed enforcement coverage.
- `tools/ci/ci_test_manifest.json` - CI manifest entry that keeps the checker covered by local and remote gates.
- `test/*superpowers*visibility*` - test fixtures or tests for Superpowers visibility enforcement.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- Comet skill instructions
- Superpowers skill invocation evidence

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan for implementation through the user's 2026-05-31 cold-start continuation request.
- [x] Add evidence expectations for using-superpowers, writing-plans, executing-plans, test-driven-development, verification-before-completion, and finishing-a-development-branch.
- [x] Update Comet skill docs so OpenSpec remains WHAT and Superpowers remains HOW.
- [x] Add checker or test coverage for missing HOW-layer evidence when Comet claims Superpowers usage.
- [x] Run skill boundary, Superpowers visibility, and local gate checks.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- The child plan is confirmed by the user's 2026-05-31 continuation request before non-document implementation.
- The active session claim names this child plan path before write work starts.
- Tests or checker fixtures fail before the implementation when the change is behavior-changing.
- Governance docs, runtime helpers, checkers, tests, and CI registration stay aligned.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-31 Stage C start: user confirmed implementation; claim `main-codex-leader-comet-superpowers-visibility-20260531` owns the serialized Comet/Superpowers visibility hotspot.
- 2026-05-31 local-main closeout: branch `implement-comet-superpowers-visibility-20260531` entered local `main` at `407e5eb`; `python tools/check_openspec_comet_superpowers_policy.py --root . --json`, `python tools/check_comet_superpowers_visibility.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, and the shared local gate evidence are captured in local history.
- 2026-06-07 closure-status sync: refreshed this bilingual plan pair so the current gate is the remote-publication approval gate rather than implying any remote step is already approved; the Chinese task backlog is aligned with the English completed checklist.
<!-- EVIDENCE_INDEX_END -->
