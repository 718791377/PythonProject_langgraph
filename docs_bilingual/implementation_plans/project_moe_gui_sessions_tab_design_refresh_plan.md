---
doc_id: project_moe_gui_sessions_tab_design_refresh_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_gui_sessions_tab_design_refresh_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-06-09
updated_at: 2026-06-10
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

- [x] Status: Stage A governance package is already merged into local `main` at `f1bbbefd31922eef729a6d414681df0bbf7212a8`.
- [x] Stage B/C runtime implementation was completed and integrated into B local `main` at `8dfe010f13118d3cd4b5aa78cc5869ca4e78bf57`.
- [x] The feature worktree `implement-project-moe-sessions-tab-design-refresh-20260609` was safely cleaned after local main integration; rollback ref: `refs/backup/local-main/20260610-014207-before-implement-project-moe-sessions-tab-design-refresh-20260609`.
- [x] Pencil MCP was blocked by `transport not connected to app: trae_cn`; HTML fallback mockup and exported PNG are recorded under `docs_bilingual/designs/project_moe_sessions_tab/`.
- [x] Focused toolchain tests passed: `python test\project_moe_gui_toolchain.test.py` reported 101/101 OK.
- [x] B-repository Sessions visual render checks passed for default, long-content, and dense-sessions fixtures at `1180x720`, `1366x768`, and `1440x900`.
- [x] Target A install completed for `D:/PythonProject_paper_suggest`; managed install artifacts were committed in A local `main` at `8d1449f` with toolchain version `0.2.39`.
- [x] Target A `project-moe-gui.cmd --preflight --json` passed with `token=ok`, Phase 1 readiness `ready`, QFluentWidgets import `ok`, and session count `5`.
- [x] Target A Sessions visual render check passed at `1180x720`, `1366x768`, and `1440x900` with `token=ok`.
- [x] Remote publication remains out of scope and was not performed.

- [x] Follow-up 0.2.40 five-thinking-model split is integrated into B local `main` at `e6fdaa138261b0b59dcd77b9c65f5e049195e87a`; it removed `thinking_dispatcher` from the visible GUI lens surface, added five independently selectable thinking-model lenses, and improved the right-side scrolling area.
- [x] Follow-up 0.2.41 existing Phase 1 CLI migration fix is integrated into B local `main` at `155c69fe634f5cf8012749363a74867c76c2f885`; rollback ref: `refs/backup/local-main/20260610-175345-before-fix-project-moe-phase1-lens-migration-20260610`.
- [x] Target A `D:/PythonProject_paper_suggest` is installed and committed with Project MOE GUI `0.2.41`: A local commit `e940cef`.
- [x] Target A `project-moe-gui.cmd --preflight --json` passed with `token=ok`, `phase1_readiness_gate.readiness_status=ready`, `session_count.value=5`, and a clean target repository after commit.
- [x] Target A `list-lenses` confirmed the category boundaries: `socratic_questioning` contains only `socratic_cbt`; `five_classic_thinking_models` contains only `feynman_learning`, `first_principles`, `pyramid_principle`, `swot_analysis`, and `decision_tree`; the visible lens list no longer contains `thinking_dispatcher`.
- [x] Target A reversible live write/readback passed and restored original state: writing the five new lens ids returned `token=ok`; compatibility input `thinking_dispatcher` read back as the five new lenses and did not include `thinking_dispatcher` or `socratic_cbt`.
- [x] Target A Sessions visual render checks passed at `1180x720`, `1366x768`, and `1440x900` with `token=ok`; output directory: `D:/PythonProject_langgraph/.tmp/visual-0.2.41-a-default`.
<!-- CURRENT_STATUS_END -->

## Task Backlog
<!-- TASK_BACKLOG_START -->

- [x] Draft the bilingual implementation plan and registry entry.
- [x] Merge the governance package into local `main`.
- [x] Create design-aid artifacts with Pencil or HTML fallback.
- [x] Implement compact Sessions list, separated right-side controls, three MOE expert modules, and category/lens i18n.
- [x] Validate focused tests and Sessions visual render checks in B.
- [x] Integrate the runtime package into B local `main` and clean the feature worktree.
- [x] Install the refreshed managed GUI artifacts into `D:/PythonProject_paper_suggest` and run target A preflight.
- [x] Run target A Sessions visual render validation for the installed GUI.

- [x] Complete follow-up 0.2.40: fix category cross-control, split the five thinking-model lenses, and improve right-side scrolling.
- [x] Complete follow-up 0.2.41: migrate the existing A Phase 1 CLI public lens/category catalog, install into A, and run preflight, live readback, and visual gates.
<!-- TASK_BACKLOG_END -->

## Evidence Index
<!-- EVIDENCE_INDEX_START -->

- Governance package local-main merge: `f1bbbefd31922eef729a6d414681df0bbf7212a8`.
- Runtime local-main merge: `8dfe010f13118d3cd4b5aa78cc5869ca4e78bf57` (runtime implementation commit).
- Runtime rollback ref: `refs/backup/local-main/20260610-014207-before-implement-project-moe-sessions-tab-design-refresh-20260609`.
- Runtime cleanup evidence: completed claim `D:/PythonProject_langgraph/.omx/session-claims/completed/implement-project-moe-sessions-tab-design-refresh-20260609.json` records cleaned worktree and deleted branch.
- Design fallback reason: `docs_bilingual/designs/project_moe_sessions_tab/fallback_reason.md`.
- HTML mockup: `docs_bilingual/designs/project_moe_sessions_tab/sessions_tab_layout.html`.
- HTML mockup screenshot: `docs_bilingual/designs/project_moe_sessions_tab/sessions_tab_layout.png`.
- Pencil MCP blocker evidence: `get_editor_state(include_schema=true)` returned `transport not connected to app: trae_cn`.
- Pencil CLI/npm evidence: `npm view '@pencil.dev/cli' name version --json` returned `@pencil.dev/cli` `0.2.7`; `htmltool2` package lookup returned npm `E404`.
- Focused tests: `python test\project_moe_gui_toolchain.test.py` -> `Ran 101 tests ... OK`.
- B repository local gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600 -Json` passed in the runtime feature worktree before local integration and passed again in primary root after merge through `tools/complete_local_flow_to_remote_gate.py --execute`.
- Sessions visual render checks in B:
  - default fixture: `python tools\project_moe_gui_toolchain\visual_render_check.py --view-model-json .tmp\project_moe_sessions_view_model.json --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --json` -> `token=ok`.
  - long-content fixture: same command with `--fixture-profile long-content` -> `token=ok`.
  - dense-sessions fixture: same command with `--fixture-profile dense-sessions` -> `token=ok`.
- Target A install: `python .\tools\project_moe_gui_toolchain\update_project_moe_gui.py --target-project D:\PythonProject_paper_suggest --json` -> `token=ok`, target version `0.2.39`.
- Target A managed install commit: `8d1449f` (Chinese commit message: upgrade paper Project MOE GUI to 0.2.38).
- Target A preflight: `D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json` -> `token=ok`, `phase1_readiness_gate.readiness_status=ready`, `session_count.value=5`.
- Target A Sessions visual render: `python tools\project_moe_gui_toolchain\visual_render_check.py --target-project D:\PythonProject_paper_suggest --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --json` -> `token=ok`.
- Remote publication: not performed; B local `main` is intentionally ahead of `gitlab/main` until explicit remote publication approval.


- Follow-up 0.2.40 plan-only package local-main merge: `333621e892f9885b60dbd9bb7da2b2430093e5fe`; rollback ref `refs/backup/local-main/20260610-144818-before-plan-moe-five-thinking-scroll-20260610`.
- Follow-up 0.2.40 focused tests: `python test\project_moe_gui_toolchain.test.py ProjectMoeGuiToolchainTests.test_phase1_bootstrap_scaffold_apply_creates_only_missing_files_in_clean_target ProjectMoeGuiToolchainTests.test_gui_shell_default_moe_modules_and_i18n_labels_are_governed ProjectMoeGuiToolchainTests.test_gui_view_model_declares_sessions_refresh_layout_contract ProjectMoeGuiToolchainTests.test_visual_render_check_defaults_to_multi_size_and_fixture_profiles` -> `Ran 4 tests ... OK`.
- Follow-up 0.2.40 full toolchain tests: `python test\project_moe_gui_toolchain.test.py` -> `Ran 101 tests ... OK`.
- Follow-up 0.2.40 B Sessions visual render checks: default, long-content, and dense-sessions fixtures at `1180x720`, `1366x768`, and `1440x900` each returned `token=ok`.
- Follow-up 0.2.40 root-cause fix evidence: the first default visual run failed on stale category checkbox geometry (`640x480`) after layout rebuild; `_clear_layout()` now hides and detaches old widgets before `deleteLater()`, and the repeated default visual check returned `token=ok`.

- Follow-up 0.2.41 B runtime local-main merge: `155c69fe634f5cf8012749363a74867c76c2f885`; rollback ref: `refs/backup/local-main/20260610-175345-before-fix-project-moe-phase1-lens-migration-20260610`; completed claim: `D:/PythonProject_langgraph/.omx/session-claims/completed/fix-project-moe-phase1-lens-migration-20260610.json`.
- Follow-up 0.2.41 tests: `python -m py_compile tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py tools/project_moe_gui_toolchain/src/project_moe_gui/__init__.py` -> exit 0; `python test/project_moe_gui_toolchain.test.py` -> `Ran 102 tests ... OK`; `python ./tools/check_precommit_update_archive.py --root . --json` -> `ok=true`.
- Follow-up 0.2.41 local flow: `python tools/complete_local_flow_to_remote_gate.py --worktree D:/PythonProject_langgraph/.worktrees/fix-project-moe-phase1-lens-migration-20260610 --execute --json --local-gate-step-timeout-seconds 600` -> `ok=true`, including feature local gate, local MR review, ff-only merge, local cleanup, and post-merge local gate.
- Target A 0.2.41 install: `python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:/PythonProject_paper_suggest --json` -> `token=ok`, `target_toolchain_version=0.2.41`, changed `tools/project_moe_gui/project_moe_gui.config.json`, `tools/project_moe_gui/project_moe_gui.install-manifest.json`, and `tools/thesis_moe_mode.py`.
- Target A 0.2.41 local commit: `e940cef`.
- Target A 0.2.41 preflight: `D:/PythonProject_paper_suggest/project-moe-gui.cmd --preflight --json` -> `token=ok`, `phase1_readiness_gate.readiness_status=ready`, `session_count.value=5`, `git_status.dirty=false`.
- Target A 0.2.41 public catalog: `python D:/PythonProject_paper_suggest/tools/thesis_moe_mode.py list-lenses --json` -> `token=ok`; category boundaries are `strict_graduate_advisor` with six advisor/review lenses, `socratic_questioning` with only `socratic_cbt`, and `five_classic_thinking_models` with only the five new thinking-model lenses; visible lenses do not include `thinking_dispatcher`.
- Target A 0.2.41 live write/readback: for session `019e7c0d-5127-7e71-8ed2-a5eea010bd5c`, writing the five new lenses returned `token=ok` and read back only those five lenses; compatibility write `thinking_dispatcher` returned `token=ok` and read back the five new lenses, without `thinking_dispatcher` or `socratic_cbt`; state was restored from `D:/PythonProject_langgraph/.tmp/moe-session-019e7c0d-before-0.2.41-live-verify.json` after validation.
- Target A 0.2.41 Sessions visual render: `python tools/project_moe_gui_toolchain/visual_render_check.py --target-project D:/PythonProject_paper_suggest --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --output-dir .tmp/visual-0.2.41-a-default --json` -> `token=ok`; screenshots are under `D:/PythonProject_langgraph/.tmp/visual-0.2.41-a-default/`.
<!-- EVIDENCE_INDEX_END -->

## Follow-up Hotfix: 0.2.40/0.2.41 Five Thinking Models, Existing CLI Migration, and Scroll Usability
<!-- FOLLOW_UP_0_2_40_START -->

This follow-up is required before the Sessions page can be considered product-ready for lens/category control. It fixes a category cross-control defect, splits the old five-thinking-model dispatcher into five independently selectable lenses, and improves the right-side scroll ergonomics for long category/lens content.

### Required behavior

- `Socratic Questioning Module` controls only `socratic_cbt`.
- `Five Classic Thinking Models Module` controls only these five lenses:
  - `feynman_learning` / Feynman learning expert;
  - `first_principles` / First principles expert;
  - `pyramid_principle` / Pyramid principle expert;
  - `swot_analysis` / SWOT analysis expert;
  - `decision_tree` / Decision tree expert.
- The deprecated `thinking_dispatcher` id remains a compatibility alias only: reads and legacy writes expand it to all five new thinking-model lenses; new GUI writes must not persist `thinking_dispatcher`.
- The legacy `thinking` category must not include `socratic_cbt`; it maps only to the five thinking-model lenses.
- If an existing target project still has the old Phase 1 CLI public catalog, the installer must safely migrate `PUBLIC_LENSES`, `PUBLIC_CATEGORIES`, selection helpers, selection validation, and parsed selection without reading or overwriting private prompt, agent TOML, or `.omx/state` content.
- The right-side lens/category selection viewport must be large enough for controlled dragging and wheel use. The three category rows should not require their own tiny scrollbar; the lens list remains independently scrollable with a taller track.

### Implementation sequence

- [x] Stage E1: update this implementation plan in both languages and merge the plan-only package into B local `main`. Evidence: `333621e892f9885b60dbd9bb7da2b2430093e5fe`.
- [x] Stage E2: implement B runtime version `0.2.40` in an isolated feature worktree.
- [x] Stage E3: update the managed Phase 1 CLI/template contract so A accepts the five new lens ids and compatibility alias expansion.
- [x] Stage E4: update focused unit tests and visual render fixtures for the five new lenses and scroll ergonomics.
- [x] Stage E5: run B tests and Sessions visual checks for default, long-content, and dense-sessions at `1180x720`, `1366x768`, and `1440x900`.
- [x] Stage E6: integrate B runtime `0.2.40` into local `main` and discover that target A's existing Phase 1 CLI was not migrated by the 0.2.40 installer; do not treat the A 0.2.40 dirty state or preflight blocker as successful acceptance.
- [x] Stage E7: implement the `0.2.41` existing Phase 1 CLI public-catalog migrator, run 102 toolchain tests, merge into B local `main` through local flow, install into `D:/PythonProject_paper_suggest`, commit A local `main`, and run A preflight, reversible live write/readback, and Sessions visual render checks.

### Additional acceptance criteria

- Toggling `Five Classic Thinking Models Module` never toggles `socratic_cbt`.
- Toggling `Socratic Questioning Module` never toggles any of the five thinking-model lenses.
- Selecting old `thinking_dispatcher` through compatibility input results in all five new thinking-model lenses being effective.
- A target-project `set-lenses` call using the five new lens ids returns `token=ok`; invalid-lens errors must not occur for the new ids.
- A target-project write using old `thinking_dispatcher` input returns `token=ok` and reads back the expanded five new lenses; it must not persist `thinking_dispatcher`.
- The target A public catalog must show `socratic_questioning` containing only `socratic_cbt`, and `five_classic_thinking_models` containing only the five new thinking-model lenses.
- Visual checks prove the category/lens panel remains usable with long labels and dense lens lists, without tiny right-side scroll tracks that make drag control impractical.

<!-- FOLLOW_UP_0_2_40_END -->
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
- [x] Merge the Stage A governance package into local `main` before runtime implementation starts. Evidence: `f1bbbefd31922eef729a6d414681df0bbf7212a8`.

### Stage B: Design-aid setup and artifacts

- [x] Verify Pencil Desktop process/path and record evidence. Evidence: local `Pencil` processes were present during Stage B.
- [x] Install or verify Pencil CLI with npm if not already available. Evidence: npm metadata lookup returned `@pencil.dev/cli` version `0.2.7`; global CLI install was not required for the HTML fallback path.
- [x] Attempt Pencil MCP/CLI design generation and PNG export. Evidence: Pencil MCP failed with `transport not connected to app: trae_cn`; HTML screenshot export was used instead.
- [x] If Pencil is unavailable or unauthenticated, create an HTML/htmltool2 mockup and record `fallback_reason`, meaning a diagnostic text field that explains why Pencil could not be used and is not consumed by the GUI runtime.
- [x] Store design artifacts under `docs_bilingual/designs/project_moe_sessions_tab/`.

### Stage C: Runtime Sessions page refresh

- [x] Bump Project MOE GUI toolchain version from `0.2.37` to the next patch version: `0.2.38`.
- [x] Change the left session list to one compact line per session plus visible session count.
- [x] Keep full `Session / Created / Updated / Directory / Branch / Conversation` identity fields only in the right details card.
- [x] Split the right side into independent sections for details, MOE status/actions, and MOE category/lens selection.
- [x] Make the lens-selection section independently scrollable and visible without scrolling the whole detail page.
- [x] Regroup MOE categories into the three requested expert modules while preserving existing lens ids.
- [x] Add category/lens display labels for Chinese, English, and bilingual modes.
- [x] Preserve category-to-lens and lens-to-category tri-state linkage.

### Stage D: Validation and A install acceptance

- [x] Add or update tests for compact list text, detail block completeness, three expert modules, i18n labels, and tri-state linkage.
- [x] Run focused Project MOE GUI tests and the full toolchain test suite as needed. Evidence: `python test\project_moe_gui_toolchain.test.py` returned 101/101 OK.
- [x] Run Sessions visual render checks at `1180x720`, `1366x768`, and `1440x900` for default, long-content, and dense-sessions fixtures.
- [x] Install the updated toolchain into `D:/PythonProject_paper_suggest` after B local `main` integration. Evidence: installer reported `token=ok` and target version `0.2.39`.
- [x] Run A `project-moe-gui.cmd --preflight --json` and verify `token=ok` after install. Evidence: preflight returned `token=ok` and Phase 1 readiness `ready`.
- [x] Confirm A still shows exactly the five real target-project sessions after install. Evidence: preflight `session_count.value=5`.
- [x] Commit A managed install artifacts with a Chinese commit message after managed artifact changes. Evidence: A local commit `8d1449f` (Chinese commit message: upgrade paper Project MOE GUI to 0.2.38).

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
