---
doc_id: spec_kit_authority_guard_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/spec_kit_authority_guard_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Authority Guard Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Update the Spec Kit authority boundary so future checkers and guarded runtime helpers can consume GitHub Spec Kit without letting `specify init`, `.specify/`, `specs/`, `/speckit.*`, or `$speckit-*` become a competing repository governance layer.

## Source Plans

- codex_governance_session_visibility_and_plan_lock_plan

## Reference Sources

- `https://github.com/github/spec-kit` - official Spec Kit repository and README; records `specify init`, `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, and Codex skills-mode `$speckit-*` command surfaces.
- `https://github.github.io/spec-kit/` - official documentation home; records the Spec -> Plan -> Tasks -> Implement SDD flow and multi-agent integration model.
- `https://github.github.io/spec-kit/reference/core.html` - official core command reference; records `specify init` options including `--integration`, `--script`, `--here`, `--force`, `--no-git`, `--ignore-agent-tools`, and `specify self check`.

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 6.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: plan-updated; checker/runtime implementation pending
Stage: Stage D documentation-only update package
Owner session: update-spec-kit-runtime-plan-20260606
Current gate: update this plan and its bilingual companion only; run plan/OpenSpec/precommit/local gates, then local-main integration and stop at the remote-publication gate
Runtime boundary: this package does not run `specify init`, create `.specify/`, install or upgrade Spec Kit, generate command files, or implement checker/runtime scripts
Priority update: 2026-06-07 records Spec Kit as the lowest-priority subordinate template/probe surface in conflicts with Comet, OpenSpec/Superpowers, gstack, or Codex harnesses.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## Conflict Priority

Spec Kit is subordinate to this repository authority stack. Priority is: Comet control first; OpenSpec spec authority and Superpowers HOW remain binding; gstack may provide advisory delivery-loop checks; Codex harnesses may govern candidate runtime jobs; Spec Kit may only provide templates, SDD references, and guarded dry-run probes. Any live `specify init`, `.specify/`, `specs/`, `/speckit.*`, or `$speckit-*` write remains blocked/subordinate/do-not-run unless a separate active implementation plan and explicit operator authorization approve it. Future checker/runtime code must emit an `authority_decision` explaining why a Spec Kit surface is allowed, blocked, or subordinate. Here `authority_decision` means the machine-readable allow/block/subordinate field that records the winning authority layer, the reason, and the applied priority outcome.

## File Ownership

- Existing checker target for future extension: `tools/check_spec_kit_authority_guard.py`
- Existing test target for future extension: `test/*spec_kit*authority*`
- Future runtime target owned by the subordinate adapter plan: `tools/spec_kit_subordinate_runtime.py`
- Governance boundary: `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md`

## Hotspot Serialization

Only one session may own each hotspot at a time:

- Spec Kit guard checker
- .specify path handling
- `tools/spec_kit_subordinate_runtime.py` future helper contract
- Parent plan size edits and docs registry references

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add tests for safe references to Spec Kit docs and unsafe authority-changing operations.
- [x] Implement a checker that fails closed on .specify governance takeover without an active plan.
- [x] Register the checker in the local gate only after implementation confirmation.
- [x] Run Spec Kit guard tests and local gate.
- [x] Record official `github/spec-kit` reference sources and the future Checker + Runtime implementation boundary.
- [x] Record conflict priority: Spec Kit is lowest-priority subordinate template/probe source behind Comet, OpenSpec/Superpowers, gstack, and Codex harnesses.
- [ ] Future Checker implementation: extend `tools/check_spec_kit_authority_guard.py` so it validates any `.specify/`, `specs/`, `/speckit.*`, `$speckit-*`, `specify init`, `specify self check`, extension, or preset evidence against the subordinate-adapter authority rule and requires machine-readable `authority_decision` evidence for allow/block/subordinate outcomes. Here `authority_decision` is the allow/block/subordinate field with the winning authority layer and reason.
- [ ] Future Runtime implementation: require a guarded dry-run/probe helper before any live Spec Kit command; live `specify init --here --force`, install, upgrade, template write, agent-command write, or constitution write requires explicit operator authorization, receipts, rollback evidence, and separate implementation approval.
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
- The updated plan explicitly names official Spec Kit references and keeps all Checker + Runtime work pending future implementation.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 conflict-priority refresh: this docs-only package records Spec Kit as the lowest-priority subordinate surface and keeps any live `specify init` or generated `.specify/` write blocked without future authorization.
- 2026-06-06 Spec Kit reference refresh: branch `update-spec-kit-runtime-plan-20260606` records `github/spec-kit` official sources and future Checker + Runtime requirements without running `specify init` or implementing scripts.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-06-01 implementation package: added `tools/check_spec_kit_authority_guard.py`, `test/spec_kit_authority_guard.test.py`, subordinate-adapter governance docs, CI manifest registration, safety-rule registry backing, and OpenSpec guard integration; focused tests passed before local gate.
<!-- EVIDENCE_INDEX_END -->
