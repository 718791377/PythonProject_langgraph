---
doc_id: pyside6_first_consumer_apply_2026_05_22
lang: en
status: active
doc_class: implementation_evidence
translation_of: docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.zh-CN.md
---

# PySide6 First Consumer Apply Evidence - 2026-05-22

Target consumer project: `D:\PythonProject_OpenClaw`.

## What changed

- Added project-local GUI package `src/pythonproject_openclaw_gui/`.
- Added `tools/gui/pyside6_runtime_contract.json`, `tools/gui/run_gui.ps1`, `tools/gui/check_pyside6_env.py`, and adapter guidance.
- Added `tests/test_gui_import.py` and `docs/pyside6_gui_rollback.md`.
- Added bilingual OpenClaw operation docs: `docs_bilingual/operations/pyside6_shared_runtime_gui.md` and `.zh-CN.md`.
- Kept OpenClaw dependency files and lockfiles unchanged; default mode is shared runtime.

## Verification

- Shared runtime Python: `D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe`.
- Import-only smoke: `tools/gui/check_pyside6_env.py --project-root D:\PythonProject_OpenClaw --json` returned `import_only_verified=true`.
- Versions: Python 3.12.10, PySide6 6.11.1, Qt 6.11.1.
- Additional import-only test: `test_gui_import.test_gui_package_imports_without_visible_window()` passed with explicit `PYTHONPATH`.
- OpenClaw local gate, local MR review, and OpenSpec guard passed after local main integration.

## Git evidence

- `b2380c9` - enabled the OpenClaw shared-runtime PySide6 GUI shell.
- `8ddf273` - corrected the runtime contract `project_root` after primary-main integration.
- `986b827` - fixed the OpenClaw Chinese operation document encoding.
- Rollback ref before first local-main fast-forward: `refs/backups/local-main-before-pyside6-shared-gui-20260522070544`.
- No remote publication was performed.

## Boundaries

- No visible GUI was launched.
- No OpenClaw-local PySide6 dependency or lockfile was added.
- Project-local override and executable packaging remain unimplemented opt-in phases.
