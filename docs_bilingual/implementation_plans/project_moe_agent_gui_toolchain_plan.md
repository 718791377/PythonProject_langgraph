---
doc_id: project_moe_agent_gui_toolchain_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
status: active
plan_readiness: full-comet-structure-ready-for-implementation-slicing
doc_class: implementation_plan
created_at: 2026-05-20
updated_at: 2026-06-06
last_reviewed_at: 2026-06-06
scope: project_moe_agent_gui_only
implementation_lane: ready_bootstrap_repair_lanes
comet_change: refine-project-moe-gui-plan-comet-structure
related_docs:
  - docs_bilingual/implementation_plans/project_moe_gui_enhancement_roadmap_plan.md
  - docs_bilingual/implementation_plans/project_moe_gui_double_click_launch_repair_plan.md
  - docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
  - docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.md
---

# Project MOE Agent GUI Toolchain Implementation Plan (Full Comet Refactor)

> **For agentic workers:** REQUIRED SUB-SKILL: prefer `$comet` as the control layer, then use `superpowers:writing-plans` / `superpowers:executing-plans` to implement task-by-task. Every step must use checkbox tracking. After each task, run the local verification for that item before moving on. If Comet bash scripts are unavailable on Windows, record the blocker and archive deferral; do not pretend `comet-state.sh` / `comet-guard.sh` succeeded.

**Goal:** Provide a reusable, installable, rollback-friendly project-level MOE Agent control surface for each local target project: target projects keep their own MOE Agent, private prompt source, Phase 1 CLI, and `.omx/state/<namespace>/`; this repository maintains the shared readiness checker, installer, PySide6 GUI shell, launcher templates, and validation fixtures.

**Architecture:** This repository provides the Project MOE GUI toolchain; target projects provide the Phase 1 JSON CLI contract. The GUI reads and writes state only through the target project's CLI and never edits target JSON directly. Projects are routed through Ready / Ready-candidate / Bootstrap / Repair lanes, and no real GUI control is allowed before readiness is proven.

**Tech Stack:** OpenSpec / Comet trace, Python CLI/checker, PySide6 shared runtime, Windows `.cmd` / PowerShell launcher, repo-local `.omx/state`, JSON contract, manifest/hash gate, local-first Git flow.

---

## 0. Full Comet Refactor Conclusion

- 2026-06-02 double-click launch repair: the standalone plan `project_moe_gui_double_click_launch_repair_plan.md` governs the B+A local fix for `D:\PythonProject_paper_suggest\project-moe-gui.cmd` closing without a visible GUI.
This document has been refactored from a loose status note plus scattered task list into an executable implementation plan with Comet trace evidence and readiness-lane contracts. It follows the same top-level pattern as `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`, but it does not reuse Pi sidecar runtime boundaries.

| Check | Result | Where it lands |
| --- | --- | --- |
| Comet / OpenSpec trace | complete | Sections 3, 14, 15; `openspec/changes/refine-project-moe-gui-plan-comet-structure/` |
| Goal / non-goal clarity | complete | Section 2 |
| Project MOE / GUI / target-project boundary | complete | Sections 1, 4, 6, 7 |
| Ready / Bootstrap / Repair lane | complete | Section 13 |
| Phase 1 CLI / readiness contract | complete | Section 9 |
| Phase 2 PySide6 GUI contract | complete | Section 10 |
| A/B validation route | confirmed | Sections 0, 1, 13, 14, 15 |
| JSON state model | complete | Section 11 |
| Security, privacy, rollback, uninstall | complete | Section 12 |
| Implementation item granularity | reordered | Section 14 |
| Verification and local/remote boundary | complete | Section 15 |

Status interpretation:

- `status: active`: this is the current executable implementation plan; it is not a claim that the Project MOE GUI runtime is fully complete.
- `plan_readiness: full-comet-structure-ready-for-implementation-slicing`: the structure, boundaries, and task granularity are ready for code implementation slicing.
- `D:\PythonProject_paper_suggest`: A remains the Phase 1 owner; B must not reimplement A business Phase 1. Current GUI availability must always be based on fresh install/readiness/preflight evidence.
- 2026-06-01 decision: A owns real Phase 1 and B owns Phase 2 toolchain; validation must update/install into A rather than recreate A business logic inside B.
- 2026-06-01 evidence: old worktree `paper_suggest-thesis-moe-phase1` is stale and must not be used as current A truth; the new A repair worktree is `D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601`, committed as `560da0e` (A Phase 1 readiness-contract repair commit; the Chinese commit subject is kept only in the zh-CN companion).
- 2026-06-01 privacy boundary: A's `MOE.md` is ignored/private and was copied only into the A repair worktree for readiness validation; do not commit it and do not copy its full content into B documentation or tooling.
- 2026-06-01 readiness evidence: A repair worktree reached static `ready-candidate/control_mode_allowed=false` and read-contract `ready/control_mode_allowed=true` with stable `token=ok`; here `control_mode_allowed` means whether the Phase 1 readiness contract permits GUI write/control actions (`false` = read/static candidate only, `true` = control path may be exposed behind gates). Checked commands were `project-status`, `list-sessions`, `status`, and `assert-on`.
- 2026-06-01 A local-main evidence: A integrated `560da0e` (Phase 1 readiness-contract repair), `c6b92ae` (real Project MOE GUI install), and `ce23931` (shared-runtime launcher update). Rollback refs are `refs/backup/local-main/20260601-125126-before-thesis-moe-phase1-repair-20260601` and `refs/backup/local-main/20260601-215213-before-project-moe-gui-runtime-entry-update`.
- 2026-06-01 Phase 2 evidence: B toolchain `0.2.22` repairs target-launcher runtime entry by re-executing through configured `runtime_python`, guarding recursion with `PROJECT_MOE_GUI_RUNTIME_REEXEC`, and setting `PYTHONUTF8=1`. The installed preflight payload records `launcher_runtime_python` and `launcher_runtime_reexec`.
- 2026-06-01 correction evidence: A later showed an installed `toolchain_source_root` still pointing at a deleted B feature worktree, so A launcher preflight returned `blocked:phase1_readiness_gate_unavailable / No module named 'project_moe_gui'`; the previous "launcher preflight ok" is historical evidence, not current availability.
- 2026-06-01 Phase 2 fix slice: B toolchain `0.2.23` writes stable source root `D:\PythonProject_langgraph\tools\project_moe_gui_toolchain`, adds a source-root existence/import checker, and lets updater repair recoverable installs whose manifest still matches but source root is unavailable.
- 2026-06-01 acceptance boundary: A remains a Ready Lane target, but current GUI preflight availability must be re-established by updating A managed artifacts to 0.2.23 and rerunning install check, readiness, and launcher preflight; no-argument / double-click launch is now the human-visible path after `0.2.25`; `--preflight --json` remains the automation path.
- 2026-06-01 scaffold apply slice: B toolchain `0.2.24` adds protected `scaffold_project_moe_phase1.py --apply`. It creates only missing Bootstrap Lane files after project-evidence and clean Git dirty-state checks pass, refuses to overwrite existing private or operator surfaces, and keeps GUI control disabled until later readiness evidence returns Ready Lane.
- 2026-06-02 human-friendly launcher slice: B toolchain `0.2.25` makes installed no-argument / double-click `project-moe-gui.cmd` open the visible PySide6 GUI by default for human operators, while preserving `--preflight --json` as the non-visible automation interface and blocking `--json` without `--preflight` from becoming an accidental machine-visible launch path.
- 2026-06-02 visual/daemon decision: later packages must keep the styled card/sidebar/status UI, license metadata, no-console daemon launch, duplicate lock, and close confirmation with explicit Exit / Hide-to-tray / Cancel behavior.
- 2026-06-05 silent launch and expert workbench slice: B toolchain `0.2.27` adds `project-moe-gui-silent.vbs` as a no-console double-click entry while keeping `project-moe-gui.cmd` as the diagnostic entry; the daemon human-GUI child prefers `pythonw.exe` when available and otherwise keeps the `python.exe + CREATE_NO_WINDOW / DETACHED_PROCESS` fallback; the GUI adds `Expert Workbench`, which only generates runtime/clipboard task briefs and never starts Codex, subagents, model APIs, or reads/copies target private `MOE.md`.
- 2026-06-05 next slice freeze: Expert Workbench v2 and session-scoped MOE lens selection remain incomplete. v2 must support multi-lens selection, per-session MOE/lens/category controls, and handoff packages for `main-session`, `subagent`, `durable-team`, and `langgraph-workflow`; the GUI still must not execute those carriers or model APIs.
- 2026-06-06 visual overflow correction: B toolchain `0.2.30` fixes the Sessions page overflow missed by earlier visual smoke checks, also fixes the Expert Workbench bottom-action overflow, and adds `visual_render_check.py` as a multi-page offscreen gate for `Project`, `Sessions`, `Expert Workbench`, `Diagnostics`, and `Settings` with visible-text and non-scroll-container overflow checks.
- Current Comet change: `refine-project-moe-gui-plan-comet-structure`. If bash is unavailable, only OpenSpec artifacts, repo-local guards, and local validation can be used as fallback evidence.

Inline field definitions:

- `readiness_status` is the target project's final Phase 1 contract readiness classification; `static-ready-candidate` means the read-only static checks satisfy candidate conditions but the target CLI read contract has not run yet, and `ready` means the read contract passed.
- `adaptation_lane` is the target project's next handling lane; `ready-candidate` may only proceed to further validation, while `ready` may enter the next install or GUI-control step.
- `control_mode_allowed` says whether GUI write/control is allowed; `false` permits display or dry-run only, while `true` still requires an install receipt, rollback pointer, and target-project acceptance before real operation.
- `token=ok` is the stable machine-readable success token returned by the target CLI or installer, so success is not inferred from prose output.
- `blockers=[]` means the dry-run found no blockers; it is not evidence that a real installation has completed.
- `launcher_runtime_python` records the interpreter that actually runs the installed launcher; `launcher_runtime_reexec=true` proves that an ambient Python invocation re-entered through the configured shared PySide6 runtime.

## 1. Relationship Model and Naming Boundary

| Name | Role | Source of truth | Boundary |
| --- | --- | --- | --- |
| Project MOE Agent | The target project's own expert-style Agent | `<project>/.codex/agents/*.toml` | Do not install it into user-level agents as a shared Agent |
| Private prompt source | Target-project private constraints, mentor guidance, domain rules | `<project>/MOE.md` or equivalent | Checker validates path/existence only, not full-text copying |
| Phase 1 CLI | Target-project MOE state read/write entrypoint | `<project>/tools/<mode>_moe_mode.py` | GUI must use CLI reads/writes, not direct JSON edits |
| Phase 2 GUI | PySide6 control surface maintained by this repository | `tools/project_moe_gui_toolchain/` | After installation it controls only the installed target project |
| Readiness checker | Read-only gate before install/control | This repository's toolchain | Emits go/no-go and blockers only |
| `.omx/state/<namespace>/` | Target-project MOE state | Target-project repo-local state | No cross-project scanning, no writes to other projects |

### 1.1 MOE experts, subagents, and skills boundary

- A MOE expert is an expert lens / routing semantic, such as blind-review expert, advisor interrogation expert, AIGC-risk expert, or novelty gatekeeper. It describes which professional perspective is used; it is not an execution carrier by itself.
- A subagent / native agent is an execution carrier or role thread, such as Codex built-in roles, user-level agent TOMLs, or project-local `.codex/agents/*.toml`. One subagent may contain multiple MOE expert lenses, and the main session may also use MOE expert lenses directly.
- Therefore MOE experts and subagents form a composable matrix relationship. They are not synonyms and are not mutually exclusive; calling a MOE lens must not be recorded as native subagent evidence.
- Calling MOE experts does not require dedicated skills. `MOE.md`, agent TOML, or main-session context can carry MOE routing rules; skills are optional workflow wrappers only, and skill/profile invocation cannot replace native expert evidence.
- Expert Workbench v2 may only generate a copyable handoff package / brief. The handoff target may be labelled `main-session`, `subagent`, `durable-team`, or `langgraph-workflow`, but the GUI itself does not execute those carriers.
- Session-scoped lens selection applies only to the currently selected session and does not mutate project-default lens policy. `selected_lenses=[]` plus `selected_categories=[]` means "all available lenses are enabled for this session," not "unconfigured" or "off".

Default names:

- Toolchain namespace: `project_moe_gui`
- State namespace example: `thesis_moe`
- Target launcher example: `project-moe-gui.cmd`
- Target CLI example: `tools/thesis_moe_mode.py`

## 2. Goals and Non-Goals

Goals:

1. Provide project-default MOE toggles, single-session overrides, state reads, and fail-closed assertions for each target project.
2. Provide a unified JSON contract so the PySide6 control surface can display project-default state, session lists, readiness blockers, and write results.
3. Route projects with missing Phase 1 into Bootstrap Lane and only output gap lists and scaffold dry-runs.
4. Route projects with partial Phase 1 into Repair Lane and require explicit fixes before GUI control is enabled.
5. Allow GUI installation and use only for projects that satisfy all readiness gates.
6. Make install, update, rollback, uninstall, and verification fully traceable through manifest/receipt records.
7. Provide per-session MOE enable/disable, lens multi-select, category multi-select, clear-selection, and readback confirmation.
8. Provide Expert Workbench v2 multi-lens brief generation and execution-carrier handoff package selection.

Non-goals:

- Do not use GUI to bypass the target project's Phase 1 readiness gate.
- Do not copy the target project's private `MOE.md` verbatim.
- Do not default-install project-specific MOE Agents into `C:\Users\lenovo\.codex\agents`.
- Do not build a cross-project master console or default cross-project scanning.
- Do not let the GUI edit `.omx/state` JSON directly.
- Do not treat workflow skills, plugin profiles, or GUI profile loading as native expert evidence.
- Do not let Expert Workbench directly start the main session, subagents, durable teams, LangGraph workflows, or any model API; it only generates handoff packages.
- Do not push GitLab/GitHub, open MRs, merge remotes, or sync mirrors without explicit remote-publication approval.

## 3. Comet / OpenSpec Work Boundary

| Phase | This file | Rule |
| --- | --- | --- |
| Open | `proposal.md`, `.openspec.yaml` | Define why/what/scope/non-goals/rollback/validation |
| Design | `design.md`, `docs/superpowers/specs/*design.md`, delta spec | Freeze structure choice, lane model, contract boundary |
| Build | This document, `docs/superpowers/plans/*`, `tasks.md` | Execute the plan and tick items |
| Verify | `git diff --check`, `openspec validate`, repo guards, precommit gate | Do not claim success without fresh evidence |
| Archive | A later step | If bash is unavailable or the branch is not ready, record archive deferral explicitly |

Current strategy:

- The initial slice was documentation / plan work; the current continuation includes bounded Project MOE GUI toolchain runtime work and target-project readiness evidence closure.
- The next validation route is "repair A's real Phase 1, then validate B's Phase 2 installation", not "copy A's business Phase 1 into B".
- Until A's readiness checker outputs `control_mode_allowed=true`, do not install the PySide6 GUI into A, start real GUI control, or write user-level directories.
- This work is authorized for local feature commit and local `main` integration only; remote publication still requires a later explicit user instruction.

### 3.1 Comet management record, phase-gate, and Monitoring semantics

This plan follows the newer Comet runtime-control structure, but Project MOE GUI remains a Project MOE toolchain plan rather than a Comet runtime implementation. The reusable semantics are:

| Concept | Required interpretation for this plan |
| --- | --- |
| Management record | `management.md` is the phase evidence ledger for Open, Design, Build, Verify, Archive, and Monitoring. It is not a decorative note; it is evidence for why the current phase may advance. |
| Phase gate | A forward transition is valid only when the phase checklist is complete and Monitoring says `clear` / `continue`. If Comet bash scripts are unavailable on Windows, file-state evidence must be recorded instead of claiming a script transition. |
| Monitoring loop | Monitoring is a cross-phase control loop, not a sixth Comet phase. Return decisions map to `return-open`, `return-design`, `return-build`, or `return-verify`, with a concrete reason and preserved artifacts. |
| Evidence retention | Verification output, archive deferral, worktree receipts, and changed-path summaries must stay in repo-local artifacts, not only in chat history. |
| Approval boundary | Local feature work and local `main` integration follow the local-first policy; remote publication, target-project writes, destructive cleanup outside the approved flow, and scope expansion need explicit user authorization. |

### 3.2 Full `/comet` structure parity checklist

The target structure must be same-level with the newer Pi sidecar plan and must also inherit the Comet runtime plan's control semantics:

| Reference structure | Project MOE GUI mapping |
| --- | --- |
| Review conclusion | Section 0 records readiness, draft status, and what is still not implemented. |
| Relationship / naming boundary | Section 1 separates target-project MOE Agents, private prompt sources, Phase 1 CLI, Phase 2 GUI, checker, and state namespace. |
| Runtime architecture and usage | Sections 4-5 define operator, launcher, GUI, CLI, and target-state interactions. |
| Source of truth | Section 6 keeps shared toolchain source in this repository and target state in target projects. |
| Install artifacts / receipt | Section 7 defines target managed files and manifest requirements. |
| CLI / JSON / state contract | Sections 9-11 define read/write commands, envelopes, state files, effective-state precedence, and stable failure tokens. |
| Readiness gates | Section 13 defines Ready, Ready-candidate, Bootstrap, and Repair lanes. |
| Implementation backlog | Section 14 uses ordered slices plus item-level checkboxes, file ownership, local integration order, and evidence-retention rules. |
| Verification / rollback / self-check | Sections 12, 15, 17, and 18 define safety, rollback, validation, risks, and completion criteria. |

## 4. Runtime Architecture

```text
Operator / Codex session
  -> target project startup/readiness check
  -> target project Phase 1 CLI JSON contract
  -> Project MOE GUI launcher installed in target project
  -> PySide6 GUI shell from this repository's toolchain
  -> target project .omx/state/<namespace>/ JSON files
```

Core rules:

- The GUI first locates the target project's root, then runs the readiness checker.
- The readiness checker is read-only; it may execute safe JSON read commands, but it may not modify the target project.
- Write commands are only allowed through the target project's Phase 1 CLI: `project-on`, `project-off`, `on --session-id`, `off --session-id`.
- After any write, the GUI must re-read state and must not trust local UI predictions.
- Dirty target projects, incomplete CLI contracts, unsafe wrappers, missing startup hooks, or prompt-source boundary violations must fail closed.

## 5. How Codex, the GUI, and Target Projects Interact

Example operator intents:

```text
Check whether this project can enable Project MOE GUI
Generate a Project MOE Bootstrap Lane gap list for this project
Open the current project's MOE GUI
Turn on the current project's MOE default state
Turn off the selected session override
```

Target-project CLI surface:

```powershell
python .\tools\thesis_moe_mode.py project-on --json
python .\tools\thesis_moe_mode.py project-off --json
python .\tools\thesis_moe_mode.py project-status --json
python .\tools\thesis_moe_mode.py list-sessions --json
python .\tools\thesis_moe_mode.py on --session-id <id> --json
python .\tools\thesis_moe_mode.py off --session-id <id> --json
python .\tools\thesis_moe_mode.py status --json
python .\tools\thesis_moe_mode.py assert-on --json
```

GUI launch examples:

```powershell
<project>\project-moe-gui.cmd
python <project>\tools\project_moe_gui\launcher.py --project-root <project>
```

The GUI must show: project root, branch, agent name, state namespace, readiness lane, project-default state, session list, recent write summary, error token, and suggested next action.

## 6. Repo-local Source of Truth

This repository maintains:

```text
tools/project_moe_gui_toolchain/
  src/project_moe_gui/
  install_project_moe_gui.py
  update_project_moe_gui.py
  check_project_moe_gui_install.py
  check_project_moe_phase1_readiness.py
  scaffold_project_moe_phase1.py
  templates/
```

Supporting governance and verification:

```text
docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
openspec/changes/<project-moe-change>/
tests/project-moe-gui/
```

Responsibilities:

- `install_project_moe_gui.py`: copy/generate target-project managed artifacts and write an install manifest.
- `update_project_moe_gui.py`: update managed artifacts in a controlled way after reading the manifest.
- `check_project_moe_gui_install.py`: verify install state and hashes.
- `check_project_moe_phase1_readiness.py`: read-only gate for whether the target project can be controlled by the GUI.
- `scaffold_project_moe_phase1.py`: Bootstrap Lane dry-run planner; default no target-project writes.

## 7. Target Install Artifacts and Manifest

Target installation layout:

```text
<project>/tools/project_moe_gui/
  launcher.py
  project_moe_gui.config.json
  project_moe_gui.install-manifest.json
<project>/project-moe-gui.cmd
```

Minimal manifest fields:

```json
{
  "schema_version": 1,
  "tool": "project_moe_gui",
  "status": "installed",
  "installed_at": "2026-05-27T00:00:00Z",
  "source_repo": "D:/PythonProject_langgraph",
  "source_commit": "<git sha>",
  "target_project": "<project>",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "managed_files": [],
  "readiness_status": "ready|ready-candidate|blocked",
  "control_mode_allowed": false,
  "rollback_pointer": null,
  "secrets_recorded": false
}
```

Rules:

- Without a manifest, a project can only be `not-installed`.
- If the manifest hash does not match, update/uninstall must fail closed.
- The installer must not default-generate a private `MOE.md` body; if scaffold is needed, create only a placeholder and require human completion.
- The installer must not default-generate `.codex/agents/*.toml` unless the user explicitly invokes a scaffold command and confirms the target path.

## 8. Target Agent TOML and Private Prompt Source Standard

Recommended TOML:

```toml
name = "thesis-moe-mentor"
description = "Project-local MOE mentor for thesis-quality review."
developer_instructions = """
Use the project-local private prompt source by reference. Do not copy full private content into shared tooling.
"""

[project]
scope = "repo-local"
state_namespace = "thesis_moe"
private_prompt_source = "MOE.md"
private_prompt_policy = "do-not-copy-full-content"

[moe]
kind = "project-moe-agent"
family = "project-specific"
requires_manual_enable = true
project_default_state = ".omx/state/thesis_moe/project-default.json"
session_state_dir = ".omx/state/thesis_moe/sessions"

[dispatch]
mode = "brief-based"
forbidden = ["full-history-fork-with-custom-role"]
fallback = ["main-session-takeover", "durable-brief"]

[extensions]
# Project-specific fields are allowed here.
```

Private prompt source rules:

- It must live inside the target project.
- It must not point to `.codex/agents/`, `.omx/state/`, `tools/project_moe_gui/`, or GUI managed artifacts.
- The readiness checker only validates path/existence and boundaries; it does not read or copy the full text.

## 9. Phase 1 CLI / Readiness Contract

Phase 1 is the target project's minimal MOE state interface.

| Command | Writes | Meaning |
| --- | --- | --- |
| `project-on --json` | yes | Enable project defaults and propagate to non-manual sessions |
| `project-off --json` | yes | Disable project defaults and propagate to non-manual sessions |
| `project-status --json` | no | Report defaults, session counts, invalid records, and path summaries |
| `list-sessions --json` | no | Return a redacted session list with session-scoped lens-selection summaries |
| `list-lenses --json` | no | Return a public MOE lens and category catalogue; never read/copy `MOE.md` body text |
| `on --session-id <id> [--lens <id> ...] [--category <id> ...] --json` | yes | Write a single-session manual enable override; may also set session-scoped lens/category selection |
| `off --session-id <id> --json` | yes | Write a single-session manual disable override while preserving existing lens selection for later re-enable |
| `set-lenses --session-id <id> [--lens <id> ...] [--category <id> ...] --json` | yes | Update only that session's lens/category selection; it does not mutate project defaults and does not mean disabled |
| `clear-lenses --session-id <id> --json` | yes | Clear that session's explicit lens/category selection so the effective lens mode returns to `all` |
| `status --session-id <id> --json` | no | Compute the effective MOE toggle and effective lens mode for the current or explicit session |
| `assert-on --json` | no | Succeed only when the effective state is on; otherwise return a stable blocker |

Readiness checker requirements:

- Git dirty state: run `git status --porcelain --untracked-files=all` with `GIT_OPTIONAL_LOCKS=0`.
- Agent TOML required fields and standard extension section.
- Private prompt path exists and does not escape the project root.
- CLI read-command envelope, `effective_source`, session counts, list structure, and privacy fields.
- Write-command surface declares `atomic_write`, `lock_status`, `audit_path`, `no_op`, `before`, `after`, `changed_paths`.
- `.cmd` wrapper only forwards controlled commands, forces `--json`, and forbids arbitrary `%*` pass-through or shell chaining.
- Startup / resume / continue / reload / phase-change checkpoints must read `status --json`.
- v2 lens commands such as `list-lenses`, `set-lenses`, and `clear-lenses`: envelope, value validation, privacy fields, write readback, and default-compatible semantics.

## 10. Phase 2 PySide6 GUI Contract

GUI v1 must include:

- Top project context: target root, branch, agent name, state namespace, readiness lane.
- Project-default card: effective default state, last update time, enable/disable buttons.
- Session table: redacted session id, source, confidence, enabled, effective_enabled, validity, lifecycle status, branch, worktree, first/last seen, reason summary.
- Action panel: refresh, enable project default, disable project default, enable selected session, disable selected session.
- Session lens panel: show available lenses/categories only for the currently selected session; support multi-select, apply, clear, and `effective_lens_mode` readback.
- Expert Workbench v2: support choosing one or more MOE lenses, choosing handoff target `main-session|subagent|durable-team|langgraph-workflow`, and generating a handoff package explicitly marked as not executed by the GUI.
- Log panel: actual command invoked, exit code, stable token, and redacted stdout/stderr summary.

GUI behavior rules:

- Refresh calls read-only commands only and never triggers write/migration/install.
- During a write, the same scope buttons are disabled and a loading state is shown.
- After a write completes, the GUI re-reads state.
- After lens writes complete, the GUI must re-read `status --session-id` and `list-sessions`; it must not trust local UI checkboxes alone.
- An empty session list must not be interpreted as MOE being disabled.
- Error display must include a stable token, a short explanation, and a recommended next action.
- State badges must use both text and color, not color alone.

### 10.1 QFluentWidgets visual contract

The next Project MOE GUI visual shell must use QFluentWidgets by default:

- The shared PySide6 runtime check must verify `PySide6-Fluent-Widgets` importability before enabling the styled shell.
- A GUI dependency license manifest must record package name, import name, version, source URL, declared license, license-review status, allowed local use, and whether commercial/public redistribution requires a new review.
- The GUI must fail closed to the plain PySide6 shell or a preflight blocker if QFluentWidgets is missing or the license manifest is absent; it must not silently claim the styled shell is ready.
- The visible shell must render a left sidebar, top status banner, cards, session table, diagnostics panel, and footer/status area from the existing view model.
- The shell must keep all state-changing actions routed through `execute_write_action_with_readback()` and target Phase 1 CLI contracts.

### 10.2 Project-level daemon and close interaction contract

The next human launcher must avoid persistent CMD windows:

- No-argument / double-click `project-moe-gui.cmd` starts a project-level daemon/watchdog and then returns quickly.
- Windows detached startup may use `subprocess` flags such as `CREATE_NO_WINDOW`, `DETACHED_PROCESS`, or an equivalent no-console combination; this is for the visible human path only.
- `--preflight --json` remains a foreground, non-visible, machine-readable path and must not spawn a daemon.
- The daemon records project-local lock / pid / status evidence and prevents duplicate GUI instances for the same target project.
- Closing the GUI window shows a confirmation dialog with `Exit`, `Hide to tray`, and cancel/close options.
- `Exit` terminates the GUI and lets the daemon exit; `Hide to tray` hides only after the operator explicitly chooses it and exposes tray actions `Show` and `Exit`; cancel keeps the window visible.
- If the system tray is unavailable, the hide option is disabled or reported as a stable blocker, while normal exit remains available.

## 11. JSON Contract and State Model

Unified envelope:

```json
{
  "schema_version": 1,
  "command": "status",
  "ok": true,
  "token": "ok",
  "exit_code": 0,
  "message": "short human message",
  "project_root": "<project>",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "generated_at": "2026-05-27T00:00:00Z",
  "warnings": [],
  "errors": []
}
```

Project-default state:

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "project-default",
  "enabled": true,
  "worktree": "D:/PythonProject_paper_suggest",
  "branch": "main",
  "updated_at": "2026-05-27T00:00:00Z",
  "reason": "project-on"
}
```

Session state:

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "session",
  "enabled": true,
  "session_id": "redacted-or-hash",
  "session_id_source": "argument|environment|generated",
  "session_confidence": "high|medium|low",
  "override_origin": "manual-session|project-propagated",
  "selected_lenses": [],
  "selected_categories": [],
  "effective_lens_mode": "all|selected",
  "lens_selection_scope": "session",
  "worktree": "D:/PythonProject_paper_suggest",
  "branch": "main",
  "first_seen_at": "2026-05-27T00:00:00Z",
  "last_seen_at": "2026-05-27T00:00:00Z",
  "updated_at": "2026-05-27T00:00:00Z",
  "reason": "manual-session-on"
}
```

Effective-state calculation:

1. A valid session override wins.
2. Otherwise use the valid project-default state.
3. Otherwise fail closed and treat the project as off.

Lens-selection compatibility semantics:

1. Legacy session state missing `selected_lenses` / `selected_categories` is treated as `[]`.
2. `selected_lenses=[]` and `selected_categories=[]` means `effective_lens_mode=all`, i.e. all available lenses are enabled for that session.
3. If either list is non-empty, `effective_lens_mode=selected`; `selected` means the effective session scope is narrowed to explicit lenses or lenses expanded from explicit categories only.
4. `list-lenses --json` returns only public structured lens/category metadata; it must not read, copy, or echo target-project private prompt source body text.

Failure tokens:

| Scenario | exit code | token |
| --- | ---: | --- |
| Successful read/write | 0 | `ok` |
| `assert-on` sees disabled | 1 | `disabled` / `blocked:moe_disabled` |
| Parameter error | 2 | `usage_error` |
| Corrupted state or schema mismatch | 3 | `state_corrupt` / `blocked:unsupported_schema_version` |
| Path, ownership, or dirty preflight block | 4 | `blocked:unsafe_target_root` / `blocked:dirty_unowned_files` |
| Missing dependency or configuration | 5 | `blocked:missing_agent_toml` / `blocked:missing_mode_cli` |
| State lock failure | 6 | `blocked:state_lock_timeout` / `blocked:stale_state_lock` |

## 12. Security, Privacy, Rollback, and Uninstall

Security rules:

- Resolve every target path and ensure it remains under the project root.
- symlink / junction / path traversal must fail closed.
- Writes must use a temporary file plus atomic rename.
- Concurrent writes must use locks; suspected stale locks only report blockers.
- The GUI must not display raw session ids, private prompt text, provider secrets, full environment variables, or full stderr.

Rollback rules:

- Record the manifest and rollback pointer before install.
- Compare managed-file hashes before update.
- Rollback only restores GUI managed artifacts; do not delete project-private Agent TOMLs, `MOE.md`, or `.omx/state`.
- Uninstall defaults to dry-run and only outputs `planned_deletes`.
- `--apply` is supported only after the manifest path allowlist and managed-file hash checks pass; it deletes only Project MOE GUI managed artifacts, reports `delete_executed=true`, and preserves `MOE.md`, `.codex/agents/*.toml`, and `.omx/state`.
- If any manifest path is outside the managed allowlist, any hash is missing or mismatched, or a managed entry is not a file, uninstall must fail closed before deleting anything.

Remote rules:

- This change and target-project adaptation default to local Git commits only.
- Without explicit remote-publication approval, do not push, open MRs, merge remotes, or sync mirrors.

## 13. Ready / Bootstrap / Repair Lane Gates

| Lane | Entry condition | GUI control | Output |
| --- | --- | --- | --- |
| Ready Lane | Phase 1 CLI, wrapper, startup hook, Agent TOML, private prompt source, dirty preflight all pass | allowed | `control_mode_allowed=true` |
| Ready-candidate | static-only checks pass but no target CLI execution evidence | forbidden | `control_mode_allowed=false`, execute read-contract evidence first |
| Bootstrap Lane | target project is missing Phase 1 | forbidden | gap list, scaffold dry-run, operator next steps |
| Repair Lane | target project has a Phase 1 candidate but blockers remain | forbidden | blocker groups, fix order, next action |

The readiness payload must include:

```json
{
  "readiness_status": "ready|ready-candidate|blocked",
  "adaptation_lane": "ready|ready-candidate|bootstrap|repair",
  "control_mode_allowed": false,
  "bootstrap_required": false,
  "repair_required": true,
  "static_surface_blocking_codes": [],
  "remediation_plan": []
}
```

`D:\PythonProject_paper_suggest` current classification: Ready Lane, but its installed GUI preflight was blocked by a stale `toolchain_source_root` pointing at a deleted feature worktree. A must be updated to B toolchain `0.2.23` and must pass install check, readiness, and launcher preflight again before current GUI preflight availability can be claimed.

The completed A convergence order was:

1. Repair the A agent TOML standard sections and wrapper / CLI JSON safety boundaries.
2. Add the startup activation hook and verify `project-status`, `list-sessions`, `status`, and `assert-on`.
3. Integrate A Phase 1 repair as `560da0e`.
4. Install B's Project MOE GUI into A and integrate the install as `c6b92ae`.
5. Repair B's installed-launcher runtime entry, update A to toolchain `0.2.22`, and integrate the A launcher update as `ce23931`.
6. Discover that stale `toolchain_source_root` can make install check look normal while launcher preflight fails.
7. Add stable source-root writing, source-root checker, and updater self-repair in B toolchain `0.2.23`.
8. Next, update A managed artifacts again and rerun install check, readiness, installed-launcher preflight, and A tests. This unlocks guarded GUI use but does not claim that a visible GUI window was launched.

## 14. Implementation Items (ordered, fine-grained)

### 14.1 Already completed or already present

- [x] Define the boundary between Project MOE GUI and the generic PySide6 capability plan.
- [x] Define the GUI source of truth in this repository and the target-project state source of truth in the target project.
- [x] Define the target install artifact and managed-manifest model.
- [x] Define that the GUI never edits state JSON directly.
- [x] Define the Ready / Ready-candidate / Bootstrap / Repair lane model.
- [x] Define that `D:\PythonProject_paper_suggest` cannot jump into GUI control just because a Phase 1 candidate exists.
- [x] Define the next route: repair A's real Phase 1 contract first, then use B's Phase 2 dry-run, install, and GUI acceptance; do not reimplement a full A business Phase 1 inside B as substitute evidence.
- [x] Define the MOE expert / subagent / skills boundary: MOE is an expert lens, subagent is an execution carrier, and skills are optional workflow wrappers.
- [x] Define that missing Comet bash scripts must not be faked.
- [x] Recast this document into the new Comet executable-plan structure.
- [x] Add Comet management-record, phase-gate, Monitoring-return, evidence-retention, and approval-boundary semantics to this plan.

### 14.2 Implementation slices

#### Slice 0: plan and OpenSpec evidence closure

- [x] Reuse the existing OpenSpec change `refine-project-moe-gui-plan-comet-structure`; do not open an unrelated duplicate change.
- [x] Keep `status: active` and use `plan_readiness` for implementation-slicing readiness, not runtime completion.
- [x] Keep the bilingual implementation-plan pair synchronized.
- [x] Keep `.comet.yaml` honest about Windows Comet bash unavailability.
- [x] Replace any corrupted Chinese OpenSpec / Superpowers support artifacts for this change with valid UTF-8 Chinese text.
- [x] Update `tasks.md` / `tasks.zh-CN.md` so this full `/comet` structural pass has explicit evidence.
- [x] Run OpenSpec validation and repository guard after the support artifacts are repaired.

#### Slice 1: Phase 1 readiness checker and schema

- [x] Define the `check_project_moe_phase1_readiness.py --json` envelope.
- [x] Add `ready`, `ready-candidate`, `bootstrap`, and `repair` fixture projects.
- [x] Add negative fixtures for missing Agent TOML, invalid TOML, missing private prompt source, unsafe private prompt path, missing CLI, unsupported CLI schema, and dirty target root.
- [x] Ensure static-only mode never executes a target project CLI.
- [x] Ensure read-contract mode only executes safe read commands.
- [x] Ensure readiness output includes lane, blockers, warnings, checked files, redacted paths, and `control_mode_allowed`.
- Evidence (2026-05-28): `harden-moe-readiness-output-contract-20260528` adds explicit `warnings`, `checked_files`, and `redacted_paths` evidence fields with ready/static-only regression coverage.
- Evidence (2026-05-28): the current schema-hardening OpenSpec change adds a stable fail-closed blocker for unsupported CLI envelope schema; its regression test proves readiness remains blocked; existing fixture coverage still proves the ready, ready-candidate, bootstrap, repair, static-only, and read-contract command boundaries.

#### Slice 2: Bootstrap and repair lane tooling

- [x] Freeze `scaffold_project_moe_phase1.py --dry-run --json` output.
- [x] Generate bootstrap actions without writing target files by default.
- [x] Add an explicit `--apply` path only after target ownership and dirty-state checks pass.
- Evidence (2026-06-01): toolchain `0.2.24` adds protected scaffold `--apply`; regression coverage proves clean targets create only missing Phase 1 files, dirty targets fail closed before writing, and existing private prompt / agent surfaces are not overwritten.
- [x] Produce a repair-lane report for partially implemented Phase 1 projects.
- [x] Preserve `D:\PythonProject_paper_suggest` as repair-lane until fresh checker evidence proves otherwise, then promote it only after real Ready Lane evidence exists.

#### Slice 3: target install, update, uninstall, and rollback manifest

- [x] Implement install artifact generation under `<project>/tools/project_moe_gui/`.
- [x] Generate `<project>/project-moe-gui.cmd` as a narrow launcher, not an arbitrary command passthrough.
- [x] Write `project_moe_gui.install-manifest.json` with source commit, managed files, hashes, target root, agent name, namespace, readiness result, and rollback pointer.
- [x] Implement update by comparing manifest hashes and source version.
- [x] Implement uninstall by deleting only manifest-owned managed files.
- [x] Create local uninstall receipts before deleting any managed target artifact and keep rollback hints in the JSON payload.
- [x] Write stable `toolchain_source_root` during target install/update instead of persisting feature worktree paths.
- [x] Make `check_project_moe_gui_install.py` fail closed when `toolchain_source_root` is missing or cannot import `project_moe_gui`.
- [x] Allow `update_project_moe_gui.py` to repair recoverable installs whose manifest still matches but `toolchain_source_root` is stale.

#### Slice 4: Phase 2 PySide6 GUI shell

- [x] Build the launcher preflight: target root selection, readiness check, read-contract check, and fail-closed blocker display.
- [x] Implement the project-default status card.
- [x] Implement the session table with desensitized session identifiers and lifecycle fields.
- [x] Implement project default on/off actions through target CLI only.
- [x] Implement selected-session on/off actions through target CLI only.
- [x] Disable same-scope write controls during writes and refresh state after every write.
- [x] Display stable failure tokens, concise explanations, suggested next actions, and redacted stdout/stderr summaries.

#### Slice 4A: QML Material visual shell, project daemon, and close confirmation

The current implemented visual path is Qt Quick/QML Material with optional legacy QFluentWidgets metadata, not a forced QFluentWidgets runtime dependency. Full QFluentWidgets adoption remains an optional future visual-library decision and is not a blocker for the current Project MOE GUI acceptance boundary.

- [x] Add visual dependency metadata and license-review fields for the optional QFluentWidgets surface.
- [x] Replace the minimal label-only window with a sidebar, top banner, cards, session table, diagnostics panel, and footer.
- [x] Preserve the existing view-model and target CLI read/write contract; no direct state JSON writes are allowed.
- [x] Implement a project-level daemon/watchdog path for no-argument / double-click launch so CMD exits quickly on Windows.
- [x] Use Windows no-console process flags such as `CREATE_NO_WINDOW` / `DETACHED_PROCESS` or equivalent guarded logic for the human visible launcher path.
- [x] Keep `--preflight --json` foreground and non-visible for automation.
- [x] Add project-local lock / pid / status handling to avoid duplicate GUI instances.
- [x] Add close confirmation with `Exit`, `Hide to tray`, and cancel behavior.
- [x] Add tray `Show` / `Exit` actions only after the operator explicitly chooses hide; do not auto-hide to tray.

#### Slice 4B: silent launch and Expert Workbench v1

- [x] Generate `<project>/project-moe-gui-silent.vbs` as the no-console double-click entry.
- [x] Keep `<project>/project-moe-gui.cmd` as the diagnostic entry, with `--preflight --json` still using foreground machine output.
- [x] Prefer `pythonw.exe` for daemon no-argument human-GUI children when it exists.
- [x] Keep `CREATE_NO_WINDOW / DETACHED_PROCESS` as the no-console fallback when `pythonw.exe` is unavailable.
- [x] Include the silent entry in manifest / config / update / uninstall allowlist.
- [x] Add an `Expert Workbench` GUI navigation page.
- [x] Load expert lenses only from public Agent TOML structured fields or safe defaults; do not read/copy `MOE.md` body text.
- [x] Generate briefs only; do not start Codex, subagents, durable workers, or model APIs.
- [x] Keep brief persistence runtime-and-clipboard-only by default; do not write disk or Git.
- [x] Add regression tests for silent entry, `pythonw.exe` selection, Expert Workbench privacy boundary, and QML page evidence.

#### Slice 4B-v2: session-scoped MOE lens selection and Expert Workbench v2

- [x] Extend Phase 1 CLI, scaffold template, and fixtures with list-lenses, set-lenses, clear-lenses, plus optional session --lens / --category.
- [x] Add compatible session fields: selected_lenses, selected_categories, effective_lens_mode, and lens_selection_scope=session; legacy records default to ll.
- [x] Extend the GUI view model and QML Sessions page with selected row, session MOE on/off, lens/category multi-select, apply, clear, readback token, and blockers.
- [x] Extend Expert Workbench v2 for multi-lens, target-labelled handoff packages for main session / subagent / durable team / LangGraph workflow.
- [x] Keep Workbench brief-only: no Codex, subagent, durable worker, LangGraph workflow, model API, disk write, or target-state write.
- [x] Extend privacy and regression coverage for lens commands, empty-selection=all, invalid selection fail-closed, legacy state, QML wiring, handoff targets, and private-surface exclusion.
- [x] B toolchain version is 0.2.29 so install/update artifacts carry the new QML/launcher contract.
- [x] B toolchain version is 0.2.30 so install/update artifacts carry the Sessions/Workbench overflow fix and multi-page visual render checker.

Follow-up after B local-main closure: update D:\PythonProject_paper_suggest and rerun install, readiness, launcher preflight, and target-project tests there.

Slice 4B-v2 evidence (2026-06-06): QML bridges project/session writes, refresh, and mandatory readback; Sessions has row selection plus MOE/lens controls; Workbench uses multi-lens clipboard-only handoff; tests cover argv, readback, QML, handoff, and privacy.

Visual overflow closure evidence (2026-06-06): `visual_render_check.py` must render `overview`, `sessions`, `workbench`, `diagnostics`, and `settings` at 1180x720; it requires key page text to be visible, rejects visible non-scroll-container overflow, allows scrollable TextArea/ScrollView content only inside its viewport, records screenshots, and fails on QML warnings.

#### Slice 5: Governance, Docs, and Checker Integration

The following are standing governance rules, not remaining product checkboxes:

- Register new checkers in repository guard and CI manifest at the same time.
- Update the PySide6 cross-project capability plan only when shared runtime and launcher boundaries change.
- Update Project MOE-specific docs only when MOE GUI state, readiness, and installer behavior change.
- Do not treat workflow skills, plugin profiles, or GUI profile loading as native-expert evidence.
- Reference private prompt sources only; do not copy body text.

Dedicated docs/checker closeout completed in this slice:

- [x] Record the stale `toolchain_source_root` risk in the Project MOE-specific plan.
- [x] Move standing governance rules out of empty todo checkboxes to avoid treating them as incomplete product work.
- [x] Add regression coverage for the source-root checker and updater self-repair.

#### Slice 6: target-project acceptance and rollout

- [x] Classify old A worktree `paper_suggest-thesis-moe-phase1` as stale evidence and stop using it as current A truth.
- [x] Create a new repair worktree from A's current `main`: `D:\PythonProject_langgraph\.worktrees\paper_suggest-moe-phase1-repair-20260601`.
- [x] Keep A's `MOE.md` as an ignored/private file, copied only into the A repair worktree for readiness validation; do not commit it and do not copy full content into B.
- [x] Repair A Agent TOML extension sections: `[project]`, `[moe]`, `[dispatch]`, and `[extensions]`.
- [x] Repair wrapper JSON/safety boundaries: `thesis-moe-on.cmd` and `thesis-moe-off.cmd` now converge to single JSON CLI calls without echo noise, waits, or pauses.
- [x] Repair A `list-sessions` CLI contract and session row stable token, including stable corrupt-state token normalization.
- [x] Commit the A repair branch: `560da0e` (A Phase 1 readiness-contract repair commit; Chinese subject is documented in the zh-CN companion).
- [x] Record A's repaired static-only readiness evidence: `ok=true / static-ready-candidate / ready-candidate / control_mode_allowed=false`.
- [x] Record A's repaired read-contract readiness evidence: `ok=true / token=ok / ready / control_mode_allowed=true`.
- [x] After A readiness outputs `control_mode_allowed=true`, record B's Phase 2 installer dry-run evidence: `ok=true / token=ok / blockers=[] / mode=dry-run`.
- [x] Add A's startup activation hook and rerun readiness against A local `main`.
- [x] After installer dry-run has no blockers, record A's real install receipt and rollback pointer.
- [x] Record write-fixture evidence for project on/off, session on/off, no-op, invalid record skip, lock timeout, and atomic write.
- [x] Only after fresh Ready Lane evidence exists, allow guarded GUI control for that target project; visible GUI launch is now the default no-argument / double-click human operator action once Ready Lane evidence exists; automation remains on `--preflight --json`.

### 14.3 File ownership map

| Path family | Owner | Rule |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan*.md` | This plan change | Bilingual plan source; update as a pair. |
| `openspec/changes/refine-project-moe-gui-plan-comet-structure/` | Current Comet/OpenSpec change | Proposal, design, tasks, management record, delta spec, and archive deferral evidence. |
| `docs/superpowers/specs/*project-moe-gui*` and `docs/superpowers/plans/*project-moe-gui*` | Current Comet/Superpowers change | HOW evidence for this refactor; Chinese pair must be valid UTF-8 if present. |
| `tools/project_moe_gui_toolchain/` | Future implementation slices | Shared checker, installer, updater, launcher templates, PySide6 GUI shell, tests. |
| `<target>/.codex/agents/*.toml`, `<target>/MOE.md`, `<target>/tools/*_moe_mode.py`, `<target>/.omx/state/<namespace>/` | Target project | Target-owned; this repository may inspect or call declared CLI contracts but must not silently own or mutate them. |

### 14.4 Local integration order and evidence retention

The following are standing local-integration rules for every implementation pass, not remaining product features:

- Create a feature branch or feature worktree from current local `main`.
- Keep the primary directory on local `main`; do not turn it into a feature workspace.
- Commit only after precommit update/archive review passes.
- Run local gate and local MR review before local `main` integration.
- Merge to local `main` only after the feature branch is clean and the local-integration authorization boundary is satisfied.
- Keep remote publication separate; do not push GitLab/GitHub unless the current user message explicitly approves remote publication.
- Preserve evidence: command output summary, changed paths, worktree receipt, rollback ref if created, and archive deferral reason if archive cannot run.

### 14.5 Never-skip execution rules

The following are standing execution rules; empty checkboxes are not used to represent them as incomplete implementation work:

- Confirm dirty/ownership preflight before every target-project write.
- Register every new checker in repository guard.
- Archive each completed OpenSpec change; if Comet bash is unavailable, record `x_archive_deferred_reason` and `x_archive_follow_up`.
- Field definitions: `x_archive_deferred_reason` records the stable reason why immediate archive cannot happen in this pass; `x_archive_follow_up` records who continues the archive and under what condition.
- Run precommit update/archive review before every local commit.
- Run local gate and local MR review before every local main merge.
- Treat expert, durable worker, GUI action, or target CLI timeout as missing evidence; only retry, narrow scope, hand off to an eligible durable lane, or record explicit main-session takeover.

## 15. Verification Plan

Feature-branch verification:

```powershell
git diff --check
openspec validate refine-project-moe-gui-plan-comet-structure
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

After commit and before local `main` integration:

```powershell
.\tools\ci\local_gate.ps1
.\tools\ci\local_mr_review.ps1
```

If Comet bash scripts are unavailable, the verification report must say so explicitly and must rely on OpenSpec validation, repository guards, local CI, and local MR review rather than fabricated `comet-state.sh` evidence.

Target-project readiness verification:

- static-only mode must never execute the target CLI.
- no-exec-cli mode must not create side effects in target state.
- read-contract execution mode must check `project-status`, `list-sessions`, `status`, and `assert-on`.
- Historical A/B evidence summary: A repair commit `560da0e`, GUI install/update commits `c6b92ae` and `ce23931`, static readiness `ready-candidate/control_mode_allowed=false`, read-contract readiness `ready/control_mode_allowed=true`, installer dry-run `token=ok`, install check `up_to_date`, launcher preflight `token=ok`, and A target tests `OK`. Long historical command lines are omitted here to keep this active plan below the size gate; see the zh-CN companion and Git history for exact command strings.
- write fixtures cover project on/off, session on/off, manual override retention, invalid-record skip, no-op, lock timeout, and atomic write in `test/project_moe_gui_toolchain.test.py`.
- QFluentWidgets / daemon follow-up verification must cover: QFluentWidgets import or fail-closed blocker, license manifest presence, GUI view-model render smoke, daemon dry-run/no-console launch plan, duplicate lock handling, `--preflight --json` foreground behavior, close-confirmation exit/hide/cancel behavior, tray-unavailable fail-closed handling, and no direct state writes.
- Visual verification must not stop at a default-page smoke screenshot. It must render Project, Sessions, Expert Workbench, Diagnostics, and Settings, and fail closed on missing required text, QML warnings, or visible non-scroll-container overflow.

Human acceptance:

- The document structure is same-level with the newer Pi sidecar plan: goal, architecture, source of truth, contracts, gates, rollback, risks, and self-checks are all present.
- `D:\PythonProject_paper_suggest` is labeled as Ready Lane only with real installed preflight evidence, not as visibly launched or fully manually accepted.
- GUI control is never extended to uninstalled target projects.
- Private prompt full text and raw session ids are not written into this repository's documentation.

## 16. Related Governance / Plan Update Requirements

When implementation moves from docs to code, also update/check:

- `pyside6_cross_project_gui_capability_plan.md`: only the generic PySide6 runtime, shared venv, and GUI packaging/launcher rules belong there; MOE private state logic does not.
- `pi_plugin_codex_user_level_sidecar_plan.md`: only a structure reference; do not import Pi sidecar runtime boundaries.
- OpenSpec stable specs: only promote to stable after implementation and archive are complete.
- Repository guard: new checkers, fixtures, or CI gates must be registered.
- Target-project docs: update only inside target-project adaptation worktrees; do not fake target-project ready state here.

## 17. Risks and Default Decisions

| Risk | Default decision |
| --- | --- |
| Copying A's business Phase 1 into B for convenient validation | Forbidden as substitute evidence for A; B fixtures may only validate checker/installer regressions, not real target-project acceptance |
| Target project has Phase 1 but it is incomplete | Enter Repair Lane; do not allow GUI control |
| Target CLI read commands may have side effects | Use `--static-only` / `--no-exec-cli` first |
| Session ids can only be generated | Treat them as low-confidence and do not use them as hard identity isolation |
| Manual session override conflicts with project default | Session wins; show the conflict in the GUI; do not auto-fix |
| Session lens selection is mistaken for project default | Lens writes are allowed only for the current selected session, and readback must show `lens_selection_scope=session` |
| Empty lens selection is mistaken for disabled | Empty selection always means `effective_lens_mode=all`; disabled is represented only by `enabled=false` |
| Expert Workbench is mistaken for an execution runner | It only generates handoff packages; the GUI does not start a carrier, and the handoff target is text metadata only |
| Manifest hash mismatch | Update/uninstall fail closed |
| Comet bash is unavailable | Record blocker and archive deferral; do not fake success |
| Remote lags behind local `main` | Report remote lag; do not push without approval |

## 18. Self-checklist

- [x] This document uses the full Comet implementation-plan structure.
- [x] `status: active` is preserved and `plan_readiness` is used to separate structure readiness from runtime completion.
- [x] GUI source of truth stays in this repository and target-project state source of truth stays in the target project.
- [x] GUI does not edit JSON directly.
- [x] Ready / Ready-candidate / Bootstrap / Repair lane is explicit.
- [x] State the historical install evidence and current stale source-root blocker for `D:\PythonProject_paper_suggest`, requiring 0.2.23 update before preflight can be claimed current again.
- [x] Private prompt sources are referenced, not copied.
- [x] Install, update, uninstall, and rollback managed-artifact boundaries are explicit.
- [x] Verification commands and local-main / remote-publication boundaries are explicit.
- [x] Comet management record, phase gates, Monitoring return semantics, and evidence retention are explicit.
- [x] Implementation slices, file ownership map, and local integration order are explicit.
- [x] Expert Workbench v2 and session-scoped lens selection are identified as the next incomplete runtime slice, with handoff-only, session-only, and empty-selection=all rules documented.
- [ ] Archive the corresponding OpenSpec change after follow-up code implementation and A/B acceptance are complete.
  - Deferral (2026-06-01): this scaffold `--apply` slice is a local toolchain completion slice. Archive remains deferred until the current local integration package is validated and the operator explicitly chooses the OpenSpec archival scope for the completed Project MOE GUI change set.
- [x] Once real Ready Lane evidence exists for a target project, allow guarded GUI control.

## 19. References

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`: newer executable-plan structure reference.
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md`: Comet management-record, phase-gate, Monitoring-return and evidence-retention semantics.
- `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md`: generic PySide6 runtime and cross-project GUI boundary.
- `openspec/changes/refresh-project-moe-gui-plan-comet/`: previous Project MOE GUI document fact-chain update trace.
- `openspec/changes/restructure-project-moe-gui-plan-modern/`: previous structure-refactor trace.
- `docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.md` and `.zh-CN.md`: static-only readiness evidence for `D:\PythonProject_paper_suggest`.
