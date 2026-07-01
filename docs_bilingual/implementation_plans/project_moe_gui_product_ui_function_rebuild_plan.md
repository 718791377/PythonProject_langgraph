---
doc_id: project_moe_gui_product_ui_function_rebuild_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_gui_product_ui_function_rebuild_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-06-08
source_plan: project_moe_gui_product_ui_function_rebuild_confirmed
related_plans:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
  - docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
---

# Project MOE GUI Product UI / Function / Session Reconciliation Rebuild Plan

## 0. Execution Verdict

This plan has upgraded Project MOE GUI from the former `0.2.31` QML Material operator console to an accepted `0.2.32` product-grade local GUI. Each target project gets a project-scoped MOE console that displays and controls only its own sessions. Each session can independently enable or disable MOE, select concrete MOE lenses or MOE categories, and see the final effective lens set. The GUI must support English, bilingual, and Chinese display modes, with bilingual as the default.

This plan also strengthens Expert Workbench. Workbench remains a safe handoff surface: it does not start Codex, native subagents, durable teams, LangGraph workflows, or model APIs. It only generates, saves, copies, and exports handoff packages and provides pre-dispatch checks.

This plan adds session identity, discovery, and reconciliation. The GUI must show full session identifiers, attempt read-only discovery of local Codex sessions, reconcile them with project MOE state, and never hide or downgrade an ordinary session only because its name contains words such as `smoke`, `test`, `fixture`, or `generated`. A session such as `smoke-session-final` must be shown by default unless it has explicit test metadata.

## 1. Current State and Problems

### 1.1 Current Capabilities

- B repository source of truth: `tools/project_moe_gui_toolchain/`.
- Target A: `D:/PythonProject_paper_suggest` has Project MOE GUI `0.2.32` installed and accepted.
- Install check reports matching installed/source toolchain versions.
- Current GUI supports project default on/off, session on/off, session lens/category state, Workbench handoff draft/export, multi-size visual rendering checks, and the QFluentWidgets / Qt Widgets product primary shell.
- Shared PySide6 runtime lives at `D:/PythonProject_langgraph/.shared_runtimes/pyside6`; consumer projects do not install PySide6 by default.
- QFluentWidgets runtime and GPLv3/commercial license manifest checks exist; the primary shell is `qfluentwidgets-qtwidgets`, and QML Material is an explicit fallback only.

### 1.2 Problems

- The primary GUI is still a QML Material operator console and does not meet the product-grade UI target.
- The current Projects page can mislead users into thinking the target-project GUI controls multiple projects.
- The UI is mostly English and has no language switch.
- MOE categories and concrete lenses are independent selection surfaces; category selection does not update concrete lenses.
- Workbench is still closer to a text package generator than a session-bound safe handoff workbench.
- Sessions only show registered MOE session state, not all known Codex sessions, and lack full identifiers, mapping evidence, and reconciliation explanations.
- Session display must not use name heuristics to hide sessions; `smoke-session` and `smoke-session-final` can be ordinary sessions.


## Current Status
<!-- CURRENT_STATUS_START -->

- [x] Requirements are frozen: product-grade Fluent Widgets shell, bilingual default, project-scoped sessions, session reconciliation, tri-state MOE category linkage, and Workbench safe handoff.
- [x] `0.2.31` baseline is confirmed: target A previously had the QML primary experience installed.
- [x] B runtime product rebuild is implemented, validated, and merged to local main: `e041f59`.
- [x] Target A install and visible-launch acceptance are complete: target A local main commit `b4c5333`.

<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Slice 0: create this product rebuild plan.
- [x] Slice 1: Fluent Widgets primary shell.
- [x] Slice 2: i18n and language switching.
- [x] Slice 3: project boundary and page reduction.
- [x] Slice 4: session list, Codex discovery, and reconciliation.
- [x] Slice 5: MOE lens/category tri-state linkage.
- [x] Slice 6: Workbench safe handoff enhancements.
- [x] Slice 7: visual and automated validation.
- [x] Slice 8: target A install acceptance.

<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- B source of truth: `tools/project_moe_gui_toolchain/`.
- Target A: `D:/PythonProject_paper_suggest`.
- Current target A installed toolchain baseline before Slice 8: `0.2.31`.
- Target A installed toolchain version after Slice 8: `0.2.32`, target A local main commit `b4c5333`.
- B source runtime version after Slice 1-7: `0.2.32`, B local main commit `e041f59`.
- Default source shell after Slice 1-7: QFluentWidgets / Qt Widgets (`qfluentwidgets-qtwidgets`); QML Material remains explicit fallback.
- B directed test evidence: `python .\test\project_moe_gui_toolchain.test.py` -> `Ran 91 tests ... OK`.
- B visual evidence: `visual_render_check.py` product Widgets shell, profiles `long-content` and `dense-sessions`, sizes `1180x720`, `1366x768`, `1440x900`, sections `overview sessions workbench diagnostics settings` -> `ok=true`.
- Slice 8 install check: `python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project D:/PythonProject_paper_suggest --json` -> `ok=true`, `status=up_to_date`, installed/target version `0.2.32`.
- Slice 8 launcher preflight: `D:/PythonProject_paper_suggest/project-moe-gui.cmd --preflight --json` -> `ok=true`, `product_shell_contract=project-moe-gui-product-widgets-v1`, `primary_shell=qfluentwidgets-qtwidgets`, `qfluentwidgets_status.ok=true`, Phase1 readiness `ready`.
- Slice 8 target A visual evidence: `visual_render_check.py --target-project D:/PythonProject_paper_suggest --shell widgets`, profiles `long-content` and `dense-sessions`, sizes `1180x720`, `1366x768`, `1440x900`, sections `overview sessions workbench diagnostics settings` -> `ok=true`; screenshot dirs `.tmp/paper_suggest_moe_visual_long/` and `.tmp/paper_suggest_moe_visual_dense/`.
- Slice 8 visible-launch smoke: `PROJECT_MOE_GUI_VISIBLE_SMOKE_EXIT_MS=3000` + `D:/PythonProject_paper_suggest/project-moe-gui.cmd --allow-visible` -> exit code `0`.
- Slice 8 target A Git status: `git -C D:/PythonProject_paper_suggest status --short --branch` -> `## main`, clean.
- Current primary shell: QFluentWidgets / Qt Widgets (`qfluentwidgets-qtwidgets`); QML Material is an explicit fallback only.
- Critical acceptance session: `smoke-session-final` must show by default unless explicit test metadata exists.

<!-- EVIDENCE_INDEX_END -->

## 2. Goals and Non-Goals

### 2.1 Goals

1. Each target-project GUI displays and controls only its own sessions by default.
2. Each session can independently enable or disable MOE.
3. Each session can select concrete MOE lenses or MOE categories, with tri-state category/lens linkage.
4. Session runtime uses GUI-written state to choose the effective MOE scope.
5. The GUI supports English, bilingual, and Chinese, defaulting to bilingual.
6. MOE categories become clearer product categories with descriptions and lens membership.
7. Workbench becomes a safe handoff workbench with drafts, history, reuse, exports, and pre-dispatch checks.
8. Sessions can be reconciled with discovered local Codex sessions through read-only discovery and confidence labels.
9. The new GUI is installed into target A, then validated through preflight, visual screenshots, visible launch, and local Git commits.

### 2.2 Non-Goals

- The GUI does not directly start Codex, native subagents, durable teams, LangGraph workflows, or model APIs.
- Target A GUI does not write other project states.
- The normal target-project GUI does not expose a default multi-project operations page.
- The GUI does not hide ordinary sessions based on their names.
- QFluentWidgets is not authorized for public closed-source commercial distribution by this plan.
- No GitLab/GitHub publication is authorized by this plan.

## 3. Runtime Boundaries

### 3.1 Project Boundary

- A target-project GUI only reads or writes the target project's `.omx/state/<namespace>/` tree.
- A GUI writes only `D:/PythonProject_paper_suggest/.omx/state/thesis_moe/`.
- The Projects page is hidden from the normal target-project GUI. Any multi-project scan remains a B-repository maintenance or diagnostics-only surface.
- All writes go through the target project's Phase 1 CLI contract and never edit JSON state directly.

### 3.2 Session Boundary

- Session on/off changes only the selected session.
- Project default and session override state must be displayed separately.
- `enabled=false` means the session does not use MOE.
- `enabled=true` with no lens/category selection means all MOE lenses are available.
- `enabled=true` with lens/category selection means only the expanded effective lens set is available.

### 3.3 Workbench Boundary

- Workbench only generates carrier-shaped handoff packages.
- Handoff targets may be `main-session`, `subagent`, `durable-team`, or `langgraph-workflow`.
- The handoff target is package metadata only and does not mean GUI execution.
- Workbench does not read or copy private `MOE.md` content; it uses public lens metadata and operator-entered brief text.

## 4. UI Technical Route

- Use QFluentWidgets / Qt Widgets for the full primary GUI shell.
- Keep the old QML shell as fallback, not the default primary experience.
- The launcher starts the Fluent Widgets GUI by default; if QFluentWidgets is unavailable, it fails closed with a clear preflight blocker.
- The shared runtime provides `PySide6-Fluent-Widgets`; consumer projects do not install PySide6 or QFluentWidgets.
- QFluentWidgets remains recorded as GPLv3/commercial dual-license and is approved here only for local personal tooling.

Product pages:

- Overview: current project, readiness, project default MOE state, recent session summary.
- Sessions: session list, details, on/off, lens/category linkage, Codex mapping, effective MOE list.
- Workbench: safe handoff package workbench, history, drafts, export, pre-dispatch checks.
- Diagnostics: preflight, blockers, runtime, QFluentWidgets, session discovery, unmatched diagnostics.
- Settings: language, theme, session discovery settings, display field settings.

## 5. i18n Contract

- Add an i18n dictionary or resource module for `en`, `zh`, and `bilingual`.
- Default language: `bilingual`.
- Core pages, buttons, labels, errors, status, and Workbench package guidance use i18n.
- Bilingual formatting uses `Chinese / English` consistently.
- Language preference is stored in GUI runtime/user preference, not business MOE state.

## 6. MOE Category and Linkage Model

Recommended A thesis-project categories:

- `review`: blind review, advisor interrogation, novelty, structure/expression.
- `evidence`: literature, evidence chain, citation coverage.
- `risk`: AIGC risk, over-claiming, blocking risk.
- `thinking`: Socratic questioning and thinking-model dispatch.

Tri-state linkage:

- Checking a category checks all lenses in that category.
- Unchecking a category unchecks all lenses in that category unless the lens is still covered by another selected category and intersection protection is selected.
- Manual lens changes update category state to checked, partial, or unchecked.
- UI always displays the final `effective_lenses`.
- Persistence remains compatible with `selected_lenses` (explicit lens ids), `selected_categories` (explicit category ids), and `effective_lens_mode` (`all` or `selected` runtime interpretation).

## 7. Session Identity / Discovery / Reconciliation

Display rules:

- Show all MOE sessions that are not explicitly hidden.
- Show full session ids.
- Never classify or hide a session by name heuristics such as `smoke`, `test`, `fixture`, or `generated`.
- Only explicit fields can move a session to diagnostics/hidden display: `session_kind` (operator-visible type), `is_test_session` (boolean test marker), `hidden_from_default_view` (display gate), or `created_by` (creator tool/source) values that explicitly indicate a test/diagnostic source.
- `smoke-session-final` must show by default when it lacks explicit test metadata.

Codex discovery:

- Read-only scan available sources such as `C:/Users/lenovo/.codex/session_index.jsonl` and `C:/Users/lenovo/.codex/sessions/**` while avoiding credential files and large full-log reads.
- Reconcile discovered Codex sessions with MOE state.
- Mapping confidence values: `exact`, `strong`, `weak`, `unmatched`.
- Unmatched MOE sessions still display and explain `Codex session mapping unavailable`.

Session details include full session id, optional Codex resume/thread id, mapping confidence, id source, override origin, enabled state, project default source, timestamps, branch/worktree, state file path, selected/effective lenses, why shown, and why mapping is unavailable or weak.

## 8. Expert Workbench Enhancements

- Bind generated packages to the selected session.
- Show selected session MOE state and effective lenses.
- Support handoff targets: main session, subagent, durable team, LangGraph workflow.
- Support drafts, copy, export, history filtering, and history reuse.
- Add pre-dispatch checks for missing objective, input material, acceptance criteria, recommended carrier, and durable-team/LangGraph suitability.
- Checks are recommendations only and never execute a carrier.

## 9. Implementation Slices

### Slice 0: Plan Landing

- [x] Create this plan.
- [x] Update parent Project MOE GUI plan index to point at this post-0.2.31 product rebuild plan.
- [x] Commit locally.
- [x] Merge into B local main.

### Slice 1: Fluent Widgets Shell

- [x] Add Widgets GUI shell.
- [x] Make launcher start Widgets shell by default.
- [x] Keep QML as fallback.
- [x] Add fail-closed QFluentWidgets preflight.
- [x] Add navigation and theme baseline.

### Slice 2: i18n

- [x] Add i18n dictionary.
- [x] Default to bilingual.
- [x] Add Settings language switch.
- [x] Connect core UI copy to i18n.

### Slice 3: Project Boundary

- [x] Hide Projects page in normal target-project GUI.
- [x] Keep multi-project scanning only as B maintenance or diagnostics-only surface.
- [x] Show target project root for all writes.

### Slice 4: Session List and Reconciliation

- [x] Add read-only Codex session discovery.
- [x] Reconcile MOE state with Codex sessions.
- [x] Show full session id and mapping confidence.
- [x] Forbid name-based hiding.
- [x] Ensure `smoke-session-final` displays by default.
- [x] Add session details and why-shown explanations.

### Slice 5: Lens/Category Tri-State Linkage

- [x] Add lens/category selection model.
- [x] Category checks update concrete lenses.
- [x] Lens changes update category tri-state.
- [x] Show final effective lens list.
- [x] Preserve read/write compatibility with existing state fields.

### Slice 6: Workbench Safe Handoff

- [x] Bind Workbench to selected session.
- [x] Include effective lenses in the package.
- [x] Add history filtering and reuse.
- [x] Add pre-dispatch checks.
- [x] Keep carrier execution disabled.

### Slice 7: Visual and Automated Validation

- [x] Update visual render checker for Widgets shell.
- [x] Cover 1180x720, 1366x768, and 1440x900.
- [x] Cover bilingual, Chinese, and English.
- [x] Cover long session ids, long lens names, many sessions, and multiple categories.

### Slice 8: Target A Acceptance

- [x] Install/update into `D:/PythonProject_paper_suggest`.
- [x] Run install check.
- [x] Run launcher preflight.
- [x] Run visual screenshot validation.
- [x] Run visible launch validation.
- [x] Commit target A local Git.
- [x] Merge target A local main.

## 10. Verification Plan

B repository:

- Project MOE install check against target A.
- QFluentWidgets runtime import/preflight.
- Session discovery tests.
- i18n tests.
- Lens/category tri-state tests.
- Workbench package schema tests.
- Visual render checker for multi-size, multi-language, multi-session fixtures.
- Precommit update/archive gate.
- OpenSpec guard.
- Local gate and local MR review.

Target A:

- `D:/PythonProject_paper_suggest/project-moe-gui.cmd --preflight --json` - target A machine-readable launcher preflight.
- Install check reports `ok=true` - target A managed artifacts and source toolchain are aligned.
- `smoke-session-final` - ordinary session-name example that must appear in the default Sessions list when no explicit test metadata exists.
- Target GUI does not show other project sessions.
- Visible launch shows Fluent product UI.
- Screenshots have no obvious clipping, overlap, or blank pages.

## 11. Risks and Defaults

| Risk | Default handling |
| --- | --- |
| QFluentWidgets GPLv3 boundary is unclear | Local personal tooling only; commercial/public distribution needs another plan |
| Full Widgets rewrite creates regression risk | Keep QML fallback and reuse CLI/view-model contract |
| Codex session discovery mismatches | Read-only discovery with confidence labels; never auto-write mappings |
| Session name is misleading | No name-based hiding; require explicit metadata |
| Multi-project page implies cross-project control | Hide from normal target-project GUI |
| Workbench is mistaken for executor | Mark packages generated-only and keep carrier execution disabled |

## 12. Definition of Done

As of 2026-06-08, every slice in this plan is complete and has passed local validation in both B and target A; remote publication is outside this plan authorization.

- This plan is committed and merged into B local main.
- B runtime implementation is committed and merged into B local main.
- Target A installation is updated and committed to A local main.
- A GUI displays only A sessions by default.
- `smoke-session-final` displays normally.
- Each session can independently toggle MOE.
- Lens/category tri-state linkage works.
- Language switching works and defaults to bilingual.
- Workbench safe handoff enhancements work.
- Preflight, visual screenshot, and visible launch validation pass.
