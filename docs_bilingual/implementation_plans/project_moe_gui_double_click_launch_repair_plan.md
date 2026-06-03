---
doc_id: project_moe_gui_double_click_launch_repair_plan
lang: en
status: active
doc_class: implementation_plan
created_at: 2026-06-02
updated_at: 2026-06-03
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
---

# Project MOE GUI Double-Click Launch Repair Plan

## Summary

This plan fixes the target-project symptom where `D:\PythonProject_paper_suggest\project-moe-gui.cmd` closes its CMD window after a double-click and no GUI window remains visible.

The repair is intentionally split into two local-main-first packages:

1. Record this plan in `D:\PythonProject_langgraph` and merge it into local `main`.
2. Implement the durable fix in `D:\PythonProject_langgraph`, then update the installed managed launcher artifacts in `D:\PythonProject_paper_suggest` and merge both local `main` branches.

Remote publication is out of scope unless a later user message explicitly names GitLab/GitHub publication.

## Current Status

<!-- CURRENT_STATUS_START -->

- Status: completed locally.
- Plan package in B (`D:\PythonProject_langgraph`) merged into local `main` at `662c2de`.
- Runtime/helper implementation package in B merged into local `main` at `c66209e`.
- Target A (`D:\PythonProject_paper_suggest`) managed-artifact refresh merged into local `main` at `0c3b49d`.
- A rollback ref: `refs/backup/local-main/20260603-083632-before-project-moe-gui-double-click-refresh` -> `958f003`.
- A feature worktree and local feature branch were cleaned after local main integration.
- Remote publication remains out of scope and was not performed.

<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->

- [x] Reproduce and classify the target launcher symptom.
- [x] Confirm target preflight still succeeds through the shared runtime.
- [x] Confirm visible-launch dry-run succeeds when explicitly enabled.
- [x] Record the two-package repair plan and cross-link it from the parent MOE GUI toolchain plan.
- [x] Merge this plan package into B local `main`.
- [x] Implement the shared runtime helper and launcher-refresh fix in B.
- [x] Verify B toolchain tests, shared-runtime checks, OpenSpec guard, local gate, and local MR review.
- [x] Refresh A managed Project MOE GUI artifacts from B.
- [x] Verify A preflight, visible dry-run, and existing thesis MOE tests.
- [x] Commit and merge A local `main`.
- [x] Preserve A local rollback evidence and completed receipt.
- [x] Clean the integrated A feature worktree and local feature branch.

<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->

- B plan package local-main commit: 662c2de (docs: record MOE GUI double-click launch repair plan).
- B runtime/helper package local-main commit: c66209e (fix: complete MOE GUI double-click launch runtime).
- A managed-artifact refresh local-main commit: `0c3b49d861b8fd0ae7e6bf9f81405bca48f56f2a`.
- A rollback ref: `refs/backup/local-main/20260603-083632-before-project-moe-gui-double-click-refresh` -> `958f003a0a82dc2c15ecb8ca6fe4b263efbfdd02`.
- A completed receipt: `D:\PythonProject_paper_suggest\.omx\session-claims\paper-suggest-project-moe-gui-double-click-refresh-20260603.json`.
- A preflight evidence command: `cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` returned exit 0, `ok: true`, `token: ok`, `launcher_runtime_reexec: true`, `qfluentwidgets_status.ok: true`, and `phase1_readiness_gate.readiness_status: ready`.
- A visible dry-run evidence command: `cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` returned exit 0, `ok: true`, `token: ok`, and `message: Visible GUI launch dry-run passed.`
- A regression evidence command: `python -m unittest discover -s test -p "test_thesis_moe_mode.py"` returned `Ran 6 tests` and `OK`.
- B source surfaces: `tools/project_moe_gui_toolchain/src/project_moe_gui/toolchain.py` and `tools/project_moe_gui_toolchain/src/project_moe_gui/daemon.py`.
- Shared runtime helper surface: `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1`.
- Remote publication evidence: not authorized and not performed.

<!-- EVIDENCE_INDEX_END -->

## Current Evidence

- The target launcher exists at `D:\PythonProject_paper_suggest\project-moe-gui.cmd` and currently calls `python tools\project_moe_gui\launcher.py` in the foreground.
- `--preflight --json` succeeds and reports `token=ok`, `launcher_runtime_reexec=true`, and Ready Lane Phase 1 evidence.
- Visible dry-run succeeds with `PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1`.
- The shared PySide6 runtime can import PySide6 and QFluentWidgets after local maintenance, but the shared runtime helper still needs to backfill `PySide6-Fluent-Widgets` into older `requirements-pyside6.txt` files.
- The B toolchain source already contains a daemon/no-persistent-CMD design, but A's installed managed artifacts may lag behind that source and must be refreshed from B.

## Implementation Changes

- In B, make the shared runtime helper idempotently merge the requirements template into existing runtime requirements and fail closed when `qfluentwidgets` cannot be imported.
- In B, keep no-argument human launcher behavior daemon-backed: parent CMD may exit, child process launches the visible GUI using the configured shared runtime, and `--preflight --json` stays foreground and machine-readable.
- In B, keep `--json` without `--preflight` machine-safe: it must not accidentally open a visible window.
- In A, update only managed Project MOE GUI artifacts from B: `project-moe-gui.cmd`, `tools/project_moe_gui/launcher.py`, config, manifest, and README.
- Do not install PySide6 into A; continue using `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.

## Test Plan

B repository:

- `python test/project_moe_gui_toolchain.test.py` - verifies generated MOE GUI managed launcher, daemon plan, and install artifact behavior.
- `python test/check_pyside6_shared_runtime_contract.test.py` - verifies the shared PySide6 runtime contract checker behavior.
- `python tools/check_pyside6_shared_runtime_contract.py --root . --json` - checks shared runtime readiness and dependency evidence in machine-readable form.
- `python tools/run_openspec_guard.py --root .` - validates repository OpenSpec and governance guard health.
- `tools/ci/local_gate.ps1` - runs the shared local CI gate used before local integration and remote CI.
- `tools/ci/local_mr_review.ps1` - runs local MR review before local `main` integration.

A repository:

- `cmd /c "D:\PythonProject_paper_suggest\project-moe-gui.cmd --preflight --json"` - verifies target-project launcher preflight without opening a visible GUI.
- `cmd /c "set PROJECT_MOE_GUI_DRY_RUN_VISIBLE=1&& D:\PythonProject_paper_suggest\project-moe-gui.cmd --allow-visible --json"` - verifies explicit visible-launch dry-run behavior without entering the Qt event loop.
- `python -m unittest discover -s test -p "test_thesis_moe_mode.py"` - checks existing thesis MOE mode regression coverage in A.
- Optional interactive check only when explicitly allowed: double-click `project-moe-gui.cmd`; the CMD parent may exit, but the GUI window must appear or a stable diagnostic route must remain available.

## Assumptions

- The selected commit scope is B plus A.
- Local `main` integration is authorized by the implementation request and local-main-first policy; remote publication is not authorized.
- QFluentWidgets is approved for local development only until commercial redistribution or packaging receives a separate license review.
