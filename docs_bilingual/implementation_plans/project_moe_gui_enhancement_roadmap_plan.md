---
doc_id: project_moe_gui_enhancement_roadmap_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.md
status: active
plan_readiness: ready-for-implementation
implementation_status: runtime-slice-0.2.31-local-complete-target-install-pending
implementation_lane: project_moe_gui_enhancement
parent_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
doc_class: implementation_plan
created_at: 2026-06-07
last_reviewed_at: 2026-06-07
scope: project_moe_gui_post_0_2_30_enhancement
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
  - docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.md
---

# Project MOE GUI Enhancement Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use `superpowers:executing-plans` for task-by-task implementation. Use `superpowers:subagent-driven-development` only when the active platform and user authorization allow native delegation. Track every implementation item with checkbox items. Run task-local verification before moving to the next task.

**Goal:** Bring the Project MOE GUI from the current functional operator console to a stronger product-grade local GUI with persistent expert workbench artifacts, stricter visual gates, better Sessions usability, and read-only multi-project install/upgrade visibility.

**Architecture:** Keep `D:/PythonProject_langgraph` as the Phase 2 toolchain source of truth and keep target projects as Phase 1 owners. The GUI may create structured handoff artifacts and local runtime history, but it must not directly start Codex, native subagents, durable teams, LangGraph workflows, model APIs, or bypass the target project's Phase 1 CLI gates.

**Tech Stack:** Python CLI/checkers, PySide6 shared runtime, QML Material shell, JSON view model, target-project Phase 1 CLI contract, local runtime artifact directories, local CI manifest, local-first Git flow.

---

## 0. Current Review Verdict

Project MOE GUI `0.2.30` was usable as a real PySide6 operator console. The first roadmap runtime batch is now implemented locally as toolchain `0.2.31`, closing the local visual-gate, Workbench artifact, Sessions usability, UI-state, and read-only multi-project panel work. Target-project reinstall and acceptance validation for `D:/PythonProject_paper_suggest` remain a separate follow-up before claiming that target project is on the latest GUI.

Completeness baseline:

| Area | Current state | This plan closes |
| --- | --- | --- |
| Visual gate | Covers the main pages at `1180x720` and catches non-scroll overflow | Multi-size, long-content, dense session/lens fixtures, and local gate wiring |
| Expert Workbench | Generates a handoff package preview and clipboard/runtime package | Drafts, history, session binding, filtering/reuse, and carrier-shaped export artifacts |
| Sessions page | Supports session on/off, lens/category apply/clear, and readback | Search, filter, sort, effective-state explanation, override conflict hints |
| UI polish | Has card/sidebar/dark styling | Product-grade empty/error/loading/help states and tighter layout polish |
| Multi-project operation | Installer/updater/checker exist as CLI surfaces | Read-only install-status panel, version-lag detection, dry-run update plan, rollback hint |

Status interpretation:

- `status: active` means this is the active child roadmap for post-`0.2.30` GUI enhancement.
- `implementation_status: runtime-slice-0.2.31-local-complete-target-install-pending` means this file records the ordered implementation scope; it is not evidence that runtime work has already shipped.
- The parent plan remains the source of broad Project MOE GUI architecture and readiness-lane governance.
- This plan does not authorize remote publication; remote GitLab/GitHub actions still require explicit user approval.

## Current Status
<!-- CURRENT_STATUS_START -->

- [x] Status: active child implementation plan for post-0.2.30 Project MOE GUI enhancements.
- [x] Local runtime batch complete: toolchain `0.2.31` implements the first enhancement batch in this repository.
- [x] Runtime artifact boundary recorded: Workbench drafts/history/queue are written under target `.project-runtime/project_moe_gui/`, and `.project-runtime/` is ignored by Git.
- [ ] Target-project follow-up pending: update/install the new toolchain into `D:/PythonProject_paper_suggest`, then rerun install check, readiness, launcher preflight, and visual validation there.

<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Slice A: make visual render gates multi-size and fixture-profile aware.
- [x] Slice B: add Expert Workbench drafts, history, session binding, filtering, and structured exports.
- [x] Slice C: improve Sessions search, filter, sort, and effective-state explanations.
- [x] Slice D: add product-grade loading, empty, error, and help states.
- [x] Slice E: add read-only multi-project install and upgrade status panel.
- [ ] Target-project acceptance: install/update `0.2.31` into `D:/PythonProject_paper_suggest` and run target preflight plus multi-size visual validation.

<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- Toolchain version evidence: `tools/project_moe_gui_toolchain/src/project_moe_gui/__init__.py` sets `TOOLCHAIN_VERSION = "0.2.31"`.
- Visual gate evidence: `tools/project_moe_gui_toolchain/visual_render_check.py` defaults to `1180x720`, `1366x768`, and `1440x900`, and supports `default`, `long-content`, and `dense-sessions` fixture profiles.
- Workbench artifact evidence: `workbench_artifacts.py` creates draft/history/handoff-queue artifacts without executing Codex, subagents, durable teams, LangGraph workflows, model APIs, or target-state writes.
- GUI evidence: `gui_shell.py` and `ProjectMoeGui.qml` expose real Workbench save/export bridge methods, Sessions search/filter/sort/effective-state explanations, UI states, and a read-only multi-project panel.
- Test evidence: targeted checks passed for QML source coverage, visible launch smoke wiring, and visual render checker behavior; full regression must be rerun before commit.
- Pending evidence: target-project install/update and acceptance validation for `D:/PythonProject_paper_suggest` have not been performed in this local runtime batch.

<!-- EVIDENCE_INDEX_END -->

## 1. Boundaries and Carrier Semantics

- MOE experts are lenses or routing semantics, not execution carriers.
- The main session, a native subagent, a durable team, and a LangGraph workflow are carriers that may consume a MOE brief.
- Expert Workbench may generate carrier-shaped artifacts for `main-session`, `subagent`, `durable-team`, and `langgraph-workflow`.
- Expert Workbench must not directly execute those carriers in this plan.
- A future one-click carrier execution slice must be separately governed because it would need platform subagent availability, durable-team threshold evidence, LangGraph state evidence, and approval gates.
- GUI history and draft artifacts are runtime artifacts; they are not committed to the target project by default.
- The GUI must never copy a target project's private `MOE.md` body or native agent developer instructions into shared toolchain artifacts.

## 2. Runtime Artifact Contract

Default target-project runtime directory:

```text
<target-project>/.project-runtime/project_moe_gui/
  workbench_drafts/
  expert_history/
  handoff_queue/
  visual_gate/
```

Minimum handoff artifact fields:

```json
{
  "schema_version": 1,
  "artifact_kind": "project_moe_gui_handoff",
  "created_at": "<iso8601>",
  "target_project": "<redacted-or-normalized-project-path>",
  "session_display_id": "<display-only-session-id>",
  "session_key_hash": "<stable-hash>",
  "selected_lenses": [],
  "selected_categories": [],
  "handoff_target": "main-session|subagent|durable-team|langgraph-workflow",
  "task_template_id": "<template-id>",
  "brief_text": "<operator-provided-brief>",
  "status": "draft|copied|queued|completed|superseded"
}
```

Rules:

- `session_display_id` must remain display-only and must not expose raw private session identifiers.
- `brief_text` is operator-provided content, not private prompt source content.
- `selected_lenses=[]` keeps the existing meaning: all available lenses are allowed for that session unless the session is disabled.
- History files must be append-only or status-transitioned with explicit timestamps; do not silently overwrite completed artifacts.
- Dirty target projects still fail closed for write/update operations; read-only status and history reads may continue.

## 3. Implementation Checklist

### Slice A: Visual Gate P0

- [x] Add default visual sizes: `1180x720`, `1366x768`, and `1440x900`.
- [x] Add `--fixture-profile default|long-content|dense-sessions` to the visual render checker.
- [x] Add long session names, long lens names, many sessions, many categories, and many lenses to generated fixtures.
- [x] Keep real PySide6 offscreen rendering as an explicit command, not a mandatory every-test default.
- [x] Add unit tests for size parsing, default sizes, fixture generation, and overflow detection.
- [x] Keep the light visual checker covered by the existing Project MOE GUI regression test suite; no separate heavy offscreen render was added to every-test defaults.
- [ ] Run target-project visual validation against `D:/PythonProject_paper_suggest` after installing the new toolchain.

### Slice B: Expert Workbench P1

- [x] Add draft-save support for handoff packages.
- [x] Add expert result history records with status transitions.
- [x] Add session binding for generated briefs.
- [x] Add filtering by session, handoff target, lens, category, and status.
- [x] Add a structured export action for each handoff target.
- [x] Preserve the rule that export means artifact generation or clipboard copy, not carrier execution.
- [x] Add tests for artifact schema, redaction boundary, draft/history lifecycle, and carrier export shape.

### Slice C: Sessions Usability P1

- [x] Add Sessions search text.
- [x] Add Sessions filter mode: all, enabled, disabled, blocked or invalid.
- [x] Add Sessions sort keys: last seen, display id, label, and effective lens mode.
- [x] Show effective lens/category mode for the selected session.
- [x] Show project-default versus session-override conflict hints.
- [x] Add no-session, no-search-result, and readiness-blocked empty states.
- [x] Add tests for view-model filtering, sorting, and explanation text.

### Slice D: UI Product Polish P2

- [x] Add loading, empty, error, and help states to the main QML pages.
- [x] Tighten card spacing and action hierarchy without introducing a new GUI framework.
- [x] Keep QFluentWidgets as an evaluated optional path only until license review is complete.
- [x] Add a license-review note if QFluentWidgets remains listed as a future option.
- [x] Extend visual fixtures to cover empty/error/loading/help states.

### Slice E: Multi-Project Install/Upgrade Panel P2

- [x] Add a read-only project registry input contract.
- [x] Add install-status scanning for explicitly listed projects only.
- [x] Show installed GUI version, source toolchain version, dirty status, readiness status, and version lag.
- [x] Generate dry-run update plan and rollback hint without writing target projects.
- [x] Keep real update/apply actions behind existing installer/updater gates.
- [x] Add tests for registry parsing, stale version detection, dirty fail-closed behavior, and dry-run output.

## 4. Verification Plan

Minimum local verification before each local commit:

```powershell
python .\tools\check_precommit_update_archive.py --root . --json
python .\test\project_moe_gui_toolchain.test.py
```

Runtime verification before integration:

```powershell
python .\tools\project_moe_gui_toolchain\visual_render_check.py --target-project D:\PythonProject_paper_suggest --size 1180x720 --size 1366x768 --size 1440x900
D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json
```

Repository integration gate:

```powershell
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

Acceptance criteria:

- Multi-size visual check reports no text or non-scroll-container overflow.
- Long-content and dense-session fixtures render without hidden required controls.
- Expert Workbench can save, list, filter, copy, and export handoff artifacts.
- Sessions page can search, filter, sort, explain effective state, and show override conflicts.
- Multi-project panel is read-only by default and does not scan outside explicitly configured projects.
- Target-project dirty state still blocks write/update flows.

## 5. Rollback and Local Integration

- Create a feature worktree and branch for each implementation batch.
- Commit each completed slice or coherent batch locally.
- Before merging to local `main`, run the precommit update/archive gate and local validation.
- Use the repository local-flow helper for local `main` integration when the batch is ready.
- Preserve rollback refs and completed receipts.
- Clean integrated feature worktrees and local feature branches after local `main` integration.
- Stop at the remote-publication gate unless the user explicitly approves GitLab/GitHub publication.
