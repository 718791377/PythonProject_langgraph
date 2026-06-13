---
doc_id: project_moe_gui_dirty_target_launch_and_wrappers_plan
lang: en
status: active
doc_class: implementation_plan
created_at: 2026-06-13
updated_at: 2026-06-13
related_docs:
  - docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.md
---

# Project MOE GUI Dirty Target Launch And Wrapper Repair Plan

## Summary

This plan repairs the remaining target-project launcher failure where newly added Codex sessions or unrelated dirty target worktree files can make `project-moe-gui.cmd` and `project-moe-gui-silent.vbs` exit before the GUI becomes visible. It also refreshes `thesis-moe-on.cmd` and `thesis-moe-off.cmd` to match the current Project MOE lens contract.

Remote publication is out of scope unless a later user message explicitly names GitLab or GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Source repository B is `D:\PythonProject_langgraph`, which owns the Project MOE GUI toolchain.
- Target project A is `D:\PythonProject_paper_suggest`; its primary directory is currently on dirty branch `implement-r6-live-runtime`, so it must not be used as the final install or commit surface for this repair.
- A clean A-project `main` worktree is required for the final managed-artifact install, validation, and local commit.
- Existing A launchers can still depend on ambient `python`; the repaired launch path should prefer the configured shared PySide6 runtime Python.
- Existing preflight can treat `blocked:dirty_target_project` as fatal and return no usable `view_model`; ordinary GUI launch/read/write must instead receive a usable view model plus diagnostics.
- User decision for this slice: unrelated dirty target worktree state is allowed for ordinary GUI read/write only as diagnostics or warnings. Install, update, managed-file overwrite, and local commit still require a clean A worktree.
- User decision for wrappers: `thesis-moe-on.cmd` and `thesis-moe-off.cmd` remain project-default MOE on/off wrappers and must not hard-code an explicit lens or category list.

<!-- CURRENT_STATUS_END -->

## Implementation Changes

- In B, keep install/update safety strict, but downgrade unrelated dirty target state from a GUI-operation blocker to a diagnostic warning for preflight, session discovery, and MOE state read/write.
- In B, ensure GUI preflight returns a usable `view_model` whenever the GUI runtime itself can run, even if unrelated target files are dirty.
- In B, allow MOE state writes only through the target Phase 1 CLI and only for managed MOE state surfaces; unrelated dirty files must not be modified or cleaned.
- In B, update launcher generation so `project-moe-gui.cmd` prefers the configured shared runtime Python and `project-moe-gui-silent.vbs` delegates to that repaired command while preserving diagnostics.
- In B, update wrapper generation so `thesis-moe-on.cmd` and `thesis-moe-off.cmd` call the current Phase 1 CLI with project-default on/off semantics.
- In A, install only managed Project MOE GUI artifacts into a clean A `main` worktree; do not install PySide6 into A and do not copy private `MOE.md` content.

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] Confirm current A primary directory is dirty and is not the final commit surface for this repair.
- [x] Freeze dirty-target and wrapper decisions in this plan.
- [ ] Merge this plan into B local `main`.
- [ ] Create a B runtime feature worktree with a receipt and claim.
- [ ] Bump the Project MOE GUI toolchain patch version.
- [ ] Change dirty-target ordinary GUI preflight/read/write handling from fatal blocker to warning.
- [ ] Add or update B tests for dirty-target preflight, dirty-target MOE state write, launcher Python selection, and project-default wrappers.
- [ ] Run B targeted tests, precommit update/archive review, local gate, and local MR review.
- [ ] Merge B runtime fix into local `main` and clean its feature worktree and branch.
- [ ] Create or reuse a clean A-project `main` worktree outside the dirty A primary directory.
- [ ] Install refreshed managed Project MOE GUI artifacts from B local `main` into the clean A worktree.
- [ ] Verify A preflight, newly added session discovery, no-argument launch path, silent VBS contract, and thesis on/off wrappers.
- [ ] Commit and merge A managed-artifact refresh into A local `main`.
- [ ] Leave the dirty A primary branch untouched and report it as separate follow-up cleanup.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- A status evidence: `D:\PythonProject_paper_suggest` primary directory is on dirty branch `implement-r6-live-runtime` and is not the final commit surface.
- B source surfaces for runtime follow-up: `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`, `daemon.py`, `gui_shell.py`, and the Project MOE installer/updater scripts.
- A managed launcher surfaces for follow-up: `project-moe-gui.cmd`, `project-moe-gui-silent.vbs`, `thesis-moe-on.cmd`, `thesis-moe-off.cmd`, and `tools/project_moe_gui/`.
- Expected verification evidence: dirty target preflight returns a usable view model with diagnostics; wrapper commands preserve project-default semantics; final A install is committed from a clean A `main` worktree.
- Remote publication evidence: not authorized and not performed.

<!-- EVIDENCE_INDEX_END -->

## Test Plan

B repository:

- `python test/project_moe_gui_toolchain.test.py` verifies generated launcher/wrapper behavior and dirty-target handling.
- A dirty target fixture must return usable GUI preflight data instead of a no-view-model fatal result.
- A dirty target write fixture must only update MOE state through the Phase 1 CLI and must not mutate unrelated dirty files.
- Launcher/template tests must confirm shared-runtime Python selection and hidden-launch diagnostics.
- Wrapper tests must confirm `thesis-moe-on/off` use project-default semantics and do not bake explicit lens/category lists.
- `python tools/check_precommit_update_archive.py --root . --json`, `tools/ci/local_gate.ps1`, and `tools/ci/local_mr_review.ps1` must pass before local integration.

A clean main worktree:

- `project-moe-gui.cmd --preflight --json` returns `ok` or a warning-bearing result with a usable `view_model`; `blocked:dirty_target_project` must not be fatal for ordinary GUI launch.
- Adding or discovering a new Codex session must not make `project-moe-gui.cmd` or `project-moe-gui-silent.vbs` flash-exit without diagnostics.
- `thesis-moe-on.cmd` and `thesis-moe-off.cmd` return JSON and switch the project default MOE state.
- A simulated unrelated dirty file is allowed for ordinary GUI preflight/read/write diagnostics, while install/update remains clean-worktree-only.

## Assumptions

- Dirty work in the A primary directory is a separate unfinished A-project change and will not be cleaned by this slice.
- Dirty-target allowance is limited to ordinary Project MOE GUI operation; it does not authorize install/update overwrites, unrelated-file cleanup, or committing from a dirty worktree.
- Existing MOE lens IDs and category IDs are preserved.