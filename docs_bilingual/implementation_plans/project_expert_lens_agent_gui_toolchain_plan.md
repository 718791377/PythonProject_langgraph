---
doc_id: project_expert_lens_agent_gui_toolchain_plan
lang: en
status: active
plan_readiness: canonical-rename-ready-for-runtime-implementation
doc_class: implementation_plan
created_at: 2026-06-17
updated_at: 2026-06-17
source_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
legacy_alias_policy: preserve-project-moe-compatibility
---

# Project Expert Lens Agent GUI Toolchain Implementation Plan

> **For agentic workers:** implement this plan with local-main-first isolation. Treat `Project MOE` as a legacy compatibility name only. Preserve `project_moe` runtime ABI until installed target projects have migrated. GUI expert-lens selection is routing input, not native-subagent or durable-team evidence.

**Goal:** Rename and extend the former Project MOE Agent GUI into **Project Expert Lens Agent GUI**. The product manages agent-like expert lenses for each target project and each Codex session; it does not describe a large-model Mixture-of-Experts architecture.

**Architecture:** This repository owns the reusable GUI toolchain, launchers, installer, checker, PySide6/QML shell, and validation fixtures. Target projects own their sessions, state, private prompts, and Phase 1 CLI. The GUI writes only through the target-project CLI contract and may generate handoff packages for the main session, native experts, durable team, persistent team, or LangGraph workflow.

**Compatibility:** Keep existing `project_moe_gui`, `project-moe-gui.cmd`, `tools/project_moe_gui/`, `thesis-moe-*`, `list-lenses`, `set-lenses`, and `clear-lenses` as compatibility aliases. Prefer new visible wording and new wrapper names: `Project Expert Lens Agent GUI`, `project-expert-lens-gui`, `expert lens`, `expert_lenses`.

---

## Current status

<!-- CURRENT_STATUS_START -->

- Status: active plan, ready for a two-stage local-main-first rollout.
- Stage A: document the canonical naming and compatibility contract, register the plan, commit, and integrate to local `main`.
- Stage B: implement runtime, QML, launcher, Workbench, and test changes, then commit and integrate to local `main`.
- Remote publication: out of scope unless the user explicitly requests GitLab/GitHub publication.

<!-- CURRENT_STATUS_END -->

## Naming model

| Layer | Canonical wording | Legacy compatibility |
| --- | --- | --- |
| Product | Project Expert Lens Agent GUI | Project MOE Agent GUI |
| Concept | expert lens | MOE lens / MOE expert |
| Script display | project-expert-lens-gui | project-moe-gui |
| JSON display fields | selected_expert_lenses, selected_expert_categories, effective_expert_lens_mode | selected_lenses, selected_categories, effective_lens_mode |
| Actions | list-expert-lenses, set-expert-lenses, clear-expert-lenses | list-lenses, set-lenses, clear-lenses |

Rules:

1. `MOE` must be described only as a historical project/toolchain term, not as a large-model internal Mixture-of-Experts implementation.
2. An expert lens is a professional perspective available to the session model.
3. Selecting a lens is not evidence that a subagent, durable worker, persistent team, or LangGraph workflow ran.
4. Runtime compatibility names stay until all installed target projects have safe migration evidence.

## Runtime and GUI requirements

1. Add canonical wrapper scripts for install, update, and check while delegating to the existing implementation.
2. Add target-project canonical launchers (`project-expert-lens-gui.cmd`, `project-expert-lens-gui-silent.vbs`) while keeping legacy launchers.
3. Add visible display labels, close-dialog wording, Workbench copy, and QML text that use Expert Lens terminology.
4. Add read/write action aliases for expert-lens verbs while preserving old action tokens.
5. Add canonical JSON mirror fields without removing legacy fields.
6. Expand Workbench handoff metadata to include `main-session`, `native-experts`, `subagent`, `durable-team`, `persistent-team`, and `langgraph-workflow`.
7. Keep old Python import package, QML bridge object names, runtime directories, and target Phase 1 compatibility paths stable.
8. Update tests so they separately assert canonical display names and legacy ABI compatibility.
9. After local `main` integration in this repository, refresh `D:\PythonProject_paper_suggest` only through the installer/update path and verify both old and new launchers.

## Orchestration boundary

- The GUI controls the available expert-lens pool for a project/session.
- The main Codex session remains the leader and decides whether to use one or more lenses directly or to route a brief to native experts, durable team, persistent team, native_omx, or LangGraph.
- The GUI may create handoff packages and copied prompts. It must not directly spawn subagents, start durable teams, start LangGraph workflows, call model APIs, or mutate remote publication state.
- Expert timeout, durable-worker stall, or provider pacing remains non-evidence and must be handled by retry, narrowed delegation, durable handoff, or main-session takeover.

## Task backlog

<!-- TASK_BACKLOG_START -->

- [x] Create the canonical bilingual implementation plan pair.
- [x] Avoid editing the oversized legacy plan as the source of naming authority; keep it as the legacy implementation history.
- [x] Register the canonical plan pair in `docs_bilingual/docs_registry.yaml`.
- [x] Run plan-stage validation; Stage A commit is being prepared.
- [x] Integrate Stage A into local `main` and clean the plan feature worktree if appropriate.
- [x] Add canonical wrapper scripts for installer/updater/checker names.
- [x] Add canonical constants and visible product labels in `project_moe_gui` runtime code.
- [x] Add canonical target-project launchers and manifest entries while preserving legacy launchers.
- [x] Add canonical action aliases and JSON mirror fields.
- [x] Update PySide6 fallback UI and QML text to Expert Lens terminology.
- [x] Update Workbench handoff wording, artifact metadata, and handoff targets.
- [x] Update tests for canonical naming and legacy ABI compatibility.
- [ ] Run focused tests, static checks, OpenSpec guard, local gate, and local MR review. Focused runtime tests passed; broader gates are pending in this worktree.
- [ ] Integrate Stage B into local `main` and stop before remote publication.
- [ ] Refresh the A project install and verify old and new launchers if target-project write approval/sandbox access is available.

<!-- TASK_BACKLOG_END -->

## Evidence index

<!-- EVIDENCE_INDEX_START -->

- 2026-06-17 Stage A plan registration evidence: docs registry entry added; `git diff --check`, `tools/check_implementation_plan_rules.py --root . --json`, and `tools/check_precommit_update_archive.py --root . --json` passed before commit.
- 2026-06-17 Stage B focused runtime evidence: canonical wrappers, launchers, action aliases, JSON mirror fields, Workbench targets, QML wording, and tests were implemented in `feature/implement-expert-lens-gui-runtime`; `python test/project_moe_gui_toolchain.test.py` passed 108 tests before broader gates.
- pending implementation evidence: Stage B broader gates, local-main integration, and target-project refresh are still pending.

<!-- EVIDENCE_INDEX_END -->

## Validation plan

- Plan-stage checks: `git diff --check`, `python tools/check_implementation_plan_rules.py --root . --json`, `python tools/check_precommit_update_archive.py --root . --json`.
- Focused runtime tests: `python -m unittest test.project_moe_gui_toolchain.test`.
- Repo gates before local main integration: `python tools/run_openspec_guard.py --root .`, `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_gate.ps1 -StepTimeoutSeconds 1200`, and `powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1`.
- Optional visual verification: run the GUI visual render checks for Sessions and Workbench when the shared PySide6 runtime is available.

## Rollback

- Stage A rollback: remove this plan pair and docs registry entry.
- Stage B rollback: remove new canonical wrappers and visible aliases, but do not delete existing managed `project_moe` target-project artifacts.
- Target-project rollback: use the installer manifest and generated rollback notes in the target project.
