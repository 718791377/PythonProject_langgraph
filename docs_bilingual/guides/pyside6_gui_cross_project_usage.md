---
doc_id: pyside6_gui_cross_project_usage
lang: en
status: active
doc_class: guide
created_at: 2026-05-21
---

# PySide6 GUI Cross-Project Operator Usage

This guide shows how an operator can use the repository-local `plugin-modules` `pyside6-gui` soft-load module for a consumer project without changing the active plugin profile, without installing PySide6, and without launching a visible desktop window by default.

## 1. Use this guide when

Use this guide when a project asks for a local desktop GUI, PySide6, Qt, a Windows desktop tool, or a small operator console, and the project should first receive task-scoped guidance rather than a persistent plugin profile change.

Do not use this guide as evidence that any consumer project is already `env_ready`, `verified`, `packaged`, or `release_ready`. Those states require project-local evidence from that consumer project.

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

The soft-load command deliberately does not install PySide6, does not edit `config.toml`, does not enable plugin bundles, does not launch a visible GUI window, and does not package executables. It also does not make omitted skills startup-visible again. If live plugin tools are needed later, preview hard-load changes separately and apply them only after explicit operator approval.

## 3. Preview the target consumer project

After reading the necessary `skill_docs`, run the preview helper against the explicit consumer project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode preview -DependencyStyle auto -CreateTemplate -Json
```

Preview mode must remain read-only. Before any apply step, review these JSON fields:

- `project_root` - confirms the exact consumer project root;
- `project_root_evidence` - explains why that root was trusted;
- `python_path` and `python_version` - identify the project-local interpreter evidence;
- `package_manager` and `dependency_style` - show the selected project-native dependency surface;
- `planned_file_changes` - lists the dependency, template, helper, test, and rollback-note files that would change;
- `planned_commands` - lists installation or smoke-test commands that are still only planned;
- `local_only_artifacts` - lists local artifacts such as `.venv`, build output, or cache directories;
- `blockers` - must be empty before apply;
- `rollback_steps` - must describe how to undo the project-local change.

Stop if the preview cannot identify a safe `ProjectRoot`, if the dependency style conflicts with existing GUI dependencies, or if the planned writes leave the explicit target project root.

## 4. Apply only after opt-in review

Apply is allowed only after the operator has reviewed the preview and approved the consumer project root, dependency style, file changes, and rollback path:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File <orchestration-repo>\tools\pyside6_gui_helpers\ensure-pyside6-gui.ps1 -ProjectRoot <consumer-project> -Mode apply -DependencyStyle auto -CreateTemplate -Json
```

Apply must remain project-local. It may create or update dependency declarations, GUI template files, `tools/gui/` helpers, import smoke tests, and `docs/pyside6_gui_rollback.md` under `<consumer-project>`. It must not write consumer GUI source into `<orchestration-repo>` and must not mutate unrelated projects.

A successful apply output should include `applied_file_changes` and `rollback_note`. Do not report `env_ready` from apply alone; runtime readiness needs project-local PySide6 import or lockfile evidence.

## 5. Install, run, and verify only when needed

Install PySide6 only into the target consumer project's `.venv` or an explicitly approved project-local Python environment, and only when local execution is required for the task. Import-only smoke tests are the default verification path.

Visible GUI launch remains an interactive desktop action. Start a visible GUI window only when the user explicitly requests interactive verification or the task itself requires it. Automated checks must not call `.show()`, `app.exec()`, or `Start-Process` to create a visible window unless that approval is present.

## 6. Packaging opt-in boundary

Packaging is a separate phase from GUI opt-in. The presence of the soft-load module, preview helper, apply helper, templates, or checker does not mean the consumer project is `packaged`.

When executable packaging is requested, first collect project-local packaging opt-in evidence for exactly one approved tool, normally PyInstaller or Nuitka. The packaging preflight must record Qt platform plugin handling, resource and icon paths, DPI and font behavior, startup logging, data directory behavior, antivirus false-positive risk, reproducible build command, output directory, data exclusions, and rollback steps. Release, signing, and distribution still require separate approval from local packaging.

## 7. Reporting states

Use these state claims only with evidence:

- `candidate` when PySide6 is being considered;
- `declared` when the dependency surface was updated;
- `template_ready` when GUI source, run helper, and import test exist;
- `env_ready` only after project-local import or lockfile evidence;
- `verified` only after project-local import-only or headless tests pass;
- `packaged` only after explicit packaging preflight succeeds.

Never infer `env_ready`, `verified`, `packaged`, or `release_ready` from policy, guide, skill, helper, or template text alone.
