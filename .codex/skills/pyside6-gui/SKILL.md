---
name: pyside6-gui
description: Preview, add, and verify project-local PySide6 desktop GUI capability without global installs or visible launches by default.
---

# PySide6 GUI

Use this skill when the user asks for a local desktop GUI, PySide6, Qt, Windows desktop tooling, or a small local operator console in a target project.

## Core rule

Keep PySide6 project-local. Do not install PySide6 globally, do not mutate unrelated projects, and do not launch a visible GUI window unless the user explicitly requests interactive verification.

## Workflow

1. Identify the target `ProjectRoot` and cite the evidence, such as `.git`, `pyproject.toml`, `requirements.txt`, `requirements-gui.txt`, `README.md`, `setup.cfg`, `setup.py`, `poetry.lock`, or `uv.lock`.
2. Inspect existing GUI code and dependency style before adding PySide6. Prefer the project-native dependency surface:
   - `requirements-gui.txt` for requirements-based projects;
   - `[project.optional-dependencies] gui = ["PySide6"]` for `pyproject.toml` optional extras;
   - a `gui` dependency group for dependency-group projects;
   - the existing GUI dependency style when the project already has one.
3. Run the helper in read-only preview first:

   ```powershell
   .\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <project-root> -Mode preview -DependencyStyle auto -CreateTemplate -Json
   ```

4. Review the JSON fields `project_root`, `project_root_evidence`, `python_path`, `python_version`, `package_manager`, `dependency_style`, `planned_file_changes`, `planned_commands`, `local_only_artifacts`, `blockers`, and `rollback_steps`.
5. Apply only after the target root and dependency style are safe:

   ```powershell
   .\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <project-root> -Mode apply -DependencyStyle auto -CreateTemplate -Json
   ```

6. Confirm apply output includes `applied_file_changes` and `rollback_note`, normally `docs/pyside6_gui_rollback.md`.
7. Install PySide6 only into the target project's `.venv` or explicitly approved project-local Python environment when local execution is required.
8. Verify with import-only smoke tests first. Do not call `.show()`, `app.exec()`, or a visible launcher during automated verification unless the user asked for interactive GUI verification.
9. Keep generated GUI shell code separate from business services, worker boundaries, config/data directories, and logging/diagnostics adapters.
10. If packaging is requested, treat PyInstaller/Nuitka work as a separate opt-in phase with its own preflight and rollback evidence.

## Expected generated files

A minimal apply may create or update these project-local files:

- `requirements-gui.txt`, `pyproject.toml`, or a project-native dependency group;
- `src/<package_name>/__init__.py`;
- `src/<package_name>/app.py`;
- `src/<package_name>/main_window.py`;
- `tools/gui/check_pyside6_env.py`;
- `tools/gui/run_gui.ps1`;
- `tests/test_gui_import.py`;
- `docs/pyside6_gui_rollback.md`.

## Fail closed

Stop and ask for clarification or fix the target project first when:

- no reliable project root evidence exists;
- dependency style is unknown;
- the helper reports blockers;
- a `gui` dependency already exists but does not mention PySide6;
- requested writes would leave the explicit target project root;
- the task requires global Python installation, plugin/vendor cache edits, remote publication, credential access, browser profile access, or visible GUI launch without explicit approval.

## Reporting

Report capability state with evidence only:

- `candidate` when PySide6 is only being considered;
- `declared` when the dependency surface was updated;
- `template_ready` when GUI source, run helper, and import test exist;
- `env_ready` only after project-local import evidence or lockfile evidence;
- `verified` only after project-local tests pass;
- `packaged` only after explicit packaging preflight succeeds.

Do not infer `env_ready`, `verified`, or `packaged` from this skill, policy text, or templates alone.
