---
doc_id: gstack_codex_delivery_loop_runtime_governance_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B follow-up child plan
phase: 4
batch: 3
confirmation_required: true
---

# gstack Codex Delivery Loop Runtime Governance Plan

> For agentic workers: use `superpowers:executing-plans`; use parallel subagents only for disjoint write sets. This R4 package implements the repo-local checker plus guarded runtime helper. It does not install upstream gstack, enable hooks, launch browser QA, enable telemetry, mutate user-level Codex configuration, or promote always-on runtime behavior.

## Goal

Add a Phase 4 child plan that forks `garrytan/gstack` workflow governance into Codex-local delivery-loop checks and a guarded future runtime target.

## Source References

| Reference | Required carry-forward |
| --- | --- |
| https://github.com/garrytan/gstack | Process model for AI-assisted software delivery: Think, Plan, Build, Review, Test, Ship, Reflect; role-like review skills, browser QA, release checks, safety guardrails, Codex second opinion, team mode, Codex host install target, and opt-in telemetry boundary. |
| https://gstack.lol/ | Public landing/reference URL for follow-up source refresh. The 2026-06-06 local DNS check failed in this session, so GitHub README is the verified source for this package. |

## Scope Decision

- Level: project-level governance and project-level runtime plan for `D:/PythonProject_langgraph` first.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Phase: Phase 4, because this affects Codex conversation workflow, planning/review/QA/ship discipline, and user-visible delivery-loop status.
- This package: repo-local checker, guarded runtime helper, focused tests, OpenSpec guard wiring, CI manifest registration, safety-rule registry entry, and plan/parent status updates through fixture-backed R4 evidence.
- Runtime boundary: no hook, skill install, MCP wrapper, browser launch, gstack clone, telemetry setup, user-level config mutation, active-candidate promotion, or remote publication is performed by this package.
- Later live implementation: any real user-level install/update, browser QA, hooks, gbrain-like memory, telemetry, or always-on routing requires a separate explicit authorization package and receipts.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local R4 candidate.
Stage: repo-local R0-R4 package adds checker, guarded helper, dry-run actions, fixture-backed R4 smoke receipts, focused tests, OpenSpec guard wiring, CI manifest registration, and safety-rule registry coverage.
Owner session: `implement-gstack-delivery-loop-r4-20260607` owns this R4 implementation package until local main integration.
Current gate: validate implementation-plan rules, OpenSpec guard, precommit update/archive review, local gate, and local MR review before local main integration. Remote publication is not authorized.
Runtime boundary: upstream gstack is not installed, cloned, enabled, invoked as a hook, registered as a skill, connected to browser QA, promoted to user level, or made active-candidate by this package. The R4 smoke path is fixture-backed/read-only and accepts honest blocked receipts when no install receipt exists; `--require-smoke-tested` requires a positive simulated/receipt-backed smoke receipt. Priority boundary: gstack is subordinate delivery-loop advice below Comet and OpenSpec/Superpowers, but above harness candidate runtime selection and Spec Kit templates when only advisory sequencing is at issue.
<!-- CURRENT_STATUS_END -->

## Conflict Priority

Authority priority string: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.

gstack contributes delivery-loop structure only: Think, Plan, Build, Review, Test, Ship, and Reflect. It may recommend sequencing, review, QA, or ship readiness, but must not override Comet control, OpenSpec WHAT authority, Superpowers HOW discipline, implementation-plan claims, local-main-first gates, remote-publication approval, user-level install receipts, browser/GUI authorization, or telemetry opt-in. If its advice conflicts with Codex harness candidate runtime governance, gstack wins only for advisory delivery-loop ordering; harness-specific read/write/runtime safety still belongs to the harness plan. If it conflicts with Spec Kit templates, gstack wins for delivery-loop sequencing while Spec Kit stays a subordinate template/probe source. Future runtime must emit `authority_decision` for each allow/block/advisory result.

## Checker and Runtime Target

The R4 code package provides these repo-local surfaces:

- `tools/check_gstack_codex_delivery_loop.py --root . --json` validates saved delivery-loop evidence, plan/checker/runtime registration, source-reference freshness, and `authority_decision` results for conflicts with Comet, OpenSpec/Superpowers, harnesses, or Spec Kit.
- `tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` reports the current Codex delivery-loop stage and missing evidence without writing files.
- `tools/gstack_codex_delivery_loop_runtime.py plan-dry-run --root . --json` proposes Think/Plan/Build/Review/Test/Ship/Reflect next steps without editing plans or durable state.
- `tools/gstack_codex_delivery_loop_runtime.py review-dry-run --root . --json` reports reviewer, QA, security, documentation, and release-readiness gaps without applying fixes.
- `tools/gstack_codex_delivery_loop_runtime.py qa-dry-run --root . --json` checks whether browser QA is eligible and records blockers without launching a browser.
- `tools/gstack_codex_delivery_loop_runtime.py ship-dry-run --root . --json` checks local-main-first readiness and remote-publication gate state without pushing, opening MRs, or syncing GitHub.
- `tools/gstack_codex_delivery_loop_runtime.py smoke --receipt-dir <dir> --json` writes a bounded R4 smoke receipt. Without an install receipt it writes a blocked/not-smoke-tested receipt. With an explicit fixture install receipt it runs a bounded help smoke, redacts raw paths/secrets from JSON output, records timeout release and rollback-pointer hashes, and remains read-only with respect to user-level state.
- `test/gstack_codex_delivery_loop_runtime.test.py` and `test/check_gstack_codex_delivery_loop.test.py` cover dry-run JSON, R4 blocked/positive receipts, authority priority, safety flag blocking, and redaction.
- Future `--apply` or live modes require explicit operator authorization, receipt/rollback evidence, timeout controls, and local-main / remote-publication boundary checks.

Protected boundaries that must not be rewritten or bypassed include OpenSpec authority, `Routing trace`, `Updated Plan`, implementation-plan claim locks, local-main-first gates, remote-publication approval gates, receipt/redaction rules, user-level install receipts, browser/GUI authorization, secret redaction, and telemetry opt-in.

## Runtime Promotion Ladder

| Stage | Scope | Required evidence |
| --- | --- | --- |
| R0 source preflight | implemented-local | Source URLs, retrieved date, gstack command/workflow mapping, and no upstream install/run evidence. |
| R1 dry-run runtime | implemented-local | Fixture-backed `analyze`, `plan-dry-run`, `review-dry-run`, `qa-dry-run`, and `ship-dry-run`; no file mutation. |
| R2 checker/runtime helper | implemented-local | Checker, guarded helper, tests, OpenSpec guard wiring, CI manifest registration, and docs registry entry. |
| R3 user-level install | fixture-backed only; live deferred | Checker/runtime accept explicit install-receipt-shaped fixture evidence. Real user-level install remains separate and requires explicit authorization, immutable source pin, Codex-host install receipt, rollback pointer, and redaction evidence. |
| R4 smoke runtime | fixture-backed implemented-local; live deferred | Bounded help/status/dry-run smoke receipt with timeout and rollback evidence is supported against an explicit fixture/existing wrapper. Real upstream smoke after real install remains separately authorized. |
| R5 active-candidate | user-level deferred | Explicit active-candidate receipt before hooks, global skill activation, browser QA, gbrain-like memory, telemetry, or always-on workflow routing. |

## File Ownership

This child plan owns its plan files and the future checker/runtime names above. It does not own upstream gstack, user-level `~/.codex/skills/gstack-*`, `~/.claude/skills/gstack`, browser adapter runtime, gbrain or memory stores, global Codex launchers, MCP Router configuration, consumer-project injected context files, telemetry settings, or remote-publication automation.

## Parallel Session Contract

One session may claim this implementation plan at a time. Later code work can run beside unrelated Phase 4 work only if docs registry, CI manifest, OpenSpec guard wiring, delivery-loop fixtures, and conversation-surface fixtures have a serialized hotspot owner.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Create this child plan and Chinese companion.
- [x] Record gstack reference links and verified GitHub README source boundary.
- [x] Require later implementation to reach checker plus runtime level rather than only text governance.
- [x] Record conflict priority: subordinate to Comet/OpenSpec/Superpowers, advisory above harness runtime-candidate selection and Spec Kit templates only for delivery-loop ordering.
- [x] R4 implementation: add `check_gstack_codex_delivery_loop.py` with focused fixtures and JSON output.
- [x] R4 implementation: add `gstack_codex_delivery_loop_runtime.py` with `analyze`, dry-run stage checks, guarded fixture-backed smoke receipts, and no apply/live modes.
- [x] R4 implementation: register focused tests, OpenSpec guard wiring, safety-rule registry entry, and CI manifest coverage.
- [x] Runtime promotion boundary: R3-R4 fixture-backed receipt/smoke paths are implemented locally; real user-level install, browser QA, hooks, gbrain-like memory, telemetry, always-on routing, and R5 active-candidate remain deferred until explicit authorization plus receipt/rollback/redaction evidence.
<!-- TASK_BACKLOG_END -->

## Verification Gates

- `python tools/check_implementation_plan_rules.py --root . --json` - validate implementation plan registry, bilingual companion, parent-plan, size, and evidence-index rules.
- `python tools/run_openspec_guard.py --root .` - validate OpenSpec state and repository governance guard wiring.
- `python tools/check_precommit_update_archive.py --root . --json` - validate required update/archive review before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - run shared local CI gate before integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - run local MR review before local main integration.

This R4 package adds focused checker and runtime helper tests.

## Acceptance Criteria

- This child plan is registered as active and linked from the parent plan.
- The plan records gstack source references and Codex-local checker/runtime targets.
- The plan states that this package does not clone, install, enable, hook, browser-run, telemetry-run, or live-run upstream gstack.
- R3-R4 fixture-backed receipt/smoke evidence is implemented locally; real user-level activation and R5 active-candidate remain deferred and receipt-gated.
- Runtime cannot bypass local-main-first gates, remote-publication approval, browser/GUI authorization, telemetry opt-in, or receipt/redaction boundaries.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R4 implementation package: branch `implement-gstack-delivery-loop-r4-20260607` adds `tools/gstack_codex_delivery_loop_runtime.py`, `tools/check_gstack_codex_delivery_loop.py`, focused tests, OpenSpec guard wiring, CI manifest registration, and safety-rule registry backing. Dry-run actions and fixture-backed R4 smoke receipts are implemented; real user-level install/live/browser/hook/telemetry/R5 active-candidate work remains deferred.
- 2026-06-07 conflict-priority refresh: this docs-only package records gstack as subordinate delivery-loop advisory governance below Comet/OpenSpec/Superpowers and above harness/Spec Kit only for advisory ordering; Checker + Runtime code remains deferred.
- 2026-06-06 documentation package: branch `plan-gstack-codex-delivery-loop-20260606` creates this active Phase 4 child plan, records `garrytan/gstack` and `gstack.lol` references, and leaves checker/runtime code to a later implementation package.
<!-- EVIDENCE_INDEX_END -->
