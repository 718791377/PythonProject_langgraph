---
doc_id: pyside6_cross_project_gui_capability_plan
lang: en
canonical: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
status: draft
doc_class: implementation_plan
created_at: 2026-05-20
---

# PySide6 Cross-Project GUI Capability Plan

> Cold-start contract: this file defines how every local project can use PySide6 for its own desktop GUI without sharing mutable Python environments. A fresh Codex session can implement it after reading `AGENTS.md` and `docs_bilingual/project_startup_summary.md`.

## 1. Goal

Make PySide6 available as a reusable GUI capability for all local projects while preserving project isolation, reproducibility, rollback safety, and package-version control.

The desired outcome is:

- any project can opt in to a PySide6 GUI quickly;
- no project is forced to install PySide6 unless it needs a GUI;
- user-level Codex skills, templates, and helper scripts can guide the setup;
- each project keeps its own dependency declaration, virtual environment, source tree, tests, and packaging decisions.

## 2. Non-goals

This plan does not:

- install PySide6 globally into the system Python;
- force every project to carry PySide6 as a default dependency;
- modify plugin/vendor caches;
- choose a single GUI layout for all products;
- package every GUI as an executable by default.

## 3. Architecture decision

Use a two-layer model.

### 3.1 User-level shared capability

The user-level layer may provide:

- a `pyside6-gui` skill or workflow note;
- a reusable setup helper such as `ensure-pyside6-gui.ps1`;
- project templates for `src/<project>_gui/`, `tools/gui/`, and `tests/`;
- smoke-test snippets;
- packaging guidance for PyInstaller or Nuitka;
- troubleshooting guidance for Qt platform plugins, DPI, fonts, and Windows paths.

The shared layer must not be treated as the runtime dependency owner for individual projects.

### 3.2 Project-level isolated dependency

Each project that wants a GUI owns:

- its own `.venv` or documented Python environment;
- `requirements-gui.txt`, a dependency extra, or a project dependency group containing PySide6;
- GUI source files;
- resource files;
- import smoke tests;
- optional packaging scripts;
- project-specific GUI acceptance tests.

## 4. Default project layout

When a project opts in, prefer this minimal layout:

```text
requirements-gui.txt
src/<project_name>_gui/
  __init__.py
  app.py
  main_window.py
tests/test_gui_import.py
tools/gui/
  run_gui.ps1
  check_pyside6_env.py
```

`requirements-gui.txt` starts as:

```text
PySide6
```

If a project already uses `pyproject.toml`, prefer a dependency extra or dependency group instead of a separate requirements file.

## 5. Environment setup rule

Before writing or running a PySide6 GUI in a project:

1. detect the project root and Python environment;
2. prefer the project `.venv`;
3. install PySide6 only into that environment;
4. record the dependency in the project dependency file;
5. run an import smoke test;
6. do not mutate other project environments.

Minimal smoke command:

```powershell
.\.venv\Scripts\python.exe -c "from PySide6.QtWidgets import QApplication; print('PySide6 ok')"
```

## 6. Codex execution workflow

When the user asks for a PySide6 GUI in any project, Codex should:

1. confirm the target project root;
2. inspect existing dependency style (`requirements*.txt`, `pyproject.toml`, `poetry.lock`, `uv.lock`, etc.);
3. choose the project-native dependency declaration;
4. add or update the GUI dependency declaration;
5. install PySide6 into the project environment only if execution is needed now;
6. create or update the GUI source files;
7. add an import smoke test;
8. run the smoke test;
9. if packaging is requested, add packaging scripts and run a packaging preflight;
10. keep GUI changes in that project repository, not in this orchestration repository unless the task is about shared policy or templates.

## 7. Packaging boundary

Packaging is a separate opt-in phase. Do not assume executable packaging just because a GUI exists.

When packaging is requested, the project must choose and document one of:

- PyInstaller;
- Nuitka;
- another explicitly approved local packaging tool.

Packaging checks must cover:

- Qt platform plugin availability;
- resource paths;
- icon paths;
- Windows DPI behavior;
- Chinese font rendering;
- startup logging;
- data directory and config-file locations.

## 8. Safety and rollback

The shared helper must be preview-first when possible.

Allowed without extra remote authorization:

- inspect local project dependency files;
- add project-local GUI dependency declarations;
- add project-local GUI source and smoke tests;
- install into the project `.venv` when the user is working in that project and local execution is required.

Requires explicit approval:

- global Python package installation;
- modifying user-level Codex config;
- editing plugin/vendor cache;
- publishing remote branches or releases;
- changing protected branch settings;
- deleting project files outside the agreed GUI scope.

## 9. Future implementation tasks

A later implementation change may add:

- user-level `pyside6-gui` skill instructions;
- `ensure-pyside6-gui.ps1` helper;
- `check_pyside6_env.py` template;
- `run_gui.ps1` template;
- a minimal PySide6 main-window template;
- a packaging preflight template;
- a cross-project usage note in the skills/profile helper documentation.

## 10. Acceptance criteria

The plan is complete when:

- the English and Chinese plan files exist;
- `docs_bilingual/docs_registry.yaml` registers the plan;
- the plan clearly separates user-level shared capability from project-level dependencies;
- the plan says not to install PySide6 globally by default;
- the plan gives a minimal project layout and smoke test;
- implementation remains local-only and does not push remotes without explicit user approval.
