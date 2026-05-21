---
doc_id: pyside6_gui_cross_project_usage
lang: en
status: active
doc_class: guide
created_at: 2026-05-21
---

# PySide6 GUI Cross-Project Operator Usage

This guide shows how an operator can use the repository-local `plugin-modules` `pyside6-gui` soft-load module for a consumer project without changing the active plugin profile, without installing PySide6 into that consumer project, and without launching a visible desktop window by default.

The default runtime is the shared PySide6 runtime maintained by this repository:

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
```

## 1. Use this guide when

Use this guide when a project asks for a local desktop GUI, PySide6, Qt, a Windows desktop tool, or a small operator console. Do not use this guide as evidence that any consumer project is already `shared_runtime_ready`, `project_gui_verified_with_shared_runtime`, `packaged`, or `release_ready`.

## 2. Soft-load the PySide6 module

Run the module loader from the orchestration repository and pass both the module name and the orchestration repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\skill_sources\plugin-modules\scripts\load_module.ps1 pyside6-gui -RepoRoot <orchestration-repo> -Json
```

Expected operator behavior:

- read only the returned `skill_docs` that are relevant to the current PySide6 task;
- treat `missing_hints` as a blocker before using the module guidance;
- keep the consumer project root separate from `<orchestration-repo>`;
- keep the returned `mode` as `soft-load`.

The soft-load command deliberately does not install PySide6, does not edit `config.toml`, does not enable plugin bundles, does not launch a visible GUI window, and does not package executables.

## 3. Verify or provision the shared runtime as a separate maintenance task

Before applying a consumer-project GUI, verify the shared runtime:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-shared-pyside6-runtime.ps1 -Mode verify -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -Json
```

If the helper reports `shared_runtime_missing`, provisioning is a separate approved maintenance action:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-shared-pyside6-runtime.ps1 -Mode provision -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 -Json
```

Provisioning creates or updates only `.shared_runtimes/pyside6`, writes `runtime.json`, installs from `requirements-pyside6.txt`, and verifies import-only PySide6 evidence. It must not install business dependencies for consumer projects.

## 4. Preview the target consumer project

After reading the necessary `skill_docs`, run the preview helper against the explicit consumer project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode preview -RuntimeMode shared -DependencyStyle auto -CreateTemplate -Json
```

Preview mode must remain read-only. Review these JSON fields:

- `project_root` and `project_root_evidence`;
- `runtime_mode`, `shared_runtime_root`, `shared_runtime_python`, and `shared_runtime_status`;
- `package_manager` and `dependency_style`;
- `planned_file_changes` and `planned_commands`;
- `local_only_artifacts`, `blockers`, and `rollback_steps`.

Stop if the preview cannot identify a safe `ProjectRoot`, if `shared_runtime_status` means the shared runtime must be provisioned first, or if planned writes leave the explicit target project root.

## 5. Apply shared-runtime project opt-in

Apply only after preview review:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -RuntimeMode shared -CreateTemplate -Json
```

Apply must remain project-local. In shared mode it may create GUI source, `tools/gui/pyside6_runtime_contract.json`, `tools/gui/run_gui.ps1`, `tools/gui/check_pyside6_env.py`, `tools/gui/adapters/README.md`, import smoke tests, and `docs/pyside6_gui_rollback.md`. It must not create `requirements-gui.txt`, mutate `pyproject.toml`, or install PySide6 in the consumer project.

A successful apply output should include `applied_file_changes` and `rollback_note`.

## 6. Project-local override boundary

Use `project-local-override` only when the target project needs its own PySide6 version, isolated packaging runtime, or offline/self-contained distribution:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -RuntimeMode project-local-override -DependencyStyle auto -OverrideReason "<why this project needs its own PySide6>" -CreateTemplate -Json
```

This exception may update `requirements-gui.txt`, `pyproject.toml`, or a dependency group, but only with override reason, version/lockfile review, and rollback evidence.

## 7. Visible GUI and packaging boundaries

Visible GUI launch remains an interactive desktop action. Start a visible GUI window only when the user explicitly requests interactive verification or the task itself requires it. Automated checks must not call `.show()`, `app.exec()`, or `Start-Process` to create a visible window unless that approval is present.

Packaging is a separate phase from GUI opt-in. When executable packaging is requested, collect project-local packaging opt-in evidence for exactly one approved tool, normally PyInstaller or Nuitka. The packaging preflight must record Qt platform plugin handling, resource and icon paths, DPI and font behavior, startup logging, data directory behavior, antivirus false-positive risk, reproducible build command, output directory, data exclusions, and rollback steps. Release, signing, and distribution still require separate approval from local packaging.

## 8. Reporting states

Use these state claims only with evidence:

- `candidate` when PySide6 is being considered;
- `shared_runtime_declared` when the consumer project has a runtime contract;
- `shared_runtime_ready` only after shared runtime `runtime.json` and import smoke evidence exist;
- `project_gui_template_ready` when GUI source, run helper, adapter, runtime contract, rollback note, and import test exist;
- `project_gui_verified_with_shared_runtime` only after import-only tests run through the shared runtime;
- `project_local_override_ready` only after a documented override has dependency/lockfile evidence;
- `packaged` only after explicit packaging preflight succeeds.

Never infer `shared_runtime_ready`, `project_gui_verified_with_shared_runtime`, `project_local_override_ready`, `packaged`, or `release_ready` from policy, guide, skill, helper, or template text alone.
