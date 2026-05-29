---
doc_id: pyside6_cross_project_gui_capability_plan
lang: en
status: draft
plan_readiness: full-comet-structure-ready-for-maintenance-slicing
doc_class: implementation_plan
translation_of: null
created_at: 2026-05-20
updated_at: 2026-05-27
comet_change: refine-pyside6-gui-plan-comet-structure
related_docs:
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
  - docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
  - docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md
  - docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.md
---

# PySide6 Cross-Project GUI Capability Plan (Full Comet Refactor)

> **For agentic workers:** Use the `$comet` control layer for structural changes to this plan. Keep this file paired with `pyside6_cross_project_gui_capability_plan.zh-CN.md`. Do not treat the presence of a shared PySide6 runtime, helpers, templates, or skills as proof that any consumer project is GUI-ready.

**Goal:** Maintain one shared PySide6 runtime owned by `D:\PythonProject_langgraph`, while allowing each consumer project to keep its own GUI source, adapters, tests, docs, and opt-in packaging decisions.

**Architecture:** Repository-owned shared runtime plus repository-owned helpers/templates/checkers plus consumer-owned GUI adapters. Consumer projects call the shared runtime through an explicit runtime contract and project-local wrapper; they do not receive a silent PySide6 install by default.

**Tech Stack:** Windows PowerShell helpers, Python 3.12 shared virtual environment, PySide6/Qt, JSON runtime contracts, import-only smoke tests, repo-local checkers, OpenSpec/Comet evidence, local-main-first Git workflow.

---

## 0. Full Comet Refactor Conclusion

The prior plan direction was correct but used the older long-form structure. This version reorganizes the plan into the same executable-plan family as the newer Pi sidecar and Comet runtime plans: review conclusion, relationship model, goals/non-goals, work boundary, runtime architecture, source-of-truth map, contracts, state model, gates, implementation items, verification plan, rollback, risks, and self-checks.

Status remains `draft`. Here, `draft` means this is a capability and implementation plan, not an always-on global governance policy. It does not mean the shared-runtime baseline is imaginary. The following facts are already landed or recorded:

- default shared runtime root: `D:\PythonProject_langgraph\.shared_runtimes\pyside6`;
- `.shared_runtimes/` is local-only and gitignored;
- the shared runtime has been provisioned on this machine and import-only verified with Python 3.12.10, PySide6 6.11.1, and Qt 6.11.1;
- repo-local helpers, templates, the `pyside6-gui` skill, operator docs, and checkers already encode shared-runtime default behavior;
- the first registered consumer project completed shared-mode opt-in and import-only smoke evidence; project-specific paths and commits remain in memory artifacts, not in this generic plan;
- the default launch entry remains each consumer project's generated `tools/gui/run_gui.ps1`; a cross-project launcher is deferred until at least two consumer projects prove repeated launcher logic that a per-project wrapper cannot absorb.

Remaining high-impact gates are explicitly trigger-driven:

- project-local PySide6 override;
- visible GUI validation or screenshot/manual QA;
- PyInstaller/Nuitka executable packaging.

Generic requests such as "continue" or "keep implementing the plan" do not authorize those high-impact actions without a named target project and explicit reason.

## 1. Relationship Model and Naming Boundary

| Name | Role in this plan | Owner | Boundary |
| --- | --- | --- | --- |
| `D:\PythonProject_langgraph` | Shared GUI runtime and governance repository | This repository | Owns reusable helpers, templates, checkers, docs, and shared-runtime maintenance scripts. |
| `.shared_runtimes/pyside6` | Local-only shared PySide6 runtime | This repository on the local machine | Contains `.venv`, runtime metadata, logs, and package artifacts; never committed. |
| Consumer project | A project that wants a local desktop GUI | The consumer project | Owns GUI source, adapters, tests, docs, project wrapper, and rollout evidence. |
| `pyside6-gui` skill | Codex routing/help surface | This repository | Explains how to use the shared runtime; it is not a native subagent or proof of runtime readiness. |
| `ensure-shared-pyside6-runtime.ps1` | Shared runtime preview/provision/verify helper | This repository | May create or verify only the shared runtime root. |
| `ensure-pyside6-gui.ps1` | Consumer opt-in helper | This repository | Writes only target-project GUI files in `apply`; default mode is `shared`. |
| `project-local-override` | Explicit exception mode | Consumer project with repository guardrails | Only allowed for independent version, isolation, offline distribution, self-contained packaging, or experiment needs. |
| Packaging | Optional executable build | Consumer project | Requires explicit trigger and packaging preflight; not part of default shared-runtime opt-in. |

## 2. Goals and Non-Goals

Goals:

1. Provide a reusable PySide6 capability for local projects without polluting system Python or each project `.venv`.
2. Keep the shared runtime maintained by this repository and reproducible through repo-local scripts.
3. Keep consumer-project GUI code local to each consumer project.
4. Make preview/apply/verify behavior machine-readable through JSON summaries.
5. Ensure helpers fail closed when the target project root, shared runtime, or writable scope is ambiguous.
6. Preserve explicit gates for visible GUI and packaging side effects.

Non-goals:

- no global Python or user-site PySide6 install by default;
- no silent PySide6 install into every consumer project;
- no business dependency install into the shared PySide6 runtime;
- no forced GUI layout or design language for all projects;
- no plugin/vendor-cache edits;
- no default executable packaging;
- no repository storage of consumer-project GUI source;
- no remote GitLab/GitHub publication unless the current user message explicitly authorizes remote publication.

## 3. Comet / OpenSpec Work Boundary

This refactor uses a full Comet/OpenSpec record because the plan governs future cross-project runtime behavior. The current change is documentation and evidence structure only:

- it updates the bilingual implementation-plan pair;
- it creates an OpenSpec change package for the plan contract;
- it creates Superpowers design and implementation-plan records;
- it does not install PySide6, write consumer projects, launch visible GUI windows, package executables, or mutate user-level configuration.

### 3.1 Comet management record, phase-gate, and Monitoring semantics

- Open: confirm why the plan needs a full executable structure and what success means.
- Design: confirm relationship model, runtime ownership, consumer ownership, state model, and explicit trigger gates.
- Build: rewrite the bilingual plan pair and support artifacts.
- Verify: run document, OpenSpec, precommit, local gate, and local MR review evidence.
- Archive: deferred until this active change is intentionally archived after local integration evidence is recorded.
- Monitoring: a cross-phase control loop. If verification finds missing target-project boundaries, runtime claims, or artifact pairing, return to Open/Design/Build as appropriate. Monitoring is not a sixth phase.

Comet `.sh` scripts may be unavailable on this Windows shell. When they are unavailable, record the blocker and rely on OpenSpec/repository gates instead of claiming unrun Comet script transitions passed.

### 3.2 Full `/comet` structure parity checklist

- [x] Review conclusion and status interpretation.
- [x] Relationship model and naming boundary.
- [x] Goals and non-goals.
- [x] Comet/OpenSpec work boundary.
- [x] Runtime architecture.
- [x] Codex/helper/consumer usage model.
- [x] Repo-local source of truth.
- [x] Shared runtime artifacts and receipt expectations.
- [x] Helper CLI/PowerShell/JSON contracts.
- [x] Runtime contract and state schema.
- [x] Safety, privacy, rollback, and authorization rules.
- [x] Capability and readiness state gates.
- [x] Ordered fine-grained implementation items.
- [x] File ownership map.
- [x] Local integration order and evidence retention.
- [x] Verification plan, related-doc rules, risks, and self-checks.

## 4. Runtime Architecture

```text
Codex request / operator request
  -> pyside6-gui skill or direct helper selection
  -> repo-local helper preview
  -> shared runtime preflight
  -> consumer-project files generated or checked
  -> import-only smoke through shared runtime
  -> optional explicit visible GUI or packaging gate
```

Default shared runtime:

```text
D:\PythonProject_langgraph\.shared_runtimes\pyside6
  .venv\
    Scripts\python.exe
  requirements-pyside6.txt
  runtime.json
  logs\
```

Design rules:

- the shared runtime is rebuildable and local-only;
- `runtime.json` records interpreter, Python version, PySide6 version, Qt version, helper version, timestamps, import-only health, and rollback/removal steps;
- shared runtime provision is a repository maintenance task, not a silent side effect of consumer-project opt-in;
- consumer business dependencies remain in the consumer project runtime and are accessed through adapters, CLI, HTTP, IPC, or worker boundaries.

## 5. Codex / Helper / Consumer Project Usage

Natural-language triggers:

```text
Create a local PySide6 GUI for this project.
Use the shared PySide6 runtime for this project.
Preview GUI opt-in for <project-root>.
Verify the PySide6 GUI import smoke test.
Package this GUI as an executable.  # explicit packaging gate
Run a visible GUI validation.       # explicit interactive gate
```

Default execution:

1. identify the target project root;
2. verify `D:\PythonProject_langgraph\.shared_runtimes\pyside6` exists and can import PySide6;
3. run project opt-in preview;
4. apply only target-project GUI files when approved by the current task;
5. run import-only smoke through the shared runtime;
6. record consumer-project evidence in that project or in a memory artifact, not in this generic plan;
7. stop before visible GUI or packaging unless explicitly requested.

## 6. Repo-local Source of Truth

Expected reusable repository surfaces:

```text
.codex/skills/pyside6-gui/SKILL.md
tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1
tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1
tools/pyside6_gui_templates/
tools/check_pyside6_shared_runtime_contract.py
tools/check_pyside6_gui_preview_helper_contract.py
tools/check_pyside6_gui_skill_contract.py
tools/check_pyside6_gui_template_contract.py
tools/check_pyside6_operator_usage_guide.py
tools/check_pyside6_project_opt_in_contract.py
tools/check_pyside6_packaging_opt_in_contract.py
docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md
docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.md
```

Consumer projects own:

```text
src/<project_name>_gui/
tests/test_gui_import.py
tools/gui/pyside6_runtime_contract.json
tools/gui/run_gui.ps1
tools/gui/check_pyside6_env.py
tools/gui/adapters/
docs or notes that describe project-specific GUI use
```

## 7. Shared Runtime Artifacts and Receipt

Minimum shared runtime metadata:

```json
{
  "schema_version": 1,
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:/PythonProject_langgraph",
  "runtime_root": "D:/PythonProject_langgraph/.shared_runtimes/pyside6",
  "runtime_python": "D:/PythonProject_langgraph/.shared_runtimes/pyside6/.venv/Scripts/python.exe",
  "python_version": "3.12.x",
  "pyside6_version": "6.x",
  "qt_version": "6.x",
  "import_only_verified": true,
  "visible_gui_verified": false,
  "packaging_verified": false,
  "created_at": "<iso8601>",
  "updated_at": "<iso8601>",
  "rollback_steps": [
    "Remove the local-only runtime root.",
    "Re-run provision from the repository helper if needed."
  ]
}
```

The runtime receipt must never contain API keys, business data, private project paths beyond the runtime path, or large log excerpts.

## 8. Helper CLI / PowerShell / JSON Contracts

Shared runtime helper:

```powershell
tools/pyside6_gui_helpers/ensure-shared-pyside6-runtime.ps1 `
  -Mode preview|provision|verify `
  -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 `
  -Json
```

Project opt-in helper:

```powershell
tools/pyside6_gui_helpers/ensure-pyside6-gui.ps1 `
  -ProjectRoot <target-project-root> `
  -Mode preview|apply `
  -RuntimeMode shared|project-local-override `
  -RuntimeRoot D:\PythonProject_langgraph\.shared_runtimes\pyside6 `
  -CreateTemplate `
  -RunSmokeTest `
  -Json
```

Required helper output fields:

| Field | Purpose |
| --- | --- |
| `project_root` | The resolved target project root that the helper may inspect or write. |
| `project_root_evidence` | The signals used to prove the target root, such as Git root, marker files, or explicit input. |
| `runtime_mode` | The selected runtime mode: `shared` for the default shared runtime or `project-local-override` for an explicit exception. |
| `shared_runtime_root` | The repository-maintained shared runtime directory. |
| `shared_runtime_python` | The Python executable inside the shared runtime. |
| `shared_runtime_status` | The preflight result for the shared runtime, such as ready, missing, stale, or blocked. |
| `planned_file_changes` | The target-project files that preview/apply would create or modify. |
| `planned_commands` | The commands the helper would run during apply or smoke verification. |
| `local_only_artifacts` | Local artifacts that must remain untracked, such as logs, caches, runtime folders, or build output. |
| `blockers` | Fail-closed reasons that prevent apply or verification. |
| `rollback_steps` | The concrete cleanup steps for generated project or runtime files. |
| `smoke_test_command` | The import-only verification command using the selected runtime. |
| `visible_gui_requires_explicit_request` | A boolean gate that prevents interactive windows from launching by default. |
| `packaging_requires_explicit_request` | A boolean gate that prevents executable packaging from running by default. |

Fail-closed conditions:

- target project root cannot be proven;
- shared runtime is missing in `shared` mode;
- helper would write outside `ProjectRoot`;
- helper would install PySide6 into consumer `.venv` in `shared` mode;
- project-local override lacks `OverrideReason`;
- visible GUI or packaging would run without explicit trigger.

## 9. Runtime Contract and State Model

Default consumer contract:

```json
{
  "schema_version": 1,
  "runtime_mode": "shared",
  "runtime_owner_repo": "D:/PythonProject_langgraph",
  "runtime_root": "D:/PythonProject_langgraph/.shared_runtimes/pyside6",
  "runtime_python": "D:/PythonProject_langgraph/.shared_runtimes/pyside6/.venv/Scripts/python.exe",
  "project_root": "<target-project-root>",
  "business_runtime_mode": "project-local-adapter",
  "import_only_smoke": "required",
  "visible_gui_requires_explicit_request": true,
  "packaging_requires_explicit_request": true,
  "project_local_override_reason": null
}
```

Capability states:

| State | Meaning | Promotion evidence |
| --- | --- | --- |
| `documented` | Plan and governance exist. | Bilingual plan and registry. |
| `repo_helper_ready` | Helpers/templates/checkers are present. | Repo guard and targeted tests pass. |
| `shared_runtime_ready` | Local shared runtime can import PySide6. | Shared runtime `verify` output and `runtime.json`. |
| `project_previewed` | A target project preview is clean. | Preview JSON with no blockers. |
| `project_gui_scaffolded` | Target project has generated GUI files. | Project diff and contract file. |
| `project_gui_verified_with_shared_runtime` | Import-only smoke passed through shared runtime. | Smoke JSON with `import_only_verified=true`. |
| `project_local_override_ready` | Target has an approved independent runtime. | Override reason, dependency/lock evidence, rollback. |
| `visible_gui_verified` | Interactive GUI was intentionally checked. | Screenshot, manual QA checklist, or GUI-capable test evidence. |
| `packaged` | Executable/package was intentionally built. | Packaging preflight and build receipt. |

Do not skip from `shared_runtime_ready` to `visible_gui_verified` or `packaged`.

## 10. Safety, Privacy, Rollback, and Authorization

Safety rules:

- Preview before apply.
- Write only inside the explicit target project root during project opt-in.
- Do not modify user-level Codex config or plugin cache.
- Do not copy consumer business data into this repository.
- Do not commit `.shared_runtimes/`, `.venv`, Qt binaries, wheels, caches, screenshots, logs, or package outputs unless a later plan explicitly defines a sanitized evidence artifact.
- Visible GUI and packaging are side-effectful and require explicit current-task authorization.

Rollback:

- Shared runtime rollback: delete `.shared_runtimes/pyside6` and rerun provision if needed.
- Consumer shared-mode rollback: remove generated GUI source, `tools/gui/`, tests, docs, and contract file according to the project's rollback note.
- Project-local override rollback: remove dependency declaration and lockfile change according to recorded override evidence.
- Packaging rollback: remove local build/dist artifacts and restore any packaging config changed for the package.

## 11. Ready / Bootstrap / Repair Lane Gates

| Lane | Entry condition | Allowed actions | Exit evidence |
| --- | --- | --- | --- |
| Ready | Shared runtime exists and project preview has no blockers. | Apply GUI scaffold, run import-only smoke. | `project_gui_verified_with_shared_runtime`. |
| Bootstrap | Shared runtime missing or stale, but repository maintenance is authorized. | Provision or verify only `.shared_runtimes/pyside6`. | `shared_runtime_ready`. |
| Repair | Existing project GUI or runtime contract is inconsistent. | Read, diagnose, propose bounded fixes; write only after target ownership is clear. | Fixed preview/smoke evidence. |
| Override | Project has a specific reason not to use shared runtime. | Create project-local dependency record and smoke path. | Override reason, lock evidence, rollback. |
| Packaging | User explicitly asks for executable/installable output. | Run packaging preflight and build. | Packaging receipt and rollback evidence. |

## 12. Implementation Items (ordered, fine-grained)

This checklist lists concrete implementation items only. It intentionally does not list "update this plan file" as an implementation item.

### 12.1 Completed or already present

- [x] Inventory existing PySide6 GUI baseline: templates, helper, skill, operator docs, project opt-in checker, packaging opt-in checker.
- [x] Change the default strategy from project-local PySide6 install to repository-owned shared PySide6 runtime.
- [x] Define the default shared runtime path as `D:\PythonProject_langgraph\.shared_runtimes\pyside6`.
- [x] Add `.shared_runtimes/` to `.gitignore`.
- [x] Add shared runtime requirements and metadata templates.
- [x] Add `ensure-shared-pyside6-runtime.ps1`.
- [x] Implement shared runtime `preview`, `provision`, and `verify` modes.
- [x] Emit structured JSON for shared runtime status, blockers, planned actions, and rollback.
- [x] Add `-RuntimeMode shared|project-local-override` to project opt-in helper.
- [x] Default project opt-in to `shared`.
- [x] Add `-RuntimeRoot` defaulting to the shared runtime path.
- [x] Forbid dependency declaration writes in shared mode.
- [x] Fail closed when shared runtime is missing in shared mode.
- [x] Generate `tools/gui/pyside6_runtime_contract.json` in shared mode.
- [x] Generate `tools/gui/adapters/README.md` in shared mode.
- [x] Update import-only smoke template to add target `src` to `sys.path` when shared runtime Python is used.
- [x] Update project `tools/gui/run_gui.ps1` template to launch through shared runtime.
- [x] Keep consumer GUI source, adapters, tests, helper, and rollback note in the consumer project.
- [x] Require `-OverrideReason` for project-local override.
- [x] Preserve dependency/lockfile and rollback evidence for override.
- [x] Update repo-local `pyside6-gui` skill for shared-runtime default behavior.
- [x] Update bilingual operator usage guidance for preview/apply/verify.
- [x] Add and register PySide6 shared runtime contract checker.
- [x] Extend helper, template, skill, operator, project opt-in, and packaging checkers.
- [x] Fix rollback note generation so PowerShell does not serialize ordered dictionaries into path lists.
- [x] Register PySide6 checks in repository guard and CI manifest.
- [x] Run targeted PySide6 tests, OpenSpec guard, precommit gate, local MR review, and local CI for the shared-runtime baseline.
- [x] Merge the shared-runtime default strategy into local `main`.
- [x] Provision the real local shared runtime under `.shared_runtimes/pyside6`.
- [x] Verify the local shared runtime with import-only evidence.
- [x] Complete first registered consumer shared-mode opt-in and import-only smoke evidence.
- [x] Record first-consumer evidence in memory artifacts rather than this generic plan.
- [x] Decide that per-project `tools/gui/run_gui.ps1` remains sufficient until repeated cross-project launcher duplication is proven.

### 12.2 Remaining explicit-trigger gates

- [ ] Execute `project-local-override` only for a named project with independent version, isolation, offline distribution, self-contained packaging, or experiment needs; record override reason, dependency/lock evidence, and rollback.
- [ ] Execute visible GUI validation only after the user explicitly asks for an interactive window, screenshot review, manual QA, or GUI-capable test runner.
- [ ] Execute PyInstaller/Nuitka packaging only after the user explicitly asks for executable or installer output and packaging preflight passes.

### 12.3 Maintenance backlog

- [ ] Reopen the cross-project launcher decision only after at least two consumer projects show repeated launcher logic that per-project wrappers cannot absorb.
- [ ] Add a sanitized shared-runtime upgrade receipt when PySide6/Qt/Python is intentionally upgraded.
- [ ] Add consumer-project compatibility notes when more than one project depends on the shared runtime.
- [ ] Promote repeated failure patterns into checkers rather than relying on chat reminders.

## 13. Implementation Slices

### Slice 0: plan and OpenSpec evidence closure

- Scope: maintain this bilingual plan pair and OpenSpec/Comet support artifacts.
- Done when: plan structure is complete, OpenSpec validates, and local gates pass.

### Slice 1: shared runtime maintenance

- Scope: provision, verify, upgrade, or rebuild `.shared_runtimes/pyside6`.
- Done when: `runtime.json` and import-only verify evidence are updated.

### Slice 2: consumer shared-mode opt-in

- Scope: preview/apply/smoke for one named target project.
- Done when: target project has contract, wrapper, GUI shell, tests, rollback note, and import-only smoke evidence.

### Slice 3: project-local override

- Scope: independent consumer runtime.
- Done when: reason, dependency/lock evidence, smoke, and rollback evidence exist.

### Slice 4: visible GUI validation

- Scope: interactive launch or screenshot/manual QA.
- Done when: explicit request and GUI evidence are recorded.

### Slice 5: packaging opt-in

- Scope: PyInstaller/Nuitka or another packaging path.
- Done when: packaging preflight, build receipt, artifact exclusion, and rollback evidence exist.

## 14. File Ownership Map

| Path | Owner | Notes |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md` | This repository | English canonical plan. |
| `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.zh-CN.md` | This repository | Chinese companion. |
| `openspec/changes/refine-pyside6-gui-plan-comet-structure/` | This change | Plan-contract evidence only. |
| `docs/superpowers/specs/2026-05-27-pyside6-gui-plan-comet-design.md` | This change | Design record. |
| `docs/superpowers/plans/2026-05-27-refine-pyside6-gui-plan-comet-structure.md` | This change | Execution record. |
| `.shared_runtimes/pyside6/` | Local machine | Ignored runtime artifact; not committed. |
| `tools/pyside6_gui_helpers/` | This repository | Reusable helper source. |
| Consumer `src/*_gui/`, `tools/gui/`, `tests/test_gui_import.py` | Consumer project | Written only during named consumer opt-in. |

## 15. Local Integration Order and Evidence Retention

1. Use a dedicated feature worktree and branch.
2. Keep the primary directory on local `main`.
3. Update the English and Chinese plan pair together.
4. Keep OpenSpec and Superpowers support artifacts bilingual when paired files are created.
5. Run `git diff --check`.
6. Run `openspec validate refine-pyside6-gui-plan-comet-structure --strict`.
7. Run `python .\tools\check_implementation_plan_rules.py --root . --json`.
8. Run `python .\tools\check_precommit_update_archive.py --root . --json`.
9. Run `python .\tools\run_openspec_guard.py --root .`.
10. Commit with a Chinese commit message.
11. Run local CI and local MR review before local `main` integration.
12. Create a local rollback backup ref before merging into local `main`.
13. Merge to local `main` only after local evidence is clean.
14. Clean the integrated feature worktree and local branch through the cleanup helper.
15. Stop before remote publication unless the current user message explicitly authorizes GitLab/GitHub publication.

## 16. Verification Plan

- `git diff --check` - checks whitespace and patch hygiene.
- `openspec validate refine-pyside6-gui-plan-comet-structure --strict` - validates the active OpenSpec change.
- `python .\tools\check_implementation_plan_rules.py --root . --json` - checks implementation-plan registry and bilingual text health.
- `python .\tools\check_precommit_update_archive.py --root . --json` - enforces update/archive review before commit.
- `python .\tools\run_openspec_guard.py --root .` - runs the repository OpenSpec and governance guard.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` - runs the local MR review gate before local main integration.

For future consumer-project opt-in, add target-specific preview JSON and import-only smoke JSON. For visible GUI and packaging, add explicit request evidence and receipts.

## 17. Related Governance / Plan Update Requirements

Update related docs or checkers when any of these change:

- shared runtime root or layout;
- helper CLI arguments or JSON schema;
- default runtime mode;
- project-local override criteria;
- visible GUI authorization boundary;
- packaging artifact handling;
- consumer-project evidence retention rules;
- skill/profile routing rules for `pyside6-gui`.

Do not update global Codex config, plugin cache, or user-level launcher behavior as part of this plan unless a separate approved plan says so.

## 18. Risks and Default Decisions

| Risk | Default decision | Mitigation |
| --- | --- | --- |
| Shared runtime drift affects multiple projects. | Treat upgrades as repository maintenance changes. | Runtime receipt, import-only smoke, consumer compatibility notes. |
| Consumer project accidentally installs PySide6 locally. | Default shared mode forbids dependency writes. | Helper/checker fail closed. |
| Visible GUI blocks automation. | Do not launch visible GUI by default. | Explicit interactive gate. |
| Packaging commits large artifacts. | Packaging is opt-in and local artifacts are excluded. | Packaging preflight and rollback receipt. |
| Plan text is mistaken for runtime readiness. | Use explicit capability states. | Do not promote without smoke/receipt evidence. |
| Cross-project launcher is overbuilt too early. | Keep per-project wrapper as default. | Reopen only after repeated evidence from two or more consumers. |

## 19. Self-checklist

- [x] The plan has the newer Comet executable structure.
- [x] The plan keeps English and Chinese files paired.
- [x] The plan preserves the shared runtime path and local-only rule.
- [x] The plan states that PySide6 is not installed globally or into every project by default.
- [x] The plan separates shared runtime readiness from consumer-project GUI readiness.
- [x] The plan keeps project-local override, visible GUI, and packaging as explicit-trigger gates.
- [x] The plan includes ordered fine-grained implementation items.
- [x] The plan includes verification, rollback, risk, and evidence-retention rules.
- [x] The plan does not authorize remote publication.

## 20. References

- `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md` - the nearest full Comet executable-plan structure used for GUI-related planning.
- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md` - the newer sidecar-plan structure used as a contract and gate reference.
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md` - the Comet management-record and Monitoring semantics reference.
- `docs_bilingual/memory/pyside6_first_consumer_apply_2026-05-22.md` - first-consumer shared-mode apply evidence.
- `docs_bilingual/memory/pyside6_explicit_trigger_gates_2026-05-22.md` - explicit high-impact gate evidence for override, visible GUI, and packaging.
