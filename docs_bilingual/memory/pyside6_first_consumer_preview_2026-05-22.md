# PySide6 First Consumer Shared Preview Evidence (2026-05-22)

## Decision

- First consumer project: `D:\PythonProject_OpenClaw`.
- Rationale: this repository's governance identifies `D:\PythonProject_OpenClaw` as a consumer of the shared user-level runtime and policy surface; this pass ran preview only and did not mutate the consumer project.
- Root evidence: `.git, README.md`.
- Helper status: `ok=true`, `mode=preview`, `runtime_mode=shared`.
- Shared runtime: `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.
- Shared runtime Python: `D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe`.
- Shared runtime status: `import_only_verified`.
- Blockers: 0.
- Warnings: 1; the current `dependency_style_unknown` warning is not a blocker for shared-runtime preview, but project-local override still requires a supported dependency surface.
- Visible GUI: not launched; preview output also states that preview creates no files, installs no packages, and launches no visible GUI window.
- Consumer-project changes: none; `git -C D:\PythonProject_OpenClaw status --short --branch` showed only the existing branch ahead state and no dirty files.

## Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot D:\PythonProject_OpenClaw -Mode preview -RuntimeMode shared -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -DependencyStyle auto -CreateTemplate -RunSmokeTest -Json
```

## Key JSON fields

| Field | Value |
| --- | --- |
| `project_root` | `D:\PythonProject_OpenClaw` |
| `project_root_evidence` | `.git, README.md` |
| `runtime_mode` | `shared` |
| `shared_runtime_root` | `D:\PythonProject_langgraph\.shared_runtimes\pyside6` |
| `shared_runtime_python` | `D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe` |
| `shared_runtime_status` | `import_only_verified` |
| `package_manager` | `unknown` |
| `dependency_style` | `unknown` |
| `package_name` | `pythonproject_openclaw_gui` |
| `run_smoke_test` | `True` |
| `smoke_test.status` | `not_requested` |

## Planned write scope (preview only)

This pass only listed planned writes; it did not run apply. Planned paths:

| Path | Planned action | Purpose |
| --- | --- | --- |
| `tools/gui/pyside6_runtime_contract.json` | `create_if_missing` | Create a shared PySide6 runtime contract. |
| `src/pythonproject_openclaw_gui/__init__.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `src/pythonproject_openclaw_gui/app.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `src/pythonproject_openclaw_gui/main_window.py` | `create_if_missing` | Create a minimal PySide6 GUI template file. |
| `tools/gui/check_pyside6_env.py` | `create_if_missing` | Create a shared-runtime PySide6 environment checker. |
| `tools/gui/run_gui.ps1` | `create_if_missing` | Create a visible-GUI launcher that uses the shared runtime Python. |
| `tools/gui/adapters/README.md` | `create_if_missing` | Create a GUI adapter boundary placeholder. |
| `tests/test_gui_import.py` | `create_if_missing` | Create an import-only GUI smoke test. |

## Planned commands

| Command | Execution phase | Purpose |
| --- | --- | --- |
| `Review preview JSON and create a feature branch or rollback commit before apply.` | `manual_review` | Preserve a rollback boundary before project-local GUI writes. |
| `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot "D:\PythonProject_langgraph\.shared_runtimes\pyside6" -Json` | `preflight_or_after_apply` | Verify shared runtime import-only status without launching a visible GUI window. |
| `"D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe" tools/gui/check_pyside6_env.py --project-root . --json` | `planned_import_only_no_visible_gui` | Verify import-only behavior without launching a visible GUI window. |

## Blockers and warnings

### Blockers

- None.

### Warnings

- `dependency_style_unknown: shared runtime mode can still create GUI files, but project-local override needs a supported dependency surface.` - non-blocking preview reminder for this pass.

## Next step

- When the user explicitly continues with consumer-project writes, create a dedicated feature worktree in `D:\PythonProject_OpenClaw` and establish that consumer project's rollback boundary first.
- Run shared-mode `apply` to create the GUI shell, runtime contract, run helper, adapter, import smoke test, and rollback note.
- Run import-only smoke through the shared runtime; still do not launch a visible GUI unless the user explicitly asks for interactive verification.
