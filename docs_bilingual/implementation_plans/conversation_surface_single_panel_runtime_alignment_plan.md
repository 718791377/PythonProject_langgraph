---
doc_id: conversation_surface_single_panel_runtime_alignment_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/conversation_surface_single_panel_runtime_alignment_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md
confirmation_required: true
---

# Conversation Surface Single-Panel Runtime Alignment Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development after this plan is confirmed. Steps use checkbox syntax for implementation-plan tracking only.

## Goal

Align the user-facing `Routing trace` and `Updated Plan` conversation surfaces across governance, checker fixtures, generated user-level runtime instructions, installed user-level artifacts, and the two general project templates. The fix prevents old short routing examples such as `experts_now` / `durable_team` from reappearing and prevents duplicate or nested user-visible `Updated Plan` panels.

## Source Plans

- `chinese_routing_trace_conversation_surface_plan` - prior fixed-label conversation surface plan.
- `routing_trace_structured_evidence_schema_plan` - structured routing evidence field contract.
- `codex_governance_session_visibility_and_plan_lock_plan` - plan visibility and conversation-surface boundary governance.
- `multi_plan_parallel_session_orchestration_plan` - parent orchestration plan and anti-conflict governance context.

## Scope Decision

- Priority order remains `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Repository scope: update project governance, checker/runtime source, fixtures, and user-level installer artifacts in `D:/PythonProject_langgraph`.
- User-level scope: refresh generated/installed Codex team-mode surfaces under `C:/Users/lenovo/.codex` through the repository installer, with smoke evidence only; installed artifacts are not the source of truth.
- Template scope: after repository runtime completion, update `D:/PythonProject_General` and `D:/PythonProject_General_2` so other projects and new computers inherit the clarified conversation-surface contract.
- Remote publication is out of scope unless the operator explicitly requests remote push, GitLab MR, GitLab merge, or GitHub sync.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: runtime implementation completed in `conversation-surface-runtime-20260612`; user-level runtime refreshed and smoke-verified; awaiting runtime local gate, local MR review, and local `main` integration before template sync
Owner session: `conversation-surface-runtime-20260612`
Current gate: commit runtime implementation, run local gate and local MR review, merge local `main`, then update `D:/PythonProject_General` and `D:/PythonProject_General_2`
Remote publication: not authorized; stop at the remote-publication approval gate
Last updated: 2026-06-12
<!-- CURRENT_STATUS_END -->

## File Ownership

- Plan and registry: this file, the zh-CN companion, and `docs_bilingual/docs_registry.yaml`.
- Runtime implementation slice: `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`, `.zh-CN.md`, `tools/install-codex-user-level-team-mode.ps1`, `tools/check_orchestration_collaboration_evidenceguard.py`, `tools/check_orchestration_trace_evidence.py`, relevant tests, and `test/fixtures/orchestration_prompt_independent_collaboration_parity/conversation_surface_*`.
- Template implementation slice: `D:/PythonProject_General` and `D:/PythonProject_General_2` template guidance and generated Codex agent/template assets that carry the conversation-surface contract.

## Hotspot Serialization

Only one session may own each hotspot at a time:

- user-facing `Routing trace` examples and field names
- user-facing `Updated Plan` rendering contract
- collaboration evidenceguard fixtures and validation logic
- user-level installer-generated `team-leader` instruction payload
- template AGENTS/team-leader surfaces in `PythonProject_General` and `PythonProject_General_2`

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Commit and merge this implementation plan into local `main` before runtime edits.
- [x] Update governance text so `Routing trace` uses the full checker-compatible field set and `Updated Plan` is one CLI/tree panel using checkmark (U+2714) and empty-square (U+25A1) status glyphs.
- [x] Replace old installer wording and generated examples that mention `experts_now`, `durable_team=<...>`, `checkbox/status-list semantics`, or ambiguous checklist semantics.
- [x] Harden conversation-surface checker logic and fixtures against duplicate `Updated Plan`, nested `Updated Plan`, Markdown checkbox `Updated Plan`, duplicate `Routing trace`, and old routing short fields.
- [x] Run targeted checker tests, OpenSpec guard, and pre-commit update/archive checks for the runtime slice.
- [x] Reinstall or refresh user-level team-mode runtime from repository source and smoke-search installed artifacts for old wording, including the generated `user-level-team-mode-model-instructions.md` cache.
- [ ] Run full local gate and local MR review for the committed runtime implementation.
- [ ] Merge the runtime implementation into local `main` and stop at the remote-publication gate.
- [ ] Update `D:/PythonProject_General` with a plan commit followed by a template implementation commit and local main integration.
- [ ] Update `D:/PythonProject_General_2` with a plan commit followed by a template implementation commit and local main integration.
<!-- TASK_BACKLOG_END -->

## Validation Gates

- `python test/check_orchestration_collaboration_evidenceguard.test.py` - verifies conversation-surface evidenceguard behavior.
- `python test/check_orchestration_trace_evidence.test.py` - verifies full routing trace evidence fields.
- `python tools/run_openspec_guard.py --root .` - validates OpenSpec and repository governance guards.
- `python tools/check_precommit_update_archive.py --root . --json` - checks pre-commit update and archive readiness.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local MR review gate.
- User-level smoke: search installed user-level surfaces for `checkbox/status-list semantics`, `experts_now`, `Routing trace: phase=..., experts_now`, and old generated `durable_team=<selected|not_selected>` examples.
- Template smoke: search both template repositories for the same old wording and confirm any remaining `Updated Plan` guidance says single CLI/tree checkmark/empty-square panel.

## Acceptance Criteria

- `Routing trace` examples in governance/runtime surfaces use the full field names: `phase`, `capability_chain`, `backend_default`, `backend_ready`, `experts`, `durable_workflow`, `persistent_team`, `main_session_escalation`, `approval_timeout_risk`, `approval_receipt`, and `why`.
- Current user-facing guidance does not present `experts_now` or `durable_team=<selected|not_selected>` as the live routing trace contract.
- `Updated Plan` guidance says one user-visible CLI/tree progress panel using checkmark (U+2714) and empty-square (U+25A1) status glyphs; Markdown checkbox syntax remains limited to implementation-plan files.
- Checker fixtures reject duplicate/nested `Updated Plan` output and duplicate/old-field `Routing trace` output.
- User-level installed artifacts and both templates pass residual old-wording smoke searches.
- Repository and template changes are committed and merged into their local `main` branches only; remote publication remains gated.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Plan integration: local `main` contains plan commit `ea9a442`.
- Runtime checks passed: `python test/check_orchestration_collaboration_evidenceguard.test.py`, `python test/check_orchestration_trace_evidence.test.py`, `python test/check_stop_slop_caveman_response_density.test.py`, `python test/check_fanout_write_ownership_evidence.test.py`, `python test/check_windows_cleanup_output_control.test.py`.
- Installer test passed: `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`.
- User-level install executed with `tools/install-codex-user-level-team-mode.ps1 -Force`; manifest listed `C:/Users/lenovo/.codex/state/user-level-team-mode-model-instructions.md` as a generated managed artifact.
- User-level smoke passed: `team-leader.toml`, `codex-routing-policy.ps1`, `_codex-user-level-team-mode.ps1`, `_codex-user-level-team-mode-launcher.ps1`, and `user-level-team-mode-model-instructions.md` had no `experts_now`, no old `durable_team=<selected|not_selected>` example, no `checkbox/status-list semantics`, and no Markdown checkbox `Updated Plan` surface.
- Repository guards passed: `python tools/check_precommit_update_archive.py --root . --json`, `python tools/check_launcher_payload_context_boundary.py --root . --json`, and `python tools/run_openspec_guard.py --root .`.
- Pending evidence: runtime local gate, local MR review, local `main` integration, and both template repository updates.
<!-- EVIDENCE_INDEX_END -->
