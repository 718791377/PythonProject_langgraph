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
- user-level Codex skills, templates, and helper scripts can guide setup;
- each project keeps its own dependency declaration, virtual environment, source tree, tests, and packaging decisions.

## 2. Non-goals

This plan does not:

- install PySide6 globally into the system Python;
- force every project to carry PySide6 as a default dependency;
- modify plugin/vendor caches;
- choose a single GUI layout for all products;
- package every GUI as an executable by default;
- make this orchestration repository the source tree for consumer-project GUIs.

## 3. Design decision

Use a two-layer model.

### 3.1 User-level shared capability

The user-level layer may provide:

- a `pyside6-gui` skill or workflow note;
- a reusable setup helper such as `ensure-pyside6-gui.ps1`;
- project templates for `src/<project>_gui/`, `tools/gui/`, and `tests/`;
- smoke-test snippets;
- packaging guidance for PyInstaller or Nuitka;
- troubleshooting guidance for Qt platform plugins, DPI, fonts, and Windows paths.

The shared layer owns reusable knowledge and templates only. It must not own project runtime dependencies or mutate all projects at once.

### 3.2 Project-level isolated dependency

Each project that wants a GUI owns:

- its own `.venv` or documented Python environment;
- `requirements-gui.txt`, a dependency extra, or a project dependency group containing PySide6;
- GUI source files;
- resource files;
- import smoke tests;
- optional packaging scripts;
- project-specific GUI acceptance tests.

## 4. Applicability and trigger rules

A project should opt in when one of these is true:

| Trigger | Action |
| --- | --- |
| The user explicitly asks for a local GUI, desktop GUI, PySide6, Qt, or a Windows desktop tool | Start the PySide6 opt-in workflow for that project |
| The project already has GUI source files or GUI dependency declarations | Inspect and continue the existing project-local GUI style |
| The project needs a small local operator tool, review console, queue dashboard, or local workflow launcher | Propose PySide6 as an option before implementation |
| The task only needs command-line automation or a browser UI already exists | Do not add PySide6 by default |

Do not treat this plan as permission to install PySide6 into every project proactively.

## 5. Default project layout

When a project opts in, prefer this minimal layout unless the project already has a stronger convention:

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

## 6. Dependency declaration patterns

Choose one project-native pattern and do not duplicate PySide6 across multiple dependency surfaces unless the project already mirrors dependencies intentionally.

| Project style | Preferred declaration |
| --- | --- |
| Plain pip / requirements | `requirements-gui.txt` with `PySide6` or a reviewed version range |
| `pyproject.toml` with optional dependencies | `[project.optional-dependencies] gui = ["PySide6"]` |
| Dependency groups | a `gui` dependency group |
| uv-managed project | project-native `uv add --optional gui PySide6` or equivalent documented command |
| Poetry-managed project | project-native optional dependency or group |
| Existing GUI stack | follow the existing GUI dependency style and avoid a parallel convention |

Version pinning rule:

- default to an unconstrained `PySide6` only for prototypes;
- for committed project workflows, prefer a bounded range or lockfile produced by the project package manager;
- do not silently upgrade PySide6 across all projects.

## 7. Environment setup rule

Before writing or running a PySide6 GUI in a project:

1. detect the project root and Python environment;
2. prefer the project `.venv`;
3. install PySide6 only into that environment;
4. record the dependency in the project dependency file;
5. run an import smoke test;
6. do not mutate other project environments.

Additional preflight requirements:

- verify the project's Python version, interpreter architecture, and package manager before installing;
- if no project environment exists, preview must propose the exact environment-creation command and target path before apply;
- apply may create a new environment only under the explicit target project root unless the user provides and approves an external `-PythonPath`;
- do not infer `env_ready` from a global interpreter that happens to import PySide6;
- visible GUI launch is an interactive desktop action and must be request-driven; default verification remains import-only.

Minimal smoke command:

```powershell
.\.venv\Scripts\python.exe -c "from PySide6.QtWidgets import QApplication; print('PySide6 ok')"
```

Headless or CI environments may run import-only tests and skip showing a window unless a GUI-capable test runner is explicitly configured.

## 8. User-level helper contract

The repository-source `ensure-pyside6-gui.ps1` helper, and any installed user-level copy, must support preview-first behavior.

Required inputs:

- `-ProjectRoot` - target project root to inspect or mutate
- `-Mode preview|apply` - preview without changes or apply project-local changes
- optional `-DependencyStyle auto|requirements|pyproject-extra|group`
- optional `-PythonPath`
- optional `-PackageVersion`
- optional `-CreateTemplate`
- optional `-RunSmokeTest`

Required preview output:

- detected project root and the evidence used to identify it;
- detected Python environment, Python version, and package manager;
- selected dependency style;
- files that would be created or changed;
- install command that would be run;
- smoke-test command;
- expected local-only artifacts such as `.venv`, build output, or caches;
- risks and rollback notes.

Preview should also emit a machine-readable summary, for example JSON fields for `project_root`, `project_root_evidence`, `python_path`, `python_version`, `package_manager`, `dependency_style`, `planned_file_changes`, `planned_commands`, `local_only_artifacts`, `blockers`, and `rollback_steps`. Human-readable output may wrap this summary, but the structured surface is what later checkers should consume.

Apply mode must be project-local and must fail closed if the target project root, dependency manager, or writable scope cannot be identified confidently.

## 9. Minimal GUI template contract

The minimal template should create a tiny application with:

- a `QApplication` entrypoint;
- a `QMainWindow` subclass;
- a deterministic window title;
- no network access;
- no global configuration mutation;
- no background daemon by default;
- clear separation between GUI shell and project business logic;
- long-running work must not block the UI event loop by default;
- project business errors must be shown in user-understandable form while preserving diagnostic logs;
- logging, settings, and data-directory behavior must be explicit and testable.

Recommended source boundaries:

| Layer | Responsibility |
| --- | --- |
| `app.py` | create `QApplication`, apply application metadata, launch window |
| `main_window.py` | define layout, actions, and UI event wiring |
| project service modules | provide business logic callable from the GUI |
| `tools/gui/run_gui.ps1` | locate the project venv and run the app |
| `tests/test_gui_import.py` | verify importability without showing the GUI |
| worker / service adapter | run long-running work without blocking the Qt event loop |
| config / data directory adapter | define local config, cache, and data directories without writing to unknown locations outside the repository |
| logging / diagnostics adapter | write diagnosable logs without leaking credentials or user-private paths into normal UI output |

## 10. Codex execution workflow

When the user asks for a PySide6 GUI in any project, Codex should:

1. confirm the target project root and state the evidence, such as `.git`, `pyproject.toml`, README, or existing scripts;
2. inspect existing dependency style (`requirements*.txt`, `pyproject.toml`, `poetry.lock`, `uv.lock`, etc.);
3. choose the project-native dependency declaration;
4. check for an existing GUI stack before introducing PySide6 in parallel;
5. create a local rollback boundary such as a feature branch or commit plan before modifying files;
6. add or update the GUI dependency declaration;
7. install PySide6 into the project environment only if execution is needed now;
8. create or update GUI source while separating GUI shell, business services, config/data paths, and worker boundaries;
9. add an import smoke test;
10. run the smoke test;
11. launch a visible GUI only when the user explicitly asks for interactive verification or when the task already requires it;
12. if packaging is requested, add packaging scripts and run a packaging preflight;
13. keep GUI changes in that project repository, not in this orchestration repository unless the task is about shared policy or templates.

## 11. Testing strategy

Minimum tests for every opted-in project:

- dependency file includes PySide6 in the selected dependency surface;
- `from PySide6.QtWidgets import QApplication` import smoke passes in the project environment;
- GUI package imports without creating a visible window;
- `tools/gui/run_gui.ps1` or equivalent run helper resolves the project root and Python path;
- if the GUI calls business logic, business logic remains testable without the GUI event loop;
- long-running actions have a worker, thread, process, or async boundary plus cancellation or failure-feedback behavior;
- local config, cache, and data directories are documented or emitted by the helper preview;
- diagnostics can be enabled for troubleshooting without exposing credentials, access tokens, browser profiles, or unrelated user-private paths.

Optional tests:

- `pytest-qt` or similar GUI interaction tests;
- screenshot/manual QA checklist;
- packaging preflight tests;
- Windows shortcut/start-menu integration tests.

## 12. Packaging boundary

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
- data directory and config-file locations;
- antivirus false-positive risk for local executables;
- reproducible build command and output directory;
- exclusion of credentials, browser profiles, user-private data directories, and unrelated repository files from the packaged artifact;
- release, signing, and distribution steps as separate approvals from local packaging.

## 13. Safety, rollback, and authorization

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
- deleting project files outside the agreed GUI scope;
- rewriting dependency locks across unrelated projects;
- allowing the GUI helper to access network resources, credentials, browser profiles, or private user directories unless the task explicitly requires it and the risk is stated;
- launching a visible GUI window from an automated session when the user has not requested interactive verification.

Rollback path:

- revert the project-local commit or feature branch;
- remove the project-local GUI dependency declaration;
- delete generated GUI template files if they were newly created;
- restore the previous lockfile if a lockfile was changed;
- keep user-level templates intact unless the template itself is the change under review.

## 14. Cross-project governance

This plan is a shared policy. Consumer project implementation must stay in the consumer project.

Rules:

- do not place consumer-project GUI source under `D:\PythonProject_langgraph`;
- do not assume one project's PySide6 version is valid for another project;
- do not use a shared mutable venv for multiple project GUIs;
- do not disable browser or web automation skills to make room for GUI capability;
- if a project needs both GUI and browser automation, keep them separate capability surfaces;
- record project-specific GUI decisions in that project's docs or dependency files;
- GUI helpers may write templates, scripts, and tests only under the explicit target project root; user-level template updates must be separate tasks.

## 15. Capability state model

Every project-local GUI capability should be described with one of these states so future sessions do not confuse policy, dependency declaration, installed runtime, and packaged artifacts:

| State | Meaning | Minimum evidence |
| --- | --- | --- |
| `not_applicable` | the project does not need a desktop GUI | documented decision or no GUI trigger |
| `candidate` | PySide6 is being considered but not adopted | short design note and competing options |
| `declared` | the project has chosen PySide6 and recorded the dependency | dependency file, extra, or group updated |
| `env_ready` | PySide6 is installed in the project environment | import smoke output or lockfile evidence |
| `template_ready` | minimal GUI source and run helper exist | `src/*_gui/`, `tools/gui/`, and import test |
| `verified` | project-local tests pass without showing a window | import-only or headless CI evidence |
| `packaged` | executable packaging was explicitly requested and validated | packaging config, preflight output, rollback note |

Do not report a project as `env_ready`, `verified`, or `packaged` from policy text alone. Those states require project-local evidence.

## 16. Implementation slices and rollout gates

Implement this capability in small, reviewable slices. A later implementation change should not try to modify every consumer project at once.

| Slice | Purpose | Deliverables | Gate before merge |
| --- | --- | --- | --- |
| 0. Inventory | find existing GUI patterns and dependency managers in the target project | read-only inventory note | no project files changed |
| 1. Policy and templates | publish the shared policy and minimal templates | bilingual plan, template files, sample smoke test | docs and template checker pass |
| 2. Preview helper | add `ensure-pyside6-gui.ps1` preview mode | helper with human-readable and JSON `preview` output, no apply mutation | preview snapshot reviewed and structured schema consumed by a checker |
| 3. Apply helper | allow controlled project-local mutation | helper `apply` mode, rollback note generation | dry-run plus apply test in a disposable fixture |
| 4. Project opt-in | enable one consumer project | dependency declaration, GUI shell, import test | project-local gate passes |
| 5. Packaging opt-in | package only if requested | PyInstaller/Nuitka config, preflight script | package preflight and rollback path recorded |

Default rollout order is 0 -> 1 -> 2 -> 3 -> 4. Slice 5 is optional and must remain request-driven.

Current local implementation status:

- Slices 0/1 shared policy and minimal templates are carried by `tools/pyside6_gui_templates/`;
- the template contract is verified by `tools/check_pyside6_gui_template_contract.py` and `test/check_pyside6_gui_template_contract.test.py`;
- Slice 2 preview helper source is carried by `tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1`;
- Slice 3 controlled `apply` mode is now implemented in `tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1` with fail-closed target-root checks, dependency-surface updates, template generation, structured `applied_file_changes`, and `docs/pyside6_gui_rollback.md` rollback-note generation;
- the preview/apply helper contract is verified by `tools/check_pyside6_gui_preview_helper_contract.py` and `test/check_pyside6_gui_preview_helper_contract.test.py`, including preview read-only behavior, disposable apply fixture writes, and unsafe-root fail-closed coverage;
- the helper now emits structured `package_manager_command_evidence` plus contextual `planned_commands` for requirements, pyproject optional extras, uv dependency groups, and Poetry projects; the evidence includes project-native dependency commands, project-environment install/sync commands, lockfile-update guidance, and import-only smoke-test guidance without executing installs or mutating lockfiles by default;
- the CI manifest registers both PySide6 contract tests, and `tools/run_openspec_guard.py` runs both checkers;
- the repo-local `pyside6-gui` skill source is now carried by `.codex/skills/pyside6-gui/SKILL.md` for future session routing; user-level installation or copying remains a separate user-level deployment decision;
- the `plugin-modules` profile helper now exposes a `pyside6-gui` soft-load module that resolves repo-local `repo:` hints for the skill, preview/apply helper, templates, and packaging preflight template without installing PySide6, editing `config.toml`, enabling plugin bundles, launching visible GUI windows, or packaging executables;
- `tools/check_plugin_modules_skill.py` and `test/check_plugin_modules_skill.test.py` verify the `pyside6-gui` module's repo-local hint contract and hard-load no-op boundary;
- the skill contract is verified by `tools/check_pyside6_gui_skill_contract.py` and `test/check_pyside6_gui_skill_contract.test.py`, and `tools/run_openspec_guard.py` runs that checker;
- Slice 4 consumer-project opt-in evidence checking is now carried by `tools/check_pyside6_project_opt_in_contract.py` and `test/check_pyside6_project_opt_in_contract.test.py`; the checker verifies target-root evidence, a single reviewed PySide6 dependency surface, GUI source boundaries, import-only smoke-test behavior, run/env helpers, rollback notes, and the rule that policy/template/skill presence cannot imply `env_ready`, `verified`, or `packaged`;
- the consumer-project opt-in checker now emits structured `lockfile_evidence` for requirements, pyproject optional extras, uv dependency groups, and Poetry GUI groups; it records whether a lockfile is expected or present, requires `poetry.lock` for Poetry GUI groups, and keeps `env_ready` from being inferred from dependency or lockfile text alone;
- `tools/run_openspec_guard.py` and `tools/ci/ci_test_manifest.json` register the consumer-project opt-in checker so future guard and CI runs keep the shared opt-in contract executable;
- actual Slice 4 enablement for a specific consumer project remains project/request-specific, and helper/template/skill/checker presence must not be misreported as any consumer project already being `env_ready`, `template_ready`, or `verified`;
- Slice 5 packaging opt-in evidence checking is now carried by `tools/check_pyside6_packaging_opt_in_contract.py` and `test/check_pyside6_packaging_opt_in_contract.test.py`; the checker requires a passing project opt-in baseline, exactly one chosen tool (`PyInstaller` or `Nuitka`), packaging preflight evidence, data-exclusion evidence, rollback evidence, reproducible build/output-directory evidence, and separate approval for release/signing/distribution;
- `tools/pyside6_gui_templates/packaging/pyside6_packaging_preflight.ps1.template` now includes structured fields for reproducible build commands, generated artifacts, output directories, antivirus-risk recording, rollback steps, data exclusions, and separate release approval; `tools/run_openspec_guard.py` and `tools/ci/ci_test_manifest.json` register the packaging opt-in checker;
- the packaging opt-in checker now emits structured `build_output_evidence` that verifies the packaging `output_directory` and `generated_artifacts` are project-relative, that generated artifacts include the selected output directory, and that neither `packaged` nor `release_ready` is inferred from preflight text alone;
- actual executable packaging remains request-driven, and checker/template presence must not be reported as any consumer project already being `packaged` or `release_ready`;
- cross-project operator usage is now documented in `docs_bilingual/guides/pyside6_gui_cross_project_usage.md` and verified by `tools/check_pyside6_operator_usage_guide.py` plus `test/check_pyside6_operator_usage_guide.test.py`, covering `plugin-modules` `pyside6-gui` soft-load, `-RepoRoot` resolution, preview/apply boundaries, no PySide6 install during soft-load, no `config.toml` edits, visible-GUI approval, packaging opt-in, and evidence-based state reporting.


## 17. Fine-grained implementation checklist

This checklist lists concrete implementation items only; it does not count “update this plan file” as an implementation item. Items are ordered by rollout sequence. Completed items use `[x]`; remaining items use `[ ]`.

- [x] Inventory the existing PySide6 GUI baseline: templates, `ensure-pyside6-gui.ps1`, the `pyside6-gui` skill, operator guide, project opt-in checker, and packaging opt-in checker.
- [x] Change the default strategy from “install PySide6 in each project” to “use the shared PySide6 runtime maintained by this repository, with project-local install as an override exception only”.
- [x] Define the shared runtime default path as `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.
- [x] Add `.shared_runtimes/` to `.gitignore` so runtime binaries, site-packages, Qt plugins, caches, and logs are not committed.
- [x] Add the shared runtime requirements template `tools/pyside6_gui_templates/shared_runtime/requirements-pyside6.txt.template`.
- [x] Add the shared runtime metadata template `tools/pyside6_gui_templates/shared_runtime/runtime.json.template`.
- [x] Add the shared runtime helper `tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1`.
- [x] Implement shared runtime helper `preview` mode as read-only planned-action output.
- [x] Implement shared runtime helper `provision` mode so it writes only under the shared runtime root.
- [x] Implement shared runtime helper `verify` mode as import-only verification with no visible GUI launch.
- [x] Emit structured JSON from the shared runtime helper for runtime root, Python path, status, planned actions, blockers, and rollback notes.
- [x] Update `ensure-pyside6-gui.ps1` with `-RuntimeMode shared|project-local-override`.
- [x] Make `shared` the default runtime mode for `ensure-pyside6-gui.ps1`.
- [x] Add `-RuntimeRoot` to `ensure-pyside6-gui.ps1`, defaulting to the shared runtime path.
- [x] Prevent shared mode from changing project dependency declarations or lockfiles by default.
- [x] Make shared mode fail closed when the shared runtime is missing instead of silently installing PySide6 into the consumer project `.venv`.
- [x] Generate project-local `tools/gui/pyside6_runtime_contract.json` in shared mode.
- [x] Generate project-local GUI adapter guidance at `tools/gui/adapters/README.md` in shared mode.
- [x] Update the `tools/gui/check_pyside6_env.py` template to use the runtime contract and shared runtime for import-only smoke checks.
- [x] Update the `tools/gui/run_gui.ps1` template so the project launches GUI code through the shared runtime.
- [x] Keep GUI source, run helper, adapter, tests, and rollback notes in the consumer project instead of writing consumer GUI code back to this repository.
- [x] Require `-OverrideReason` for `project-local-override`.
- [x] Preserve dependency declaration, lockfile evidence, and rollback evidence boundaries for `project-local-override`.
- [x] Update the repo-local `pyside6-gui` skill to describe the shared runtime default, missing-runtime blocker, and override exception.
- [x] Update bilingual operator usage guides so preview/apply/verify flow matches the shared runtime default.
- [x] Add `tools/check_pyside6_shared_runtime_contract.py` for shared runtime helper, templates, gitignore, skill, and CI registration contracts.
- [x] Update `tools/check_pyside6_gui_preview_helper_contract.py` for shared/runtime-root/override behavior.
- [x] Update `tools/check_pyside6_gui_skill_contract.py` for shared runtime defaults and state-reporting guardrails.
- [x] Update `tools/check_pyside6_gui_template_contract.py` for runtime contract, adapter, and shared runtime templates.
- [x] Update `tools/check_pyside6_operator_usage_guide.py` for shared runtime usage in operator guidance.
- [x] Update `tools/check_pyside6_project_opt_in_contract.py` for shared mode no-install behavior and override exceptions.
- [x] Add and update PySide6 Node tests for shared runtime checker, template checker, preview helper checker, skill checker, project opt-in checker, packaging opt-in checker, and operator guide checker.
- [x] Register the shared runtime checker in `tools/run_openspec_guard.py`.
- [x] Register the shared runtime checker test in `tools/ci/ci_test_manifest.json`.
- [x] Fix `test/run_openspec_guard_json.test.py` so guard JSON tests cover the new checker.
- [x] Run targeted PySide6 tests and confirm they pass.
- [x] Run `python tools\run_openspec_guard.py --root .` and confirm it passes.
- [x] Run `python tools/check_precommit_update_archive.py --root . --json` and confirm it passes.
- [x] Run `git diff --check` and confirm it passes.
- [x] Run the local MR review gate and confirm it passes.
- [x] Run the local CI gate and confirm it passes.
- [x] Merge the shared runtime default strategy into local `main`.
- [x] Clean the integrated `implement-pyside6-shared-runtime` worktree and local feature branch.
- [ ] After explicit user approval, provision the real shared PySide6 runtime at `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.
- [ ] After provisioning, run shared runtime `verify` and record Python, PySide6, and Qt import-only evidence.
- [ ] After provisioning, generate or refresh real `runtime.json` with versions, paths, creation time, and helper version.
- [ ] Select the first consumer project when a concrete request exists; run shared mode `preview` first and confirm target root, write scope, and blockers.
- [ ] Run shared mode `apply` in the first consumer project to generate GUI shell, runtime contract, run helper, adapter, import smoke test, and rollback note.
- [ ] Run the import-only smoke test in the first consumer project through the shared runtime.
- [ ] Update first-consumer project-local documentation with GUI capability state, runtime contract, adapter boundary, and rollback path.
- [ ] Extend the project opt-in checker based on first-consumer evidence to cover real runtime contract, adapter, and shared runtime smoke output.
- [ ] If the first consumer project shows a need, add a cross-project `run-shared-pyside6-gui.ps1`; otherwise record why per-project `tools/gui/run_gui.ps1` is sufficient.
- [ ] Execute `project-local-override` only when a project has independent-version, isolation, or self-contained packaging needs, with override reason plus dependency/lockfile and rollback evidence.
- [ ] Run visible GUI verification or screenshot/manual QA only when the user explicitly requests visible GUI validation.
- [ ] Enter the PyInstaller/Nuitka packaging opt-in phase and run packaging preflight only when the user explicitly requests an executable.

## 18. Failure modes and triage

Common failure modes must be handled as local project issues, not by weakening the shared policy:

| Symptom | Likely cause | Preferred response |
| --- | --- | --- |
| `ModuleNotFoundError: PySide6` | dependency not installed in the active project venv | confirm Python path, install only into the project venv, rerun import smoke |
| Qt platform plugin error | Qt plugin path or packaged artifact missing runtime files | inspect project venv/package output, add packaging preflight evidence |
| GUI test hangs in CI | event loop or visible-window test running in headless environment | use import-only smoke or a GUI-capable test runner |
| Chinese text renders incorrectly | font fallback or packaging missing fonts | document font choice and test Windows rendering |
| antivirus warning for packaged exe | one-file executable heuristic | record tool/version, prefer reproducible build, avoid unreviewed binaries |
| helper cannot identify project root | unsafe target detection | fail closed and ask for `-ProjectRoot` |

## 19. Future implementation tasks

Remaining work must be triggered by a concrete maintenance request or a concrete consumer-project need. Do not keep listing already landed helpers, templates, checkers, skills, or CI registration as future work:

- provision the first real shared runtime at `D:\PythonProject_langgraph\.shared_runtimes\pyside6` and run import-only verify;
- generate or refresh the real `runtime.json` with Python, PySide6, Qt, path, and helper-version evidence;
- when the first consumer project is selected, run shared mode preview/apply and generate GUI shell, runtime contract, adapter, import smoke test, and rollback note inside that project;
- extend opt-in checkers from real consumer-project evidence so template presence alone cannot imply `project_gui_verified_with_shared_runtime`;
- decide from first-consumer usage whether an additional cross-project `run-shared-pyside6-gui.ps1` is needed; if per-project `tools/gui/run_gui.ps1` is sufficient, record that tradeoff;
- advance `project-local-override` only for a concrete project with independent-version, isolation, or self-contained packaging needs;
- advance PyInstaller/Nuitka packaging opt-in and packaging preflight only when the user asks for an executable;
- advance screenshots, manual QA, or `pytest-qt` style interactive tests only when the user asks for visible GUI verification.

The shared surfaces already implemented can be reused as template and checker baselines, but they must not be reported as evidence that any consumer project is already `project_gui_verified_with_shared_runtime`, `project_local_override_ready`, `packaged`, or `release_ready`.

## 20. Acceptance criteria

The plan is complete when:

- the English and Chinese plan files exist;
- `docs_bilingual/docs_registry.yaml` registers the plan;
- the plan clearly separates user-level shared capability from project-level dependencies;
- the plan says not to install PySide6 globally by default;
- the plan defines when to opt in and when not to opt in;
- the plan gives dependency declaration patterns for requirements, `pyproject.toml`, dependency groups, and existing managed projects;
- the plan gives a minimal project layout, helper contract, template contract, and smoke test;
- the plan defines testing, packaging, rollback, and authorization boundaries;
- the plan defines a project-local PySide6 capability state model so policy text is not misreported as runtime readiness;
- the plan defines small implementation slices, per-slice deliverables, and merge gates;
- the plan defines target-project discovery, install preconditions, GUI/business boundaries, worker boundaries, and config/data path requirements;
- the plan defines structured helper preview evidence, visible-GUI launch boundaries, and packaging data-exclusion requirements;
- the plan and helper contract require package-manager-specific command and lockfile evidence so future consumer-project GUI opt-ins do not silently use the wrong install path or mutate unrelated lockfiles;
- the consumer-project opt-in checker reports package-manager-specific `lockfile_evidence` and fails closed when Poetry GUI-group evidence lacks `poetry.lock`;
- the plan lists key failure modes and triage paths;
- the repo-local `pyside6-gui` skill can be discovered through `plugin-modules` soft-load routing without hard-loading plugins or mutating user-level config;
- the packaging opt-in checker reports structured `build_output_evidence` and fails closed when output directories or generated artifacts are absolute, root-like, outside-project, empty, or missing the selected output directory;
- the cross-project operator guide documents and checks the `pyside6-gui` soft-load workflow, preview/apply boundary, no `config.toml` edit, no PySide6 install during soft-load, visible-GUI approval, and packaging opt-in boundary;
- implementation remains local-only and does not push remotes without explicit user approval.
