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

> For agentic workers: use `superpowers:executing-plans`; use parallel subagents only for disjoint write sets. This package records the checker plus runtime target only; it does not create scripts, install gstack, or enable runtime behavior.

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
- This package: plan, registry, and parent index update only; no checker, runtime helper, hook, skill install, MCP wrapper, browser launch, gstack clone, telemetry setup, or user-level config mutation.
- Later implementation: must reach checker plus runtime level before any readiness claim.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active child-plan definition; code work is not started.
Stage: documentation package records the checker plus runtime requirement and source links.
Owner session: `plan-gstack-codex-delivery-loop-20260606` owns this plan-document package only.
Current gate: validate implementation-plan rules, OpenSpec guard, precommit update/archive review, local gate, and local MR review before local main integration. Remote publication is not authorized.
Runtime boundary: no gstack runtime is installed, cloned, enabled, invoked as a hook, registered as a skill, connected to browser QA, or promoted to user level by this package.
<!-- CURRENT_STATUS_END -->

## Checker and Runtime Target

The later code package must provide these repo-local surfaces before the plan may claim R2 readiness:

- `tools/check_gstack_codex_delivery_loop.py --root . --json` validates saved delivery-loop evidence, plan/checker/runtime registration, and source-reference freshness.
- `tools/gstack_codex_delivery_loop_runtime.py analyze --root . --json` reports the current Codex delivery-loop stage and missing evidence without writing files.
- `tools/gstack_codex_delivery_loop_runtime.py plan-dry-run --root . --json` proposes Think/Plan/Build/Review/Test/Ship/Reflect next steps without editing plans or durable state.
- `tools/gstack_codex_delivery_loop_runtime.py review-dry-run --root . --json` reports reviewer, QA, security, documentation, and release-readiness gaps without applying fixes.
- `tools/gstack_codex_delivery_loop_runtime.py qa-dry-run --root . --json` checks whether browser QA is eligible and records blockers without launching a browser.
- `tools/gstack_codex_delivery_loop_runtime.py ship-dry-run --root . --json` checks local-main-first readiness and remote-publication gate state without pushing, opening MRs, or syncing GitHub.
- Future `--apply` or live modes require explicit operator authorization, receipt/rollback evidence, timeout controls, and local-main / remote-publication boundary checks.

Protected boundaries that must not be rewritten or bypassed include OpenSpec authority, `Routing trace`, `Updated Plan`, implementation-plan claim locks, local-main-first gates, remote-publication approval gates, receipt/redaction rules, user-level install receipts, browser/GUI authorization, secret redaction, and telemetry opt-in.

## Runtime Promotion Ladder

| Stage | Scope | Required evidence |
| --- | --- | --- |
| R0 source preflight | project-level | Source URLs, retrieved date, gstack command/workflow mapping, and no install/run evidence. |
| R1 dry-run runtime | project-level | Fixture-backed `analyze`, `plan-dry-run`, `review-dry-run`, `qa-dry-run`, and `ship-dry-run`; no file mutation. |
| R2 checker/runtime helper | project-level | Checker, guarded helper, tests, OpenSpec guard wiring, CI manifest registration, and docs registry entry. |
| R3 user-level install | user-level deferred | Explicit authorization, immutable source pin, Codex-host install receipt, rollback pointer, and redaction evidence. |
| R4 smoke runtime | user-level deferred | Bounded help/status/dry-run smoke receipt with timeout and rollback evidence. |
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
- [ ] Later implementation: add `check_gstack_codex_delivery_loop.py` with focused fixtures and JSON output.
- [ ] Later implementation: add `gstack_codex_delivery_loop_runtime.py` with `analyze`, dry-run stage checks, and guarded future apply/live modes.
- [ ] Later implementation: register focused tests, OpenSpec guard wiring, and CI manifest coverage.
- [ ] Later runtime promotion: R3-R5 user-level install, browser QA, hooks, gbrain-like memory, telemetry, and always-on routing require explicit authorization plus receipt/rollback/redaction evidence.
<!-- TASK_BACKLOG_END -->

## Verification Gates

- `python tools/check_implementation_plan_rules.py --root . --json` - validate implementation plan registry, bilingual companion, parent-plan, size, and evidence-index rules.
- `python tools/run_openspec_guard.py --root .` - validate OpenSpec state and repository governance guard wiring.
- `python tools/check_precommit_update_archive.py --root . --json` - validate required update/archive review before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - run shared local CI gate before integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - run local MR review before local main integration.

Later code work must also add focused checker and runtime helper tests.

## Acceptance Criteria

- This child plan is registered as active and linked from the parent plan.
- The plan records gstack source references and Codex-local checker/runtime targets.
- The plan states that this package does not clone, install, enable, smoke-run, or live-run gstack.
- R3-R5 user-level activation remains deferred and receipt-gated.
- Future runtime cannot bypass local-main-first gates, remote-publication approval, browser/GUI authorization, telemetry opt-in, or receipt/redaction boundaries.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 documentation package: branch `plan-gstack-codex-delivery-loop-20260606` creates this active Phase 4 child plan, records `garrytan/gstack` and `gstack.lol` references, and leaves checker/runtime code to a later implementation package.
<!-- EVIDENCE_INDEX_END -->
