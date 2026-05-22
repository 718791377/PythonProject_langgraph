---
doc_id: pyside6_cross_project_gui_capability_plan
lang: en
canonical: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
status: draft
doc_class: implementation_plan
translation_of: docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md
created_at: 2026-05-20
---

# PySide6 Cross-Project GUI Capability Plan

> Cold-start contract: this file defines how local projects can use PySide6 through the shared runtime maintained by `D:\PythonProject_langgraph`, without installing PySide6 into every consumer project by default and without launching visible GUI windows unless explicitly requested.

## 1. Goal

Provide PySide6 as a reusable local desktop GUI capability for all projects while keeping the runtime centrally maintained and consumer projects isolated.

Default shared runtime:

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
  .venv\                    # local-only shared PySide6 venv, gitignored
  requirements-pyside6.txt   # runtime dependency declaration
  runtime.json               # local runtime version and import-only evidence
  logs\                      # local-only diagnostics
```

Desired outcomes:

- one governed shared PySide6 runtime is maintained by this repository;
- consumer projects get project-local GUI source, adapter docs, runtime contract, run helper, import smoke test, and rollback note;
- consumer projects do not receive PySide6 dependency declarations or lockfile changes in the default shared mode;
- visible GUI launch, project-local override, and executable packaging remain separate opt-in phases;
- state claims are evidence-based: policy, skill, or template presence alone cannot imply verification.

## 2. Non-goals

This plan does not:

- install PySide6 into system Python or user site-packages;
- install PySide6 into every consumer project `.venv` by default;
- install consumer-project business dependencies into the shared runtime;
- edit plugin/vendor caches;
- force every project to have a desktop GUI;
- package every GUI as an executable;
- store consumer-project GUI source inside this orchestration repository.

## 3. Architecture decision

Use a three-layer model.

### 3.1 Shared PySide6 runtime

The only default PySide6 install location is:

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe
```

Rules:

- `.shared_runtimes/` is a local-only ignored artifact;
- runtime provision/verify is a governed maintenance task in this repository;
- the shared runtime installs PySide6 and approved GUI-runtime support packages only;
- consumer-project opt-in must fail closed when the shared runtime is missing;
- runtime readiness requires import-only evidence and `runtime.json`, not policy text.

### 3.2 Shared helpers, templates, skills, and checkers

This repository owns:

- `.codex/skills/pyside6-gui/SKILL.md`;
- `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1`;
- `tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1`;
- `tools/pyside6_gui_templates/`;
- PySide6 contract checkers and tests;
- cross-project operator guidance.

These shared surfaces may generate project-local files, but they do not make any consumer project verified by themselves.

### 3.3 Consumer-project GUI adapter

A consumer project that opts in owns:

- `src/<project>_gui/` GUI shell;
- `tools/gui/pyside6_runtime_contract.json`;
- `tools/gui/run_gui.ps1`;
- `tools/gui/check_pyside6_env.py`;
- `tools/gui/adapters/README.md`;
- `tests/test_gui_import.py`;
- `docs/pyside6_gui_rollback.md`;
- project-local operational docs.

Business logic remains in the consumer project and is reached through adapters, CLI, HTTP, IPC, or workers. Do not move business dependencies into the shared runtime.

## 4. Trigger rules

| Trigger | Action |
| --- | --- |
| User asks for local GUI, desktop GUI, PySide6, Qt, or Windows operator console | Run shared-runtime preview/apply for the explicit target project |
| Project already has GUI source or GUI dependency declarations | Inspect existing GUI stack before adding PySide6 |
| Project needs a small local review console, queue dashboard, or operator launcher | Propose PySide6 as one option before implementation |
| Task only needs CLI automation or an existing browser UI | Do not add PySide6 by default |

## 5. Default consumer-project layout

```text
src/<project_name>_gui/
  __init__.py
  app.py
  main_window.py
tests/test_gui_import.py
tools/gui/
  pyside6_runtime_contract.json
  run_gui.ps1
  check_pyside6_env.py
  adapters/README.md
docs/pyside6_gui_rollback.md
```

Default shared mode must not create `requirements-gui.txt`, dependency groups, optional extras, or lockfile changes.

## 6. Runtime contract pattern

A default shared contract records:

```json
{
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:\\PythonProject_langgraph",
  "runtime_root": "D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6",
  "runtime_python": "D:\\PythonProject_langgraph\\.shared_runtimes\\pyside6\\.venv\\Scripts\\python.exe",
  "project_root": "<target-project-root>",
  "business_runtime_mode": "project-local-adapter",
  "visible_gui_requires_explicit_request": true,
  "packaging_requires_explicit_request": true,
  "project_local_override": false
}
```

Project-local dependency declarations are allowed only in `project-local-override` mode with override reason, dependency/lockfile evidence, and rollback evidence.

## 7. Verification rules

Default automated verification is import-only:

```powershell
& 'D:\PythonProject_langgraph\.shared_runtimes\pyside6\.venv\Scripts\python.exe' .\tools\gui\check_pyside6_env.py --project-root . --json
```

The generated checker must:

- read `tools/gui/pyside6_runtime_contract.json`;
- add `<project-root>/src` to `sys.path` before importing the project GUI package;
- import PySide6 and the GUI package without creating or showing windows;
- emit structured JSON with `import_only_verified`, PySide6/Qt versions, runtime paths, blockers, and rollback steps.

A visible GUI requires explicit operator approval and `tools/gui/run_gui.ps1 -AllowVisibleGui`.

## 8. Helper contract

`ensure-shared-pyside6-runtime.ps1` supports `preview|provision|verify` and may write only under the shared runtime root in provision mode.

`ensure-pyside6-gui.ps1` supports:

- `-Mode preview|apply`;
- `-RuntimeMode shared|project-local-override` with `shared` as default;
- `-RuntimeRoot` defaulting to the shared runtime;
- `-CreateTemplate`;
- `-RunSmokeTest` as an import-only plan/evidence field;
- `-OverrideReason` only for project-local override.

Preview is read-only. Apply writes only under the explicit `ProjectRoot`, records structured `applied_file_changes`, and writes `docs/pyside6_gui_rollback.md`.

## 9. Rollback and authorization

Allowed in local shared mode:

- inspect target project files;
- create GUI shell, runtime contract, adapter guidance, run helper, import test, and rollback note;
- run import-only smoke through the shared runtime.

Requires explicit approval:

- system/global Python installs;
- project-local PySide6 dependency override;
- visible GUI launch;
- executable packaging;
- remote push/MR/sync;
- credential, browser profile, or private-directory access.

Rollback is normally: revert the local feature commit, or delete generated paths listed in `docs/pyside6_gui_rollback.md`.

## 10. Capability state model

| State | Meaning | Minimum evidence |
| --- | --- | --- |
| `not_applicable` | Project does not need desktop GUI | Documented decision or no trigger |
| `candidate` | PySide6 is being considered | Short design note |
| `shared_runtime_declared` | Contract points to shared runtime | `tools/gui/pyside6_runtime_contract.json` |
| `shared_runtime_ready` | Local shared runtime is usable | runtime import smoke and `runtime.json` |
| `project_gui_template_ready` | Consumer GUI shell exists | GUI source, tools/gui, import test, rollback note |
| `project_gui_verified_with_shared_runtime` | Consumer GUI passed import-only smoke via shared runtime | `check_pyside6_env.py --json` with `import_only_verified=true` and no blockers |
| `project_local_override_ready` | Explicit project-local PySide6 override exists | override reason, dependency/lockfile evidence, rollback evidence |
| `packaged` | Executable packaging was requested and validated | packaging config and preflight evidence |

## 11. Implementation checklist

Concrete implementation items only; updating this plan file is not counted as an implementation item.

- [x] Inventory the existing PySide6 GUI baseline: templates, helper, skill, operator guide, opt-in checker, and packaging checker.
- [x] Change the default strategy to shared runtime maintained by `D:\PythonProject_langgraph`, with project-local install as an override exception only.
- [x] Define the shared runtime default path as `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.
- [x] Add `.shared_runtimes/` to `.gitignore`.
- [x] Add shared runtime requirements and metadata templates.
- [x] Add `ensure-shared-pyside6-runtime.ps1` with preview/provision/verify.
- [x] Emit structured JSON from the shared runtime helper.
- [x] Update `ensure-pyside6-gui.ps1` with shared default, `-RuntimeRoot`, and override gating.
- [x] Prevent shared mode from changing project dependency declarations or lockfiles.
- [x] Make shared mode fail closed when the shared runtime is missing.
- [x] Generate project-local runtime contract, GUI shell, adapter guidance, run helper, import test, and rollback note.
- [x] Update `tools/gui/check_pyside6_env.py` template to read runtime contract and inject `<project-root>/src` into `sys.path`.
- [x] Update rollback-note generation so applied paths and literal `tools/gui/` / `tests/` paths are not corrupted by PowerShell interpolation.
- [x] Update repo-local `pyside6-gui` skill and operator usage guides for shared runtime behavior.
- [x] Add and register PySide6 shared-runtime, template, preview-helper, skill, operator-guide, project opt-in, and packaging checkers/tests.
- [x] Provision the real local shared runtime at `.shared_runtimes/pyside6` and verify Python 3.12.10, PySide6 6.11.1, and Qt 6.11.1 with no visible GUI.
- [x] Select the first consumer project and run shared-mode preview; evidence recorded in `docs_bilingual/memory/pyside6_first_consumer_preview_2026-05-22.md`.
- [x] Run shared-mode apply in the first consumer project, generating GUI shell, runtime contract, run helper, adapter, import smoke test, and rollback note.
- [x] Run the first consumer project's import-only smoke test through the shared runtime.
- [x] Update the first consumer project's local documentation with GUI state, runtime contract, adapter boundary, and rollback path.
- [x] Extend the project opt-in checker so real shared-runtime smoke JSON can promote state to `project_gui_verified_with_shared_runtime` only when `import_only_verified=true` and blockers are empty.
- [ ] Decide from first-consumer evidence whether an extra cross-project `run-shared-pyside6-gui.ps1` is needed; otherwise record that per-project `tools/gui/run_gui.ps1` is sufficient.
- [ ] Execute `project-local-override` only when a concrete project has independent-version, isolation, or self-contained packaging needs.
- [ ] Run visible GUI validation only when explicitly requested.
- [ ] Enter PyInstaller/Nuitka packaging only when explicitly requested.

## 12. First-consumer evidence summary

On 2026-05-22, the first registered consumer-project opt-in was completed locally. To keep this repository-level plan generic and compliant with the current-repo authority guard, the project-specific path, commit IDs, smoke output, and rollback details are recorded in:

- `docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md` - records the project-specific first-consumer apply evidence.
- `docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.zh-CN.md` - records the Chinese companion for the same evidence.

The reusable conclusions for this plan are:

- shared-mode apply can generate the GUI shell, runtime contract, run helper, adapter note, import smoke test, rollback note, and local project documentation without installing PySide6 into the consumer project;
- the generated import smoke needs to inject the target project's `src` directory when it is executed by the shared runtime Python;
- the rollback note generator must use explicit formatted strings for changed paths so PowerShell does not serialize ordered dictionaries or corrupt literal `tools/gui/` / `tests/` paths;
- project-specific evidence remains in memory artifacts, not in this generic implementation plan.

## 13. Remaining work

Remaining work is request-driven:

- decide whether a cross-project launcher adds value beyond per-project `tools/gui/run_gui.ps1`;
- use project-local override only for a concrete project and documented reason;
- run visible GUI/manual QA only by explicit request;
- run packaging preflight only by explicit executable-packaging request.

## 14. Acceptance criteria

This plan is complete when:

- bilingual plan files exist and are registered;
- shared runtime policy, default path, gitignore boundary, helper contracts, and state model are documented;
- helper/checker/test surfaces enforce shared-mode no-install behavior and override exceptions;
- the first consumer project has GUI shell, runtime contract, docs, rollback note, and import-only smoke evidence;
- the project opt-in checker can consume real smoke JSON without inferring verification from template presence;
- remote publication is not performed without explicit approval.
