---
name: pyside6-gui
description: Preview, add, and verify PySide6 desktop GUI capability through the shared local runtime, with project-local override only by exception.
---

# PySide6 GUI

Use this skill when the user asks for a local desktop GUI, PySide6, Qt, Windows desktop tooling, or a small local operator console in a target project.

## Core rule

Use the shared PySide6 runtime by default:

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
```

Consumer projects do not install PySide6 by default. They receive project-local GUI source, `tools/gui/pyside6_runtime_contract.json`, `tools/gui/run_gui.ps1`, import-only tests, adapters, and rollback notes that point to the shared runtime. Do not install PySide6 globally, do not mutate unrelated projects, and do not launch a visible GUI window unless the user explicitly requests interactive verification.

`project-local-override` is an exception for a documented independent PySide6 version, self-contained packaging, or isolation requirement. It must include an override reason, dependency/lockfile evidence, and rollback evidence.

## Workflow

1. Identify the target `ProjectRoot` and cite evidence such as `.git`, `pyproject.toml`, `requirements.txt`, `README.md`, `setup.cfg`, `setup.py`, `poetry.lock`, or `uv.lock`.
2. Inspect existing GUI code before adding PySide6. Avoid adding PySide6 beside an existing GUI framework without review.
3. Check whether the shared runtime is already ready:

   ```powershell
   .\tools\pyside6_gui_helpers\ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -Json
   ```

   If it reports `shared_runtime_missing`, treat runtime provisioning as a separate approved maintenance task. Do not install PySide6 inside the consumer project as a fallback.

4. Run the consumer-project helper in read-only preview first:

   ```powershell
   .\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <project-root> -Mode preview -RuntimeMode shared -DependencyStyle auto -CreateTemplate -Json
   ```

5. Review JSON fields `project_root`, `project_root_evidence`, `runtime_mode`, `shared_runtime_root`, `shared_runtime_python`, `shared_runtime_status`, `planned_file_changes`, `planned_commands`, `local_only_artifacts`, `blockers`, and `rollback_steps`.
6. Apply only after the target root and shared runtime contract are safe:

   ```powershell
   .\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <project-root> -Mode apply -RuntimeMode shared -CreateTemplate -Json
   ```

7. Confirm apply output includes `applied_file_changes` and `rollback_note`, normally `docs/pyside6_gui_rollback.md`.
8. Verify with import-only smoke tests first. Do not call `.show()`, `app.exec()`, or a visible launcher during automated verification.
9. Keep generated GUI shell code separate from business services, worker boundaries, config/data directories, and logging/diagnostics adapters.
10. Use `project-local-override` only when explicitly justified:

    ```powershell
    .\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <project-root> -Mode apply -RuntimeMode project-local-override -DependencyStyle auto -OverrideReason "<why this project needs its own PySide6>" -CreateTemplate -Json
    ```

11. If packaging is requested, treat PyInstaller/Nuitka work as a separate opt-in phase with its own preflight and rollback evidence.

## Expected generated files

A minimal shared-runtime apply may create or update these project-local files:

- `tools/gui/pyside6_runtime_contract.json`;
- `src/<package_name>/__init__.py`;
- `src/<package_name>/app.py`;
- `src/<package_name>/main_window.py`;
- `tools/gui/check_pyside6_env.py`;
- `tools/gui/run_gui.ps1`;
- `tools/gui/adapters/README.md`;
- `tests/test_gui_import.py`;
- `docs/pyside6_gui_rollback.md`.

`requirements-gui.txt`, `pyproject.toml`, or a dependency group may be changed only in `project-local-override` mode.

## Fail closed

Stop and ask for clarification or fix the target project first when:

- no reliable project root evidence exists;
- the shared runtime is missing in apply/verification mode;
- the helper reports blockers;
- requested writes would leave the explicit target project root;
- a project-local override lacks an override reason or version/lockfile evidence;
- the task requires global Python installation, plugin/vendor cache edits, remote publication, credential access, browser profile access, or visible GUI launch without explicit approval.

## Reporting

Report capability state with evidence only:

- `candidate` when PySide6 is only being considered;
- `shared_runtime_declared` when a runtime contract points to the shared runtime;
- `shared_runtime_ready` only after the shared runtime import smoke and `runtime.json` evidence exist;
- `project_gui_template_ready` when GUI source, run helper, adapter, runtime contract, rollback note, and import test exist;
- `project_gui_verified_with_shared_runtime` only after import-only tests run through the shared runtime;
- `project_local_override_ready` only after a documented override has dependency/lockfile evidence;
- `packaged` only after explicit packaging preflight succeeds.

Do not infer `shared_runtime_ready`, `project_gui_verified_with_shared_runtime`, `project_local_override_ready`, or `packaged` from this skill, policy text, or templates alone.
