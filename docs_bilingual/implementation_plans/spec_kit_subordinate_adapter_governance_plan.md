---
doc_id: spec_kit_subordinate_adapter_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/spec_kit_subordinate_adapter_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 6
batch: 4
confirmation_required: true
---

# Spec Kit Subordinate Adapter Governance Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Document GitHub Spec Kit as an optional subordinate adapter/template/runtime-probe source and require future checker plus guarded runtime implementation before any Spec Kit command or generated template can affect this repository.

## Source Plans

- codex_governance_session_visibility_and_plan_lock_plan

## Reference Sources

- `https://github.com/github/spec-kit` - official repository and README; records `specify init`, the `/speckit.constitution` -> `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement` workflow, optional `/speckit.clarify`, `/speckit.analyze`, `/speckit.checklist`, and Codex skills-mode `$speckit-*` surfaces.
- `https://github.github.io/spec-kit/` - official documentation home; records Spec Kit as a Spec-Driven Development toolkit and the Spec -> Plan -> Tasks -> Implement artifact chain.
- `https://github.github.io/spec-kit/reference/core.html` - official core command reference; records initialization, integration, PowerShell script selection, force/overwrite, no-git, and self-check command boundaries.

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 4.
- Phase: Phase 6.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: R4 implemented as a dry-run checker/runtime package
Stage: R4 Checker + Runtime implementation package
Owner session: implement-spec-kit-authority-guard-r4-20260607
Current gate: local-main-first validation and integration for this package; after local integration, stop at the remote-publication gate
Runtime boundary: dry-run only; this package records and implements dry-run/probe runtime support without installing Spec Kit, running `specify init`, writing `.specify/`, creating root `specs/`, or exposing `/speckit.*`/`$speckit-*` commands
Priority update: 2026-06-07 keeps Spec Kit as the lowest-priority subordinate adapter behind Comet, OpenSpec/Superpowers, gstack, and Codex harnesses.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## Conflict Priority

This adapter never outranks Comet, OpenSpec, Superpowers, gstack delivery-loop advisory checks, Codex harness candidate runtime guards, implementation-plan claims, local-main-first gates, or remote-publication gates. It may translate Spec Kit artifacts into reviewable subordinate inputs only after authority checks pass. Guarded runtime modes must record `authority_decision`, `source_url`, `source_pin`, `dry_run_only`, receipt/rollback paths, and whether `specify init`/`.specify/`/`specs/`/`/speckit.*`/`$speckit-*` remains blocked/subordinate/do-not-run. Here `authority_decision` is the machine-readable allow/block/subordinate field for the winning authority layer and applied priority outcome.

## File Ownership

- Governance docs: `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md` and `.zh-CN.md`
- Existing authority checker consumer: `tools/check_spec_kit_authority_guard.py`
- Future runtime helper target: `tools/spec_kit_subordinate_runtime.py`
- Runtime tests: `test/spec_kit_subordinate_runtime.test.py` plus the existing `test/spec_kit_authority_guard.test.py` authority-guard coverage
- Registry hotspot only if new docs are added: `docs_bilingual/docs_registry.yaml`

## Hotspot Serialization

Only one session may own each hotspot at a time:

- new governance doc registry entries
- future `tools/spec_kit_subordinate_runtime.py` helper and tests
- `.specify/`, `specs/`, slash-command, and skills-mode generated surfaces

## Parallel Session Contract

- Maximum parallel sessions for this phase: 2.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Document authority order: Comet controls OpenSpec WHAT and Superpowers HOW; Spec Kit may only provide subordinate templates unless a separate plan changes that.
- [x] Add usage boundaries for any future specify command.
- [x] Register the new governance pair if created.
- [x] Run docs registry and implementation-plan checks.
- [x] Record official `github/spec-kit` reference sources and future Checker + Runtime implementation requirements.
- [x] Record lowest-priority subordinate-adapter conflict handling behind Comet, OpenSpec/Superpowers, gstack, and Codex harnesses.
- [x] R4 Checker implementation: verify subordinate adapter usage for Spec Kit artifacts, command files, skills-mode `$speckit-*` surfaces, generated templates, extensions, presets, and workflow outputs without allowing governance-authority migration; require `authority_decision` evidence.
- [x] R4 Runtime implementation: add `tools/spec_kit_subordinate_runtime.py` with `source-refresh`, `probe`, `plan-dry-run`, `init-dry-run`, and `self-check-dry-run` modes; live/apply mode names are rejected and all supported modes remain dry-run only with receipts, rollback pointers, redacted output, timeout controls, and local-main-first validation evidence.
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
- R4 runtime acceptance now requires dry-run/probe receipts before any future live Spec Kit initialization, template write, or command-surface write.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R4 implementation package: implemented dry-run-only Spec Kit subordinate runtime receipts plus checker validation for generated Spec Kit surfaces and receipt authority decisions; no live Spec Kit command, install, `.specify/`, root `specs/`, `/speckit.*`, or `$speckit-*` surface was created.
- 2026-06-07 conflict-priority refresh: this docs-only package records Spec Kit as subordinate adapter/template/probe only; live or apply modes remain deferred behind future Checker + Runtime implementation and explicit authorization.
- 2026-06-06 Spec Kit reference refresh: branch `update-spec-kit-runtime-plan-20260606` records official `github/spec-kit` references and future Checker + Runtime helper requirements without installing or running Spec Kit.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-06-01 Stage C implementation: reused the registered `docs_bilingual/governance/spec_kit_subordinate_adapter_policy.md` and `.zh-CN.md` governance pair, added future `specify` command boundary wording, and marked this child plan implemented-local; validation evidence is recorded in local command output and final assistant response.
<!-- EVIDENCE_INDEX_END -->
