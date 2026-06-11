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
- This R4 implementation package adds repo-local checker/runtime/smoke-receipt code only; it does not install user-level tools, enable hooks, create MCP wrappers, or mutate user-level configuration.
- Later implementation: must reach checker plus runtime level before any readiness claim.
- Remote publication: out of scope unless the user explicitly asks for remote publication.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: implemented-local
Status: R6 live-executed
Stage: R6 live-runtime receipt coverage package for Stop-Slop/Caveman response-density runtime.
Owner session: `implement-multi-plan-family-r6-live-runtime-20260611` updates the strict parent-family checker; existing accepted receipts remain the live runtime evidence source.
R6 evidence: `.omx/r6-live-runtime/receipts/` contains accepted `live-executed` evidence for lane `stop-slop-caveman-response-density-runtime`, validated by `tools/check_r6_live_runtime_receipts.py --require-coverage` and `tools/check_multi_plan_family_r6_live_runtime.py --require-coverage`.
Runtime boundary: this status update performs no browser/GUI action, no WXWork message send, no harness job, no Spec Kit apply, no user-level config mutation, and no remote publication; it reconciles the plan with already accepted hash-only/redacted R6 receipts.
Priority order: `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
Last updated: 2026-06-11
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
- [x] Later implementation: add `check_stop_slop_caveman_response_density.py` with focused fixtures and JSON output.
- [x] Later implementation: add `stop_slop_caveman_runtime.py` with `analyze`, `rewrite --dry-run`, and guarded `rewrite --apply`.
- [x] Later implementation: register focused tests, OpenSpec guard wiring, and CI manifest coverage.
- [x] Later runtime promotion: keep R3-R5 user-level install, hooks, MCP shrink, and always-on compression behind explicit authorization and receipt/rollback/redaction evidence; R4 accepts blocked receipts but only smoke-tested safe receipts count as positive evidence.
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
- The plan states that this package creates repo-local runtime helpers only and does not install or enable user-level runtime behavior.
- R3-R5 user-level activation remains deferred behind explicit authorization and receipts.
- Protected technical surfaces and fixed conversation labels cannot be rewritten by the future runtime.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- 2026-06-07 R5 active-candidate gate: branch `implement-r5-runtime-governance-batch-20260607` adds shared active-candidate receipt validation for Stop-Slop/Caveman response-density runtime. Evidence requires authorization receipt, owner lease, target/action allowlist, timeout release, redacted transcript, rollback pointer/readiness, cleanup evidence, authority decision with the exact priority order `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`, and `remote_publication_mutated=false`. Focused validation: `python test\check_r5_active_candidate_receipts.test.py` plus lane-specific focused tests described in the OpenSpec verification report. No real user-level install/start/send/browser/GUI/MCP/harness/Spec Kit action and no remote mutation occurs in this package.
- 2026-06-06 documentation package: branch `plan-stop-slop-caveman-runtime-20260606` creates this active Phase 4 child plan, records `hardikpandya/stop-slop` and `JuliusBrussee/caveman` as references, and keeps checker/runtime code for a later implementation package.
- 2026-06-07 R4 implementation package: branch `implement-stop-slop-caveman-r4-20260607` adds `tools/check_stop_slop_caveman_response_density.py`, `tools/stop_slop_caveman_runtime.py`, `tools/check_stop_slop_caveman_smoke_receipts.py`, focused test `check_stop_slop_caveman_response_density.test.py`, OpenSpec guard wiring, CI manifest registration, and safety-rule script backing. Focused RED/GREEN evidence: `python test\check_stop_slop_caveman_response_density.test.py` failed before scripts existed, then passed 8 tests after implementation, including real Unicode punctuation coverage.
- 2026-06-07 focused validation evidence: `python tools\check_stop_slop_caveman_response_density.py --root . --json`, `python tools\check_stop_slop_caveman_smoke_receipts.py --root . --json`, `python tools\check_safety_rule_script_backing.py --root . --json`, `openspec validate implement-stop-slop-caveman-response-density-r4 --strict`, and `git diff --check` passed after LF normalization.
- 2026-06-07 resumed integration evidence: the current round reactivated the `stop-slop-caveman-r4-20260607` claim and merged CI manifest, OpenSpec guard, and safety-rule registry against the current `main` baseline, preserving Spec Kit, Codex harnesses, and gstack entries while adding Stop-Slop/Caveman R4 guard steps.
- 2026-06-07 archive validation evidence: `openspec archive implement-stop-slop-caveman-response-density-r4 --yes` created archive path `openspec/changes/archive/2026-06-07-implement-stop-slop-caveman-response-density-r4/` and stable spec `openspec/specs/codex-user-level-response-density-runtime/spec.md`; `openspec validate --all --strict`, `python tools\check_precommit_update_archive.py --root . --json`, `python tools\check_stop_slop_caveman_response_density.py --root . --json`, and `python tools\check_safety_rule_script_backing.py --root . --json` passed after archive.
<!-- EVIDENCE_INDEX_END -->
