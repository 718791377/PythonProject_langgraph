---
doc_id: stop_slop_caveman_response_density_runtime_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/stop_slop_caveman_response_density_runtime_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
stage: Stage B follow-up child plan
phase: 4
batch: 3
confirmation_required: true
---

# Stop-Slop and Caveman Response Density Runtime Plan

> For agentic workers: use `superpowers:executing-plans`; use parallel subagents only for disjoint write sets. This package records the checker plus runtime target only; it does not create scripts.

## Goal

Add a Phase 4 child plan that turns the `stop-slop` and `caveman` references into a project-level response-density checker and guarded local runtime target for Codex conversation output.

## Source References

| Reference | Required carry-forward |
| --- | --- |
| https://github.com/hardikpandya/stop-slop | Anti-slop checks: remove filler, avoid predictable phrases and structures, require active voice, forbid em dashes, vary rhythm, and score directness, rhythm, trust, authenticity, and density. |
| https://github.com/JuliusBrussee/caveman | Output-compression pattern: cut output tokens while preserving technical accuracy; protect code, URLs, paths, command arguments, and technical tokens from rewrite. |

## Scope Decision

- Level: project-level governance and project-level runtime plan for `D:/PythonProject_langgraph` first.
- Parent: `docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md`.
- Phase: Phase 4, because this affects conversation-surface quality and output density.
- This package: plan, registry, and parent index update only; no checker, runtime helper, hook, skill install, MCP wrapper, or user-level config mutation.
- Later implementation: must reach checker plus runtime level before any readiness claim.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: active child-plan definition; code work is not started.
Stage: documentation package records the checker plus runtime requirement and source links.
Owner session: `plan-stop-slop-caveman-runtime-20260606` owns this plan-document package only.
Current gate: validate implementation-plan rules, OpenSpec guard, precommit update/archive review, local gate, and local MR review before local main integration. Remote publication is not authorized.
Runtime boundary: no Stop-Slop or Caveman runtime is installed, enabled, invoked as a hook, or promoted to user level by this package.
<!-- CURRENT_STATUS_END -->

## Checker and Runtime Target

The later code package must provide these repo-local surfaces before the plan may claim R2 readiness:

- `tools/check_stop_slop_caveman_response_density.py` validates response samples, fixtures, and selected documentation snippets for stop-slop and density rules.
- `tools/stop_slop_caveman_runtime.py analyze` returns JSON diagnostics without rewriting input.
- `tools/stop_slop_caveman_runtime.py rewrite --dry-run` proposes a shorter rewrite without writing files.
- `tools/stop_slop_caveman_runtime.py rewrite --apply --operator-confirmation` is allowed only for explicit files or text passed by the operator and must preserve protected spans.
- Tests must cover valid and invalid slop examples, protected code blocks, protected URLs, protected paths, protected CLI arguments, protected schema keys, Chinese explanatory text, and conversation labels.

Protected spans that must never be rewritten by the checker/runtime include code fences, inline code, URLs, file paths, CLI arguments, JSON/YAML keys, OpenSpec requirement keywords, evidence tokens, blocker tokens, `Routing trace`, and `Updated Plan`.

## Runtime Promotion Ladder

| Stage | Scope | Required evidence |
| --- | --- | --- |
| R0 source preflight | project-level | Source URLs, retrieved date, rule mapping, and no install/run evidence. |
| R1 dry-run runtime | project-level | Fixture-backed `analyze` and `rewrite --dry-run`; no file mutation. |
| R2 checker/runtime helper | project-level | Checker, guarded helper, tests, OpenSpec guard wiring, CI manifest registration, and docs registry entry. |
| R3 user-level install | user-level deferred | Explicit authorization, immutable source pin, install/update receipt, rollback pointer, and redaction evidence. |
| R4 smoke runtime | user-level deferred | Bounded help/status/safe rewrite smoke receipt with timeout and rollback evidence. |
| R5 active-candidate | user-level deferred | Explicit active-candidate receipt before hooks, global skill activation, MCP shrink, or always-on compression. |

## File Ownership

This child plan owns its plan files and the future checker/runtime names above. It does not own canary placement, `Routing trace` semantics, `Updated Plan` rendering, user-level skill installation, MCP Router configuration, consumer-project injected context files, or global Codex launcher profiles.

## Parallel Session Contract

One session may claim this implementation plan at a time. Later code work can run beside unrelated Phase 4 work only if docs registry, CI manifest, OpenSpec guard wiring, and conversation-surface fixtures have a serialized hotspot owner.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Create this child plan and Chinese companion.
- [x] Record Stop-Slop and Caveman reference links.
- [x] Require later checker plus runtime implementation rather than pure prose governance.
- [ ] Later implementation: add `check_stop_slop_caveman_response_density.py` with focused fixtures and JSON output.
- [ ] Later implementation: add `stop_slop_caveman_runtime.py` with `analyze`, `rewrite --dry-run`, and guarded `rewrite --apply`.
- [ ] Later implementation: register focused tests, OpenSpec guard wiring, and CI manifest coverage.
- [ ] Later runtime promotion: keep R3-R5 user-level install, hooks, MCP shrink, and always-on compression behind explicit authorization and receipt/rollback/redaction evidence.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- `python tools/check_implementation_plan_rules.py --root . --json` - validates implementation-plan registry, bilingual companion, parent-plan, size, and evidence-index rules.
- `python tools/run_openspec_guard.py --root .` - validates OpenSpec state plus repository governance guard wiring.
- `python tools/check_precommit_update_archive.py --root . --json` - validates required update/archive review before commit.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate before integration.
- `powershell -NoProfile -ExecutionPolicy Bypass -File ./tools/ci/local_mr_review.ps1` - runs the local MR review gate before local main integration.

Later code work must also add focused tests for the checker and runtime helper.

## Acceptance Criteria

- This child plan is registered as active and linked to the parent plan.
- The plan records both reference sources and the project-specific checker/runtime target.
- The plan states that this package does not create or enable runtime code.
- R3-R5 user-level activation remains deferred behind explicit authorization and receipts.
- Protected technical surfaces and fixed conversation labels cannot be rewritten by the future runtime.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-06 documentation package: branch `plan-stop-slop-caveman-runtime-20260606` creates this active Phase 4 child plan, records `hardikpandya/stop-slop` and `JuliusBrussee/caveman` as references, and keeps checker/runtime code for a later implementation package.
<!-- EVIDENCE_INDEX_END -->
