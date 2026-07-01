---
doc_id: transient_operator_surface_replay_filtering_plan
lang: en
status: active
doc_class: implementation_plan
zh_cn_path: docs_bilingual/implementation_plans/transient_operator_surface_replay_filtering_plan.zh-CN.md
parent_plan: docs_bilingual/implementation_plans/conversation_surface_single_panel_runtime_alignment_plan.md
confirmation_required: true
---

# Transient Operator Surface Replay Filtering Plan

## Goal

Correct the `Routing trace` and `Updated Plan` boundary: they are current-session, operator-visible transient runtime surfaces. They may appear in the live Codex UI while a turn is running, but they must not be replayed as model-readable session history after `codex resume`, restart, compacted replay, or session-history hydration. A resumed session must rerun activation and render fresh transient surfaces for the current activation instead of inheriting prior trace or plan panels.

## Current Status

<!-- CURRENT_STATUS_START -->
Status: runtime implementation in progress after plan package was integrated into local `main`
Owner session: `transient-operator-surfaces-20260616`
Current gate: implement replay filtering runtime, governance wording, tests, and template propagation
Remote publication: not authorized; stop at remote-publication gate
Last updated: 2026-06-16
<!-- CURRENT_STATUS_END -->

## Implementation Scope

- Governance and OpenSpec wording must distinguish three surfaces: live transient operator display, model-readable session history/replay, and explicit saved evidence fixtures.
- Replay filtering must remove standalone/panel-shaped `Routing trace` and `Updated Plan` surfaces from resumed assistant-visible context as `transient_operator_surface`.
- Replay filtering must fail closed when those panels are embedded in ordinary assistant prose or treated as prompt authority, using a `transient_surface_leak` blocked reason.
- Saved evidence checkers may still validate explicit trace/progress fixture files, but such fixtures must be labeled as saved evidence and must not be accepted as session-history authority.
- User-level generated instructions and both General templates must inherit the corrected live-only boundary.

## Task Backlog

<!-- TASK_BACKLOG_START -->
- [x] Commit this plan and registry entry, then integrate it into source local `main`.
- [x] Update governance/OpenSpec/installer wording from conversation-history surface to transient operator runtime surface.
- [x] Extend `session_replay_context_filtering.py` to filter standalone live panels and block embedded leaks.
- [x] Add regression tests and fixtures for resume/session-history filtering of both labels.
- [ ] Run source checks, commit runtime implementation, and integrate into source local `main`.
- [ ] Propagate the corrected boundary to `D:\PythonProject_General` and validate/merge local `main`.
- [ ] Propagate the local-only corrected boundary to `D:\PythonProject_General_2` and validate/merge local `main`.
<!-- TASK_BACKLOG_END -->

## Acceptance Criteria

- `codex resume` or session replay must not expose previous-turn `Routing trace` / `Updated Plan` panels as current assistant-visible authority.
- A current live activation may still display exactly one fresh `Routing trace` and one native/canonical `Updated Plan` panel for the current turn.
- Explicit saved evidence remains valid only when supplied to evidence checkers as saved evidence, not as session history.
- Source repo and both templates pass their local gates and local MR review, with no remote publication performed.

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Plan package integrated into local `main` at `8d4910c` before runtime edits.
- Runtime implementation now filters standalone `Routing trace` / `Updated Plan` panels as `transient_operator_surface` and blocks embedded leaks as `transient_surface_leak`.
<!-- EVIDENCE_INDEX_END -->
