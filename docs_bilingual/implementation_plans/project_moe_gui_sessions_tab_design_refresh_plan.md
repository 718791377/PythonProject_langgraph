---
doc_id: project_moe_gui_sessions_tab_design_refresh_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_gui_sessions_tab_design_refresh_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-06-09
updated_at: 2026-06-09
scope: project_moe_gui_sessions_tab_design_refresh
parent_plan: docs_bilingual/implementation_plans/project_moe_gui_product_ui_function_rebuild_plan.md
related_plans:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
  - docs_bilingual/implementation_plans/project_moe_gui_product_ui_function_rebuild_plan.md
  - docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.md
---

# Project MOE GUI Sessions Tab Design Refresh Plan

## 0. Execution Verdict

This active implementation plan refreshes the Project MOE GUI Sessions page after the accepted `0.2.37` session identity fix. The next runtime slice must make the Sessions page easier to scan and operate: the left session list becomes a compact one-line list, the right side separates session details from MOE controls and lens selection, MOE categories are regrouped into three bilingual expert modules, and category/lens labels follow the existing Chinese / English / bilingual language modes.

The implementation must use Pencil as the preferred design-aid surface. Pencil Desktop is already installed on the local machine, while Pencil CLI may need installation and authentication. If Pencil CLI, Pencil MCP, or desktop connection is unavailable, the implementation must use an HTML/htmltool2 design mockup as a fallback and record the fallback reason. Pencil/htmltool2 are design aids only; the product runtime remains PySide6/QFluentWidgets.

## Current Status
<!-- CURRENT_STATUS_START -->

- [ ] Status: active governance package drafted; Stage A is pending local `main` integration before runtime implementation starts.
- [ ] Runtime implementation evidence is pending Stage B/C/D execution.
- [ ] Remote publication is out of scope unless the user explicitly requests GitLab/GitHub publication.

<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Draft the bilingual implementation plan and registry entry.
- [ ] Merge the governance package into local `main`.
- [ ] Create design-aid artifacts with Pencil or HTML fallback.
- [ ] Implement compact Sessions list, separated right-side controls, three MOE expert modules, and category/lens i18n.
- [ ] Validate tests, visual render checks, target A install, and target A preflight.

<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- Pending implementation evidence is expected after Stage A local integration and Stage B/C/D execution.

<!-- EVIDENCE_INDEX_END -->

## 1. Current State

- B repository source of truth: `tools/project_moe_gui_toolchain/`.
- Target A: `D:/PythonProject_paper_suggest` is the real validation target.
- Current accepted toolchain baseline: `0.2.37`.
- The current Sessions list can contain too much repeated detail, so users cannot quickly see how many sessions exist.
- The right side currently mixes identity details, MOE status controls, category selection, and lens selection in one scrolling area.
- The default MOE category model is still too coarse for the requested expert modules.
- Product i18n exists for primary UI labels, but category and lens checkbox text must also obey Chinese / English / bilingual display modes.

## 2. Source of Truth and Boundaries

- Runtime source of truth stays in B under `tools/project_moe_gui_toolchain/`.
- Target A receives only managed install artifacts and validation commits.
- Pencil `.pen`, HTML mockups, and screenshots belong under `docs_bilingual/designs/project_moe_sessions_tab/`.
- Pencil/htmltool2 must not become target-project runtime dependencies.
- Do not copy private A prompt content such as `MOE.md` into B or design artifacts.
- Do not mutate GitLab/GitHub remotes in this plan unless the user explicitly requests remote publication.

## 3. Implementation Checklist

### Stage A: Governance package

- [x] Create this active implementation plan in English and Chinese.
- [x] Register the plan in `docs_bilingual/docs_registry.yaml`.
- [ ] Merge the Stage A governance package into local `main` before runtime implementation starts.

### Stage B: Design-aid setup and artifacts

- [ ] Verify Pencil Desktop process/path and record evidence.
- [ ] Install or verify Pencil CLI with npm if not already available.
- [ ] Attempt Pencil MCP/CLI design generation and PNG export.
- [ ] If Pencil is unavailable or unauthenticated, create an HTML/htmltool2 mockup and record `fallback_reason`, meaning a diagnostic text field that explains why Pencil could not be used and is not consumed by the GUI runtime.
- [ ] Store design artifacts under `docs_bilingual/designs/project_moe_sessions_tab/`.

### Stage C: Runtime Sessions page refresh

- [ ] Bump Project MOE GUI toolchain version from `0.2.37` to the next patch version.
- [ ] Change the left session list to one compact line per session plus visible session count.
- [ ] Keep full `Session / Created / Updated / Directory / Branch / Conversation` identity fields only in the right details card.
- [ ] Split the right side into independent sections for details, MOE status/actions, and MOE category/lens selection.
- [ ] Make the lens-selection section independently scrollable and visible without scrolling the whole detail page.
- [ ] Regroup MOE categories into the three requested expert modules while preserving existing lens ids.
- [ ] Add category/lens display labels for Chinese, English, and bilingual modes.
- [ ] Preserve category-to-lens and lens-to-category tri-state linkage.

### Stage D: Validation and A install acceptance

- [ ] Add or update tests for compact list text, detail block completeness, three expert modules, i18n labels, and tri-state linkage.
- [ ] Run focused Project MOE GUI tests and the full toolchain test suite as needed.
- [ ] Run Sessions visual render checks at `1180x720`, `1366x768`, and `1440x900`.
- [ ] Install the updated toolchain into `D:/PythonProject_paper_suggest`.
- [ ] Run A `project-moe-gui.cmd --preflight --json` and verify `token=ok`.
- [ ] Confirm A still shows exactly the five real target-project sessions.
- [ ] Commit A managed install artifacts with a Chinese commit message.

## 4. Acceptance Criteria

- The Sessions list shows a compact one-line row per visible session and a clear total count.
- The list row does not repeat the full detail block.
- The right details card still contains `Session`, `Created`, `Updated`, `Directory`, `Branch`, and `Conversation`.
- MOE action buttons and lens/category controls are visually separated from the details card.
- Lens/category selection can be reached without scrolling through the details text.
- MOE categories are exactly the requested three bilingual modules in the display layer.
- Category and lens checkbox labels obey the selected language mode.
- Category and lens selection remains bidirectionally linked.
- Pencil design artifacts are generated, or HTML fallback artifacts exist with a recorded Pencil blocker/fallback reason.
- B local `main` contains the runtime implementation; A local `main` contains the refreshed managed install artifacts.

## 5. Risk Controls

- If Pencil CLI install or authentication fails, use HTML/htmltool2 fallback instead of blocking runtime implementation.
- If MCP cannot connect to Pencil Desktop, record the MCP blocker and continue with CLI or HTML fallback.
- Keep QFluentWidgets/PySide6 as the only product GUI runtime surface.
- Keep target A writes limited to managed Project MOE GUI install artifacts and validation commits.
- Stop before remote publication unless the user explicitly requests GitLab/GitHub actions.
