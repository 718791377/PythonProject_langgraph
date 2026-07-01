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
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for Spec Kit authority guard.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `spec-kit-authority-guard`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with already accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
<!-- CURRENT_STATUS_END -->

## Conflict Priority

Spec Kit is subordinate to this repository authority stack. The strict priority order is `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`. Spec Kit may only provide templates, SDD references, and guarded dry-run probes. Any live `specify init`, `.specify/`, `specs/`, `/speckit.*`, or `$speckit-*` write remains blocked/subordinate/do-not-run unless a separate active implementation plan and explicit operator authorization approve it. Future checker/runtime code must emit an `authority_decision` explaining why a Spec Kit surface is allowed, blocked, or subordinate. Here `authority_decision` means the machine-readable allow/block/subordinate field that records the winning authority layer, the reason, and the applied strict priority outcome.

## File Ownership

- Existing checker target for future extension: `tools/check_spec_kit_authority_guard.py`
- Existing authority test target: `test/spec_kit_authority_guard.test.py`
- R4 runtime target owned by the subordinate adapter plan: `tools/spec_kit_subordinate_runtime.py` and `test/spec_kit_subordinate_runtime.test.py`
- Governance boundary: `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md`

## Hotspot Serialization

Only one session may own each hotspot at a time:

- Spec Kit guard checker
- .specify path handling
- `tools/spec_kit_subordinate_runtime.py` dry-run helper contract and runtime test coverage
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
- [x] Record conflict priority: Spec Kit is the lowest-priority subordinate template/probe source behind Comet, OpenSpec/Superpowers, gstack, and harness runtime safety.
- [x] R4 Checker implementation: extend `tools/check_spec_kit_authority_guard.py` so it validates `.specify/`, root `specs/`, generated `/speckit.*`, `$speckit-*`, `.codex/commands/*speckit*`, `.codex/skills/*speckit*`, `.github/prompts/*speckit*`, root `speckit.*`, root `speckit-*`, extension, preset, and workflow-output surfaces, and validates machine-readable `authority_decision` receipt evidence.
- [x] R4 Runtime implementation: add `tools/spec_kit_subordinate_runtime.py` with `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run` modes; all modes are dry-run only and live/apply modes are rejected.
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
- The R4 package implements dry-run-only checker/runtime support while keeping live Spec Kit commands and generated surfaces blocked without future authorization.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for Spec Kit authority guard. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-07 R4 implementation package: added dry-run-only `tools/spec_kit_subordinate_runtime.py`, extended `tools/check_spec_kit_authority_guard.py` receipt and generated-surface validation, added standalone `test/spec_kit_subordinate_runtime.test.py`, and registered runtime coverage in the CI manifest.
- 2026-06-07 R4 closeout package: tightened the strict authority order to `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, promoted the stable safety-rule requirement, and archived the bounded closeout change before local-main integration.
- 2026-06-07 conflict-priority refresh: this package records the strict order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit` and keeps any live `specify init` or generated `.specify/` write blocked without future authorization.
- 2026-06-06 Spec Kit reference refresh: branch `update-spec-kit-runtime-plan-20260606` records `github/spec-kit` official sources and future Checker + Runtime requirements without running `specify init` or implementing scripts.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-06-01 implementation package: added `tools/check_spec_kit_authority_guard.py`, `test/spec_kit_authority_guard.test.py`, subordinate-adapter governance docs, CI manifest registration, safety-rule registry backing, and OpenSpec guard integration; focused tests passed before local gate.
<!-- EVIDENCE_INDEX_END -->
