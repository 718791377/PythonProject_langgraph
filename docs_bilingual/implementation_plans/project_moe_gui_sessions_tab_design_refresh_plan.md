---
doc_id: project_moe_gui_sessions_tab_design_refresh_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_gui_sessions_tab_design_refresh_plan.md
status: active
doc_class: implementation_plan
created_at: 2026-06-09
updated_at: 2026-06-11
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

- [x] Follow-up 0.2.42 Sessions left-list usability is integrated into B local `main` at `3ac470689775d18f8db070acd713e884d9e447cb`; its Stage A governance package is `1174201323ca75e4d013791ffa1755b12780bd02`; target A `D:/PythonProject_paper_suggest` was installed and committed at `1b34cf7` with toolchain version `0.2.42`.
- [x] Follow-up 0.2.43 Phase 1 CLI migration idempotency hotfix is integrated into B local `main` at `f25c6b222eecfecfc2f9eeb031d2767aa59f4adb`; rollback ref: `refs/backup/local-main/20260611-074904-before-fix-project-moe-phase1-migration-idempotency-20260611`; target A was installed and committed at `ebd94d1`, and duplicate helper counts are now `expand_lens_aliases=1`, `normalize_category_aliases=1`.
- [x] Follow-up 0.2.44 B runtime implementation is complete in feature worktree `improve-project-moe-sessions-lens-first-0-2-44-20260611`: toolchain version `0.2.44`, compact lens-first right-side layout, two-column lens grid, compact session details/status cards, and visual-gate enforcement for the final core thinking-model lens.
- [x] Follow-up 0.2.44 B validation passed in the feature worktree: focused contract tests, full `python test/project_moe_gui_toolchain.test.py` (104/104 OK), py_compile, and Sessions visual render checks for default, long-content, and dense-sessions at `1180x720`, `1366x768`, and `1440x900`.
- [x] Follow-up 0.2.44 is integrated into B local `main` at `66c9b1a04553393fd2adfc6fbf8b41776fa97716`; the feature worktree/branch was cleaned, target A was reinstalled from the B primary root, A local `main` committed the managed install artifacts at `5d7316e`, A preflight returned `token=ok`, and A Sessions visual render checks for default, long-content, and dense-sessions returned `token=ok` at `1180x720`, `1366x768`, and `1440x900`.
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

- [x] Complete follow-up 0.2.42: wire left-side Sessions search, enabled-state filtering, sorting, and count summary into the runtime and validate it in target A.
- [x] Complete follow-up 0.2.43: make existing Phase 1 CLI public-catalog migration idempotent, reinstall into target A, and verify no duplicate alias helper functions remain.
- [x] Complete follow-up 0.2.44 B runtime: lens-first compact Sessions right side, compact details/actions, two-column lens grid, and stricter visual visibility for `decision_tree` / `the Chinese decision-tree lens label`.
- [x] Complete follow-up 0.2.44 post-merge target A acceptance: installed from B primary root into `D:/PythonProject_paper_suggest`, ran preflight and default/long-content/dense-sessions visual checks, committed A managed artifacts at `5d7316e`, and recorded final evidence.
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

- Follow-up 0.2.42 Stage A governance package: `1174201323ca75e4d013791ffa1755b12780bd02`; runtime local-main merge: `3ac470689775d18f8db070acd713e884d9e447cb`; target A 0.2.42 install commit: `1b34cf7`.
- Follow-up 0.2.42 B validation: focused contract tests and full `python test/project_moe_gui_toolchain.test.py` passed before local integration; local flow merged the feature into B local `main` and cleaned the feature worktree.
- Follow-up 0.2.42 target A validation: installer upgraded `0.2.41` -> `0.2.42`; `project-moe-gui.cmd --preflight --json` returned `token=ok`; Sessions visual render checks covered `1180x720`, `1366x768`, and `1440x900`.
- Follow-up 0.2.43 B hotfix commit: `f25c6b222eecfecfc2f9eeb031d2767aa59f4adb`; rollback ref: `refs/backup/local-main/20260611-074904-before-fix-project-moe-phase1-migration-idempotency-20260611`; completed claim preserved under `.omx/session-claims/completed/fix-project-moe-phase1-migration-idempotency-20260611.json`; feature worktree and branch were cleaned.
- Follow-up 0.2.43 B tests: RED regression reproduced duplicate helper insertion on second migration; focused test then passed; `python test/project_moe_gui_toolchain.test.py` -> `Ran 104 tests ... OK`; `python .\tools\check_precommit_update_archive.py --root . --json` -> `ok=true`; local flow feature gate, local MR review, merge, cleanup, and post-merge local gate passed.
- Target A 0.2.43 install: `python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:/PythonProject_paper_suggest --json` -> `token=ok`, upgraded `0.2.42` -> `0.2.43`, changed `tools/project_moe_gui/project_moe_gui.config.json`, `tools/project_moe_gui/project_moe_gui.install-manifest.json`, and `tools/thesis_moe_mode.py`.
- Target A 0.2.43 local commit: `ebd94d1` (Chinese subject: upgrade Project MOE GUI to 0.2.43).
- Target A 0.2.43 duplicate-helper evidence: `expand_lens_aliases` count is `1`; `normalize_category_aliases` count is `1`; `python D:/PythonProject_paper_suggest/tools/thesis_moe_mode.py list-lenses --json` returned `token=ok` with the accepted three category boundaries.
- Target A 0.2.43 preflight: `D:/PythonProject_paper_suggest/project-moe-gui.cmd --preflight --json` -> `token=ok`, `phase1_readiness_gate.readiness_status=ready`, `git_status.dirty=false`, `session_count.value=5`.
- Target A 0.2.43 Sessions visual render: `python tools/project_moe_gui_toolchain/visual_render_check.py --target-project D:/PythonProject_paper_suggest --shell widgets --sections sessions --size 1180x720 --size 1366x768 --size 1440x900 --fixture-profile default --output-dir .tmp/visual-0.2.43-a-default --json` -> `token=ok`; screenshots are under `D:/PythonProject_langgraph/.tmp/visual-0.2.43-a-default/`.
- Follow-up 0.2.44 feature worktree: `D:/PythonProject_langgraph/.worktrees/improve-project-moe-sessions-lens-first-0-2-44-20260611`; branch `improve-project-moe-sessions-lens-first-0-2-44-20260611`; receipt `.omx/worktree-task-receipt.json`.
- Follow-up 0.2.44 focused tests: `python test\project_moe_gui_toolchain.test.py ProjectMoeGuiToolchainTests.test_gui_view_model_declares_sessions_refresh_layout_contract ProjectMoeGuiToolchainTests.test_gui_view_model_declares_sessions_search_filter_sort_counts_contract ProjectMoeGuiToolchainTests.test_gui_shell_default_moe_modules_and_i18n_labels_are_governed ProjectMoeGuiToolchainTests.test_visual_render_check_defaults_to_multi_size_and_fixture_profiles` -> `Ran 4 tests ... OK`.
- Follow-up 0.2.44 full toolchain tests: `python test\project_moe_gui_toolchain.test.py` -> `Ran 104 tests ... OK`.
- Follow-up 0.2.44 py_compile: `python -m py_compile tools\project_moe_gui_toolchain\src\project_moe_gui\gui_shell.py tools\project_moe_gui_toolchain\visual_render_check.py` -> exit `0`.
- Follow-up 0.2.44 B Sessions visual render: default, long-content, and dense-sessions fixtures at `1180x720`, `1366x768`, and `1440x900` each returned `token=ok`; output directories `.tmp/visual-0.2.44-a-current-default`, `.tmp/visual-0.2.44-a-current-long`, and `.tmp/visual-0.2.44-a-current-dense`.
- Follow-up 0.2.44 B local-main integration: `python D:/PythonProject_langgraph/tools/complete_local_flow_to_remote_gate.py --worktree D:/PythonProject_langgraph/.worktrees/improve-project-moe-sessions-lens-first-0-2-44-20260611 --execute --json --local-gate-step-timeout-seconds 900` -> `ok=true`; B local `main` is `66c9b1a04553393fd2adfc6fbf8b41776fa97716`; rollback ref `refs/backup/local-main/20260611-121709-before-improve-project-moe-sessions-lens-first-0-2-44-20260611`; feature worktree and branch were cleaned.
- Target A 0.2.44 install: `python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:/PythonProject_paper_suggest --json` -> `token=ok`, upgraded `0.2.43` -> `0.2.44`, changed only `tools/project_moe_gui/project_moe_gui.config.json` and `tools/project_moe_gui/project_moe_gui.install-manifest.json`.
- Target A 0.2.44 local commit: `5d7316e` (Chinese subject: upgrade Project MOE GUI to 0.2.44).
- Target A 0.2.44 preflight: `D:/PythonProject_paper_suggest/project-moe-gui.cmd --preflight --json` -> `token=ok`, `phase1_readiness_gate.readiness_status=ready`, `session_count.value=5`, `git_status.dirty=false`.
- Target A 0.2.44 Sessions visual render: default, long-content, and dense-sessions fixtures at `1180x720`, `1366x768`, and `1440x900` returned `token=ok`; output directories `.tmp/visual-0.2.44-a-default`, `.tmp/visual-0.2.44-a-long`, and `.tmp/visual-0.2.44-a-dense`.
- Target A 0.2.44 manual screenshot audit: `sessions_1180x720.png` for default, long-content, and dense-sessions shows compact one-line session rows, separated session details/status/category/lens areas, and the decision-tree expert lens visible on the first screen.
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

## Follow-up: 0.2.42 Sessions Search / Filter / Sort / Count Usability
<!-- FOLLOW_UP_0_2_42_START -->

This follow-up closes a Sessions-page usability slice after 0.2.40/0.2.41 completed category boundaries, the five-thinking-model split, and existing Phase 1 CLI migration. It does not change the governed MOE lens/category boundary. It wires the already-declared view-model search, enabled-state filter, sorting, and count-summary behavior into the Qt Widgets left session list.

### Required behavior

- The left session list keeps a search box that can search session id, display id, title, preview, directory, branch, source, token, and lens selection summary.
- The left side adds filter controls for at least all, enabled, disabled, and blocked/invalid sessions.
- The left side adds sort controls for at least last seen, display id, label, and effective lens mode.
- The left count surface must show current shown count versus total count, while a tooltip or equivalent explanation preserves total / enabled / disabled / blocked-invalid / origin breakdown.
- The view-model must explicitly declare `sessions_layout_contract.left_list_controls = search_filter_sort` and visible count-breakdown contract.
- This slice must not alter the 0.2.40/0.2.41 accepted MOE category boundary: `socratic_questioning` still controls only `socratic_cbt`, and `five_classic_thinking_models` still controls only the five thinking-model lenses.

### Implementation sequence

- [x] Stage E8.1: add a RED test in an isolated feature worktree for the Sessions search / filter / sort / count contract.
- [x] Stage E8.2: implement view-model counts, default filtered rows, expanded search fields, and Qt Widgets filter/sort controls.
- [x] Stage E8.3: bump the toolchain version to `0.2.42` and update bilingual plan evidence.
- [x] Stage E8.4: run focused tests, full toolchain tests, and B Sessions visual render checks.
- [x] Stage E8.5: install into `D:/PythonProject_paper_suggest`, run A preflight and A Sessions visual render checks, and commit A local repository changes.
- [x] Stage E8.6: commit the B feature, run local flow into B local `main`, and clean the feature worktree.

### Acceptance criteria

- Focused tests cover `left_list_controls`, filter modes, sort keys, count summary, enabled/disabled/blocked-invalid filtering, and search hitting conversation preview.
- Changing the Qt Widgets filter/sort combo refreshes the left list immediately and updates shown/total count text.
- After A install, the GUI still shows only current-project real sessions and `project-moe-gui.cmd --preflight --json` returns `token=ok`.
- Sessions visual render covers at least `1180x720`, `1366x768`, and `1440x900`, confirming the left list, search/filter/sort controls, right details, and lens selection region do not visibly overflow.

## Follow-up: 0.2.43 Phase 1 CLI Migration Idempotency Hotfix
<!-- FOLLOW_UP_0_2_43_START -->

This runtime hotfix closes the installation idempotency gap discovered after target A upgraded to `0.2.42`: repeated public-catalog migration could insert duplicate `expand_lens_aliases` and `normalize_category_aliases` helper functions into an existing Phase 1 CLI, which means the selected-helper replacement anchor must replace the whole helper block from the first existing alias helper, category helper, or `selected_lenses_from` through `effective_lens_mode`.

In this section, `selected-helper block` means the contiguous Phase 1 CLI helper region that computes selected lenses, selected categories, and the effective lens mode; `replacement anchor` means the first line where the migrator starts replacing that whole region, not a user-facing GUI control.

### Required behavior

- Re-running `migrate_phase1_mode_cli_catalog_text()` on already migrated text must return the same text and no blockers.
- `expand_lens_aliases` appears exactly once after migration.
- `normalize_category_aliases` appears exactly once after migration.
- Target A remains on the B main source path, not a feature-worktree source path.
- Target A preflight and Sessions visual render checks continue to pass after the `0.2.43` install.

### Implementation sequence

- [x] Stage E9.1: add a RED idempotency regression assertion to the existing public-catalog migration test.
- [x] Stage E9.2: fix `_phase1_replace_selected_helpers()` to replace the entire selected-helper block when prior alias helpers already exist.
- [x] Stage E9.3: bump Project MOE GUI toolchain version to `0.2.43`.
- [x] Stage E9.4: run focused test, full toolchain tests, precommit update/archive gate, local gate, and local MR review.
- [x] Stage E9.5: integrate into B local `main`, clean the feature worktree/branch, reinstall from B main into target A, and commit A local `main`.
- [x] Stage E9.6: verify target A duplicate helper counts, preflight, and Sessions visual render.

<!-- FOLLOW_UP_0_2_43_END -->

## Follow-up: 0.2.44 Sessions Lens-First Compact Layout
<!-- FOLLOW_UP_0_2_44_START -->

This follow-up closes the remaining Sessions-page ergonomics gap found after 0.2.43: at `1180x720`, the right-side details/status region still consumed too much vertical space, so users could need to drag a short right-side scroll track before seeing and operating all core MOE lenses. The 0.2.44 slice makes the right side lens-first and compact while keeping full session identity available through compact labels and tooltips.

### Required behavior

- The toolchain version must be bumped to `0.2.44`.
- The view-model layout contract must declare `right_density = compact_lens_first`, `lens_selection_layout = two_column_lens_grid`, at least two lens-grid columns, compact maximum heights for details/status/category rows, and `all_default_lenses_fit_without_outer_scroll_at_1180x720 = true`.
- The right details card must keep `Session / Created / Updated / Directory / Branch / Conversation`, but Conversation is a compact single-line summary with full text preserved in the tooltip instead of a tall text editor.
- The status/action card must be vertically compact while preserving `Enable session MOE`, `Disable session MOE`, `Apply session lenses`, and `Clear session lenses`.
- The lens area must use a two-column grid with short checkbox labels and full bilingual labels/descriptions in tooltips.
- The category and lens layouts must be top-aligned so stale layout stretch does not push the last visible lens below the first screen.
- The visual gate must prove that the final core thinking-model lens `decision_tree` / `the Chinese decision-tree lens label` is visible in default, long-content, and dense-sessions fixtures at `1180x720`, `1366x768`, and `1440x900`.
- The long-content fixture must keep the full governed lens set, including `decision_tree`; long labels may stress wrapping, but must not remove the core lens from the visual surface.

### Implementation sequence

- [x] Stage E10.1: add RED layout-contract assertions for compact lens-first right-side behavior.
- [x] Stage E10.2: implement compact session details/status cards, two-column lens rows, short checkbox labels, and top-aligned category/lens layouts.
- [x] Stage E10.3: extend the visual render required text to include `the Chinese decision-tree lens label` and keep all five core thinking-model lenses in the long-content fixture.
- [x] Stage E10.4: run focused tests, full toolchain tests, py_compile, and B visual render checks for default, long-content, and dense-sessions.
- [x] Stage E10.5: commit the B feature, run local gates/local MR review, integrate into B local `main`, and clean the feature worktree/branch.
- [x] Stage E10.6: from B primary root, reinstall into `D:/PythonProject_paper_suggest`, run A preflight and visual render checks, and commit A managed install artifacts.

### Acceptance criteria

- At `1180x720`, the right side shows session details, MOE status/actions, the three MOE categories, and `the Chinese decision-tree lens label` without whole-detail-page scrolling.
- Visual render output has no missing required text and no overflow violations for default, long-content, or dense-sessions fixtures.
- Full toolchain tests remain green.
- Target A install must use `D:/PythonProject_langgraph/tools/project_moe_gui_toolchain` as the stable source root after B local-main integration, not the feature worktree path.

<!-- FOLLOW_UP_0_2_44_END -->


<!-- FOLLOW_UP_0_2_42_END -->
