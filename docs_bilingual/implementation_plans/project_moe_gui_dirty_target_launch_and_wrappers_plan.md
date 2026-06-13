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

This plan repairs the target-project launcher failure where newly added Codex sessions or unrelated dirty target worktree files could make `project-moe-gui.cmd` and `project-moe-gui-silent.vbs` exit before the GUI became visible. It also refreshes `thesis-moe-on.cmd` and `thesis-moe-off.cmd` so they match the current Project MOE lens contract.

Remote publication remains out of scope unless a later user message explicitly names GitLab or GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Source repository B is `D:\PythonProject_langgraph`, which owns the Project MOE GUI toolchain.
- The governance plan package is present on B local `main` at commit `5bfec68`.
- The runtime repair package is present on B local `main` at commit `5d2deff` and upgraded Project MOE GUI from `0.2.44` to `0.2.45`.
- The local rollback point for the runtime integration is `refs/backup/local-main/20260613-154650-before-fix-moe-gui-dirty-launch-wrapper-runtime`.
- The runtime feature worktree and branch `fix-moe-gui-dirty-launch-wrapper-runtime` were cleaned after local-main integration.
- Target project A is `D:\PythonProject_paper_suggest`; its managed Project MOE GUI artifacts were installed from B local `main` and committed on A local `main` at `a22a13b`.
- The earlier dirty-target concern was handled by not using unrelated dirty target work as an install/commit surface. Ordinary GUI launch, preflight, read, and MOE write operations now downgrade unrelated dirty target state to diagnostics or warnings; install/update/managed overwrite still require a clean target worktree.
- `project-moe-gui.cmd --preflight --json` in A returns `ok=true`, a usable `view_model`, and no blockers.
- `thesis-moe-off.cmd` and `thesis-moe-on.cmd` were live-verified in A as project-default MOE off/on wrappers; the final project-default MOE state was restored to `enabled`.
- A follow-up guard false positive was found during this status closeout: ignored `.tmp/skills-usage-audit-*.json` runtime outputs could be scanned by the Spec Kit authority guard. That guard boundary is fixed in this closeout so ignored runtime/audit output does not block unrelated commits.
- No GitLab or GitHub remote publication was authorized or performed for this plan.

<!-- CURRENT_STATUS_END -->

## Implementation Changes

- In B, install/update safety remains strict, while unrelated dirty target state is downgraded from a GUI-operation blocker to a diagnostic warning for preflight, session discovery, and MOE state read/write.
- In B, GUI preflight now returns a usable `view_model` whenever the GUI runtime itself can run, even if unrelated target files are dirty.
- In B, MOE state writes still go through the target Phase 1 CLI and are limited to managed MOE state surfaces; unrelated dirty files are not modified or cleaned.
- In B, launcher generation now makes `project-moe-gui.cmd` prefer the configured shared PySide6 runtime Python, while `project-moe-gui-silent.vbs` delegates to the repaired command and preserves diagnostics.
- In B, wrapper generation now makes `thesis-moe-on.cmd` and `thesis-moe-off.cmd` use current Phase 1 CLI project-default on/off semantics without hard-coded explicit lens or category lists.
- In B, the Spec Kit authority guard now excludes `.tmp/` runtime scratch output, matching the existing Git ignore boundary and preventing ignored skills-audit JSON from becoming commit-blocking policy evidence.
- In A, only managed Project MOE GUI artifacts were installed; PySide6 was not installed into A and private `MOE.md` content was not copied.

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] Confirm the dirty-target concern and avoid using unrelated dirty target work as the final install or commit surface.
- [x] Freeze dirty-target and wrapper decisions in this plan.
- [x] Merge this plan into B local `main`.
- [x] Create a B runtime feature worktree with a receipt and claim.
- [x] Bump the Project MOE GUI toolchain patch version.
- [x] Change dirty-target ordinary GUI preflight/read/write handling from fatal blocker to warning.
- [x] Add or update B tests for dirty-target preflight, dirty-target MOE state write, launcher Python selection, and project-default wrappers.
- [x] Run B targeted tests, precommit update/archive review, OpenSpec guard, local MR review, and follow-up split verification.
- [x] Merge B runtime fix into local `main` and clean its feature worktree and branch.
- [x] Use a clean A-project `main` surface for managed-artifact install.
- [x] Install refreshed managed Project MOE GUI artifacts from B local `main` into A.
- [x] Verify A preflight, newly added session discovery path, no-argument launch contract, silent VBS delegation contract, and thesis on/off wrappers.
- [x] Commit the A managed-artifact refresh into A local `main`.
- [x] Leave unrelated dirty-target work outside this slice and report it as a separate cleanup concern when present.
- [x] Fix the closeout guard false positive where ignored `.tmp` skills-audit JSON could block an unrelated local commit.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- B governance package: `5bfec68`.
- B runtime package: `5d2deff`.
- B rollback ref: `refs/backup/local-main/20260613-154650-before-fix-moe-gui-dirty-launch-wrapper-runtime`.
- B completed claim: `.omx/session-claims/completed/fix-moe-gui-dirty-launch-wrapper-runtime.json`.
- B source surfaces changed for runtime package: `tools/project_moe_gui_toolchain/src/project_moe_gui/__init__.py`, `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py`, and `test/project_moe_gui_toolchain.test.py`.
- B source surfaces changed for closeout guard package: `tools/check_spec_kit_authority_guard.py`, `test/spec_kit_authority_guard.test.py`, and this plan pair.
- B targeted tests passed for dirty-target preflight, dirty-target managed namespace write allowance, runtime Python launcher selection, and project-default thesis wrappers.
- B full Python unittest evidence passed with 814 tests for the runtime package.
- B OpenSpec guard evidence passed with 66/66 checks for the runtime package.
- B local MR review evidence passed for the runtime package.
- B Node/PowerShell manifest check passed with 0 registered files for the runtime package.
- B `git diff --check` evidence passed for the runtime package.
- One earlier full `tools/ci/local_gate.ps1` wrapper run hit a transient order-sensitive failure and must not be cited as a green run; this slice is closed with the fresh split verification evidence above.
- A managed-artifact refresh commit: `a22a13b`.
- A update dry-run after install returned `status=up_to_date`, `no_op=true`, and no blockers.
- A `project-moe-gui.cmd --preflight --json` returned `ok=true`, a usable `view_model`, and no blockers.
- A `thesis-moe-off.cmd` and `thesis-moe-on.cmd` live verification switched project-default MOE off and back on; final state restored to `enabled`.
- A `project-status --json` returned `ok=true`, `enabled=true`, `effective_enabled=true`, branch `main`, and five valid registered sessions.
- Closeout guard evidence: `python test/spec_kit_authority_guard.test.py` covers `.tmp/skills-usage-audit-7d.json` exclusion, and `python tools/check_spec_kit_authority_guard.py --root . --json` reports zero findings even when ignored `.tmp` audit output exists.
- Remote publication evidence: not authorized and not performed.

<!-- EVIDENCE_INDEX_END -->

## Test Plan

B repository:

- `python test/project_moe_gui_toolchain.test.py` must cover generated launcher/wrapper behavior and dirty-target handling.
- Dirty target fixtures must return usable GUI preflight data instead of a no-view-model fatal result.
- Dirty target write fixtures must only update MOE state through the Phase 1 CLI and must not mutate unrelated dirty files.
- Launcher/template tests must confirm shared-runtime Python selection and hidden-launch diagnostics.
- Wrapper tests must confirm `thesis-moe-on/off` use project-default semantics and do not bake explicit lens/category lists.
- `python test/spec_kit_authority_guard.test.py` must cover `.tmp/` scratch output exclusion from Spec Kit authority scans.
- Final status updates must keep passing `python tools/check_precommit_update_archive.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, `python tools/check_document_pair_policy.py --root . --json`, `python tools/check_spec_kit_authority_guard.py --root . --json`, and `git diff --check`.

A clean main worktree:

- `project-moe-gui.cmd --preflight --json` must return `ok=true` or a warning-bearing result with a usable `view_model`; `blocked:dirty_target_project` must not be fatal for ordinary GUI launch.
- Adding or discovering a new Codex session must not make `project-moe-gui.cmd` or `project-moe-gui-silent.vbs` flash-exit without diagnostics.
- `thesis-moe-on.cmd` and `thesis-moe-off.cmd` must return JSON and switch the project default MOE state.
- A simulated unrelated dirty file is allowed for ordinary GUI preflight/read/write diagnostics, while install/update remains clean-worktree-only.

## Assumptions

- Dirty-target allowance is limited to ordinary Project MOE GUI operation; it does not authorize install/update overwrites, unrelated-file cleanup, or committing from a dirty worktree.
- Existing MOE lens IDs and category IDs are preserved unless a later lens taxonomy plan explicitly changes them.
- `.tmp/` is scratch output, not an authority surface or durable evidence source for committed policy checks.
- Remote publication is still a separate explicit gate.
