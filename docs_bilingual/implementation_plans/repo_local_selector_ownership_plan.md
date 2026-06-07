---
doc_id: repo_local_selector_ownership_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/repo_local_selector_ownership_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B child plan
phase: 3
batch: 2
confirmation_required: true
---

# Repo Local Selector Ownership Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this child plan is confirmed. Steps use checkbox syntax for tracking.

## Goal

Ensure active durable selectors are repository-local and cannot leak across repositories or worktrees.

## Source Plans

- codex_user_level_cross_session_durable_state_isolation_plan

## Scope Decision

- Level: project-level governance and runtime planning for `D:/PythonProject_langgraph`.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Batch: Stage B Batch 2.
- Phase: Phase 3.
- Status: this file is an active child implementation plan, but implementation must not start until the user confirms this child plan after local `main` integration.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R5 checker-backed active-candidate gate implemented locally; real sensitive live actions remain blocked unless a current lane receipt passes.
Stage: R5 runtime-governance receipt package for repo-local selector ownership.
Owner session: `resume-019e8aa7-r5-runtime-governance-batch` in feature branch `implement-r5-runtime-governance-batch-20260607`.
Current gate: run focused tests, repository guard, precommit update/archive review, local CI, local MR review, then guarded local-main-first integration; remote publication remains unauthorized.
R5 evidence: `selector active-candidate receipt linkage and same-repo adoption split` is validated by `tools/check_r5_active_candidate_receipts.py` and the generic `tools/user_level_receipt_governance.py active-check` contract.
Runtime boundary: this R5 package validates fixture-backed receipts and checker wiring only; it does not install user-level tools, start browsers or GUI apps, send WXWork messages, launch durable workers, run live harness jobs, run Spec Kit live/apply modes, mutate user-level config, or mutate remote publication.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-07
<!-- CURRENT_STATUS_END -->

## File Ownership

- `.omx/state/selectors/active.json` schema or fixtures - defines repo-local active selector truth.
- `tools/check_durable_artifact_state_surfaces.py` - validates durable artifact and state-surface evidence.
- `tools/*selector*` - covers selector ownership, runtime, and fixture helper surfaces.
- `tools/repo_local_selector_runtime.py` - writes, releases, stale-reclaims, and smoke-tests repo-local selector receipts.
- `test/*selector*ownership*` - covers selector ownership checker regression fixtures.
- `test/repo_local_selector_runtime.test.py` - covers R4 selector runtime regression behavior.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- .omx/state/selectors/active.json
- .omx/state/selectors/leases/*

## Parallel Session Contract

- Maximum parallel sessions for this phase: 3.
- This child plan is one claim unit: exactly one active session may claim it at a time.
- Parallel work is allowed only with different child plans and disjoint write scopes.
- Local `main` integration remains serial through `local-main-retire.lock`; the owning session may self-retire only its own ready package and must stop at the remote publication gate.

## Task Backlog

## Real Runtime Implementation Gap

Selector ownership is checker-backed, but automatic selector refresh is not implemented. Real runtime work must write, renew, release, and audit repo-local active selectors under ownership and stale-lock rules.

<!-- TASK_BACKLOG_START -->
- [x] Confirm this child plan after local main integration.
- [x] Add fixtures for same-repo, cross-repo, and stale selector ownership.
- [x] Update checker logic to fail closed on cross-repository selector adoption.
- [x] Document safe selector inspection and no-auto-adoption behavior.
- [x] Run durable state surface checks and local gate.
- [x] Stage D real runtime: implement selector write/refresh helper that records owner session, backend family, lease expiry, selector revision, and rollback pointer.
- [x] Stage D real runtime: implement selector release/stale-reclaim helper with explicit nonce matching and audit receipts.
- [x] Stage D real runtime: add dry-run and apply modes that fail closed on cross-repo selector adoption.
- [x] R4 user-level smoke runtime: add bounded read-only selector smoke that records a `smoke-tested` receipt without mutating the active selector.
<!-- TASK_BACKLOG_END -->

## Validation Gates

Run these gates before local `main` integration unless this child plan later narrows the command list with a justified update:

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan anchors, size limits, registry entries, and bilingual pairs.
- `python tools/check_precommit_update_archive.py --root . --json` - reviews required existing-file updates, checker registration, and archive readiness before commit.
- `python tools/check_worktree_task_receipt.py --root . --json` - validates worktree claim and receipt lifecycle metadata.
- `python test/repo_local_selector_runtime.test.py` - validates selector write/refresh, release, stale-reclaim, dry-run/apply, fail-closed, and R4 smoke receipt behavior.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs local MR review before local main integration.

## Acceptance Criteria

- The child plan is confirmed by the user after local `main` integration.
- The active session claim names this child plan path before write work starts.
- Tests or checker fixtures fail before the implementation when the change is behavior-changing.
- Governance docs, runtime helpers, checkers, tests, safety registry, and CI registration stay aligned.
- R4 smoke receipt writes only sanitized repo-local selector evidence and does not mutate user-level state, browser data, or the active selector during smoke.
- Evidence is recorded as a lightweight index instead of appending large evidence packages to this plan.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for repo-local selector ownership. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-05 Stage D R4 implementation: branch `implement-repo-local-selector-r4-20260605` adds `tools/repo_local_selector_runtime.py`, `test/repo_local_selector_runtime.test.py`, CI manifest registration, and safety registry wiring for selector write/refresh, explicit nonce release, stale reclaim, dry-run/apply fail-closed behavior, and R4 `smoke-tested` receipts.
- 2026-06-05 real-runtime gap update: branch `runtime-plan-standard-20260605` records pending Stage D runtime work for active selector write, refresh, renewal, and release helpers; this package updates plan governance only and does not run live runtime.
- 2026-05-28 Stage B child-plan creation: created as part of the parent multi-plan orchestration child-plan package; final commit is recorded in the assistant response and local git history.
- 2026-05-30 Stage C implementation start: active session claim `main-codex-repo-local-selector-ownership-20260530` created before tracked write work; implementation adds repo-local selector fixtures, checker, guard wiring, and governance documentation.
- 2026-05-30 Local validation: selector ownership checker, durable artifact surface tests, OpenSpec guard JSON tests, precommit review checks, worktree receipt check, and `tools/ci/local_gate.ps1` passed before feature commit.
<!-- EVIDENCE_INDEX_END -->
