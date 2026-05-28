---
doc_id: project_moe_agent_gui_toolchain_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
status: draft
plan_readiness: full-comet-structure-ready-for-implementation-slicing
doc_class: implementation_plan
created_at: 2026-05-20
updated_at: 2026-05-27
last_reviewed_at: 2026-05-27
scope: project_moe_agent_gui_only
implementation_lane: ready_bootstrap_repair_lanes
comet_change: refine-project-moe-gui-plan-comet-structure
related_docs:
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

This document has been refactored from a loose status note plus scattered task list into an executable implementation plan with Comet trace evidence and readiness-lane contracts. It follows the same top-level pattern as `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`, but it does not reuse Pi sidecar runtime boundaries.

| Check | Result | Where it lands |
| --- | --- | --- |
| Comet / OpenSpec trace | complete | Sections 3, 14, 15; `openspec/changes/refine-project-moe-gui-plan-comet-structure/` |
| Goal / non-goal clarity | complete | Section 2 |
| Project MOE / GUI / target-project boundary | complete | Sections 1, 4, 6, 7 |
| Ready / Bootstrap / Repair lane | complete | Section 13 |
| Phase 1 CLI / readiness contract | complete | Section 9 |
| Phase 2 PySide6 GUI contract | complete | Section 10 |
| JSON state model | complete | Section 11 |
| Security, privacy, rollback, uninstall | complete | Section 12 |
| Implementation item granularity | reordered | Section 14 |
| Verification and local/remote boundary | complete | Section 15 |

Status interpretation:

- `status: draft`: this is still an implementation plan, not a completed runtime capability claim.
- `plan_readiness: full-comet-structure-ready-for-implementation-slicing`: the structure, boundaries, and task granularity are ready for code implementation slicing.
- `D:\PythonProject_paper_suggest`: still only a Phase 1 candidate project; the latest recorded static-only evidence is `blocked / repair-lane / control_mode_allowed=false`, so it must not be labeled GUI-ready.
- Current Comet change: `refine-project-moe-gui-plan-comet-structure`. If bash is unavailable, only OpenSpec artifacts, repo-local guards, and local validation can be used as fallback evidence.

## 1. Relationship Model and Naming Boundary

| Name | Role | Source of truth | Boundary |
| --- | --- | --- | --- |
| Project MOE Agent | The target project's own expert-style Agent | `<project>/.codex/agents/*.toml` | Do not install it into user-level agents as a shared Agent |
| Private prompt source | Target-project private constraints, mentor guidance, domain rules | `<project>/MOE.md` or equivalent | Checker validates path/existence only, not full-text copying |
| Phase 1 CLI | Target-project MOE state read/write entrypoint | `<project>/tools/<mode>_moe_mode.py` | GUI must use CLI reads/writes, not direct JSON edits |
| Phase 2 GUI | PySide6 control surface maintained by this repository | `tools/project_moe_gui_toolchain/` | After installation it controls only the installed target project |
| Readiness checker | Read-only gate before install/control | This repository's toolchain | Emits go/no-go and blockers only |
| `.omx/state/<namespace>/` | Target-project MOE state | Target-project repo-local state | No cross-project scanning, no writes to other projects |

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

Non-goals:

- Do not use GUI to bypass the target project's Phase 1 readiness gate.
- Do not copy the target project's private `MOE.md` verbatim.
- Do not default-install project-specific MOE Agents into `C:\Users\lenovo\.codex\agents`.
- Do not build a cross-project master console or default cross-project scanning.
- Do not let the GUI edit `.omx/state` JSON directly.
- Do not treat workflow skills, plugin profiles, or GUI profile loading as native expert evidence.
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

- The initial slice was documentation / plan work; the current continuation includes one bounded runtime slice for guarded uninstall `--apply`.
- This work does not install PySide6, roll out to real target projects, or write user-level directories.
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
| `list-sessions --json` | no | Return a redacted session list |
| `on --session-id <id> --json` | yes | Write a single-session manual enable override |
| `off --session-id <id> --json` | yes | Write a single-session manual disable override |
| `status --json` | no | Compute the effective state for the current or explicit session |
| `assert-on --json` | no | Succeed only when the effective state is on; otherwise return a stable blocker |

Readiness checker requirements:

- Git dirty state: run `git status --porcelain --untracked-files=all` with `GIT_OPTIONAL_LOCKS=0`.
- Agent TOML required fields and standard extension section.
- Private prompt path exists and does not escape the project root.
- CLI read-command envelope, `effective_source`, session counts, list structure, and privacy fields.
- Write-command surface declares `atomic_write`, `lock_status`, `audit_path`, `no_op`, `before`, `after`, `changed_paths`.
- `.cmd` wrapper only forwards controlled commands, forces `--json`, and forbids arbitrary `%*` pass-through or shell chaining.
- Startup / resume / continue / reload / phase-change checkpoints must read `status --json`.

## 10. Phase 2 PySide6 GUI Contract

GUI v1 must include:

- Top project context: target root, branch, agent name, state namespace, readiness lane.
- Project-default card: effective default state, last update time, enable/disable buttons.
- Session table: redacted session id, source, confidence, enabled, effective_enabled, validity, lifecycle status, branch, worktree, first/last seen, reason summary.
- Action panel: refresh, enable project default, disable project default, enable selected session, disable selected session.
- Log panel: actual command invoked, exit code, stable token, and redacted stdout/stderr summary.

GUI behavior rules:

- Refresh calls read-only commands only and never triggers write/migration/install.
- During a write, the same scope buttons are disabled and a loading state is shown.
- After a write completes, the GUI re-reads state.
- An empty session list must not be interpreted as MOE being disabled.
- Error display must include a stable token, a short explanation, and a recommended next action.
- State badges must use both text and color, not color alone.

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

`D:\PythonProject_paper_suggest` is still categorized as a Ready Lane candidate, but the latest static evidence is still blocked / Repair Lane; only a readiness checker that explicitly outputs ready may unlock real GUI installation and control.

## 14. Implementation Items (ordered, fine-grained)

### 14.1 Already completed or already present

- [x] Define the boundary between Project MOE GUI and the generic PySide6 capability plan.
- [x] Define the GUI source of truth in this repository and the target-project state source of truth in the target project.
- [x] Define the target install artifact and managed-manifest model.
- [x] Define that the GUI never edits state JSON directly.
- [x] Define the Ready / Ready-candidate / Bootstrap / Repair lane model.
- [x] Define that `D:\PythonProject_paper_suggest` cannot jump into GUI control just because a Phase 1 candidate exists.
- [x] Define that missing Comet bash scripts must not be faked.
- [x] Recast this document into the new Comet executable-plan structure.
- [x] Add Comet management-record, phase-gate, Monitoring-return, evidence-retention, and approval-boundary semantics to this plan.

### 14.2 Implementation slices

#### Slice 0: plan and OpenSpec evidence closure

- [x] Reuse the existing OpenSpec change `refine-project-moe-gui-plan-comet-structure`; do not open an unrelated duplicate change.
- [x] Keep `status: draft` and use `plan_readiness` for implementation-slicing readiness, not runtime completion.
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
- [ ] Ensure readiness output includes lane, blockers, warnings, checked files, redacted paths, and `control_mode_allowed`.
- Current slice (2026-05-28): `harden-moe-readiness-output-contract-20260528` is adding explicit `warnings`, `checked_files`, and `redacted_paths` evidence fields before this item is checked.
- Evidence (2026-05-28): the current schema-hardening OpenSpec change adds a stable fail-closed blocker for unsupported CLI envelope schema; its regression test proves readiness remains blocked; existing fixture coverage still proves the ready, ready-candidate, bootstrap, repair, static-only, and read-contract command boundaries.

#### Slice 2: Bootstrap and repair lane tooling

- [ ] Freeze `scaffold_project_moe_phase1.py --dry-run --json` output.
- [ ] Generate bootstrap actions without writing target files by default.
- [ ] Add an explicit `--apply` path only after target ownership and dirty-state checks pass.
- [ ] Produce a repair-lane report for partially implemented Phase 1 projects.
- [ ] Preserve `D:\PythonProject_paper_suggest` as repair-lane until fresh checker evidence proves otherwise.

#### Slice 3: target install, update, uninstall, and rollback manifest

- [ ] Implement install artifact generation under `<project>/tools/project_moe_gui/`.
- [ ] Generate `<project>/project-moe-gui.cmd` as a narrow launcher, not an arbitrary command passthrough.
- [ ] Write `project_moe_gui.install-manifest.json` with source commit, managed files, hashes, target root, agent name, namespace, readiness result, and rollback pointer.
- [ ] Implement update by comparing manifest hashes and source version.
- [x] Implement uninstall by deleting only manifest-owned managed files.
- [x] Create local uninstall receipts before deleting any managed target artifact and keep rollback hints in the JSON payload.

#### Slice 4: Phase 2 PySide6 GUI shell

- [ ] Build the launcher preflight: target root selection, readiness check, read-contract check, and fail-closed blocker display.
- [ ] Implement the project-default status card.
- [ ] Implement the session table with desensitized session identifiers and lifecycle fields.
- [ ] Implement project default on/off actions through target CLI only.
- [ ] Implement selected-session on/off actions through target CLI only.
- [ ] Disable same-scope write controls during writes and refresh state after every write.
- [ ] Display stable failure tokens, concise explanations, suggested next actions, and redacted stdout/stderr summaries.

#### Slice 5: governance, docs, and checker integration

- [ ] Register any new checker in the repository guard and CI manifest.
- [ ] Update the PySide6 cross-project capability plan only for shared runtime and launcher boundary changes.
- [ ] Update Project MOE-specific docs only for MOE GUI state, readiness, and installer behavior.
- [ ] Keep workflow skills, plugin profiles, and GUI profile loading out of native-expert evidence claims.
- [ ] Keep private prompt source content referenced, not copied.

#### Slice 6: target-project acceptance and rollout

- [ ] Record static-only evidence for the target project.
- [ ] Record read-contract evidence for the target project.
- [ ] Record write-fixture evidence for project on/off, session on/off, no-op, invalid record skip, lock timeout, and atomic write.
- [ ] Only after fresh Ready Lane evidence exists, allow GUI control for that target project.
- [ ] Record the target install receipt and rollback pointer.

### 14.3 File ownership map

| Path family | Owner | Rule |
| --- | --- | --- |
| `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan*.md` | This plan change | Bilingual plan source; update as a pair. |
| `openspec/changes/refine-project-moe-gui-plan-comet-structure/` | Current Comet/OpenSpec change | Proposal, design, tasks, management record, delta spec, and archive deferral evidence. |
| `docs/superpowers/specs/*project-moe-gui*` and `docs/superpowers/plans/*project-moe-gui*` | Current Comet/Superpowers change | HOW evidence for this refactor; Chinese pair must be valid UTF-8 if present. |
| `tools/project_moe_gui_toolchain/` | Future implementation slices | Shared checker, installer, updater, launcher templates, PySide6 GUI shell, tests. |
| `<target>/.codex/agents/*.toml`, `<target>/MOE.md`, `<target>/tools/*_moe_mode.py`, `<target>/.omx/state/<namespace>/` | Target project | Target-owned; this repository may inspect or call declared CLI contracts but must not silently own or mutate them. |

### 14.4 Local integration order and evidence retention

- [ ] Start implementation from a feature branch or feature worktree based on current local `main`.
- [ ] Keep the primary worktree on local `main`; do not turn it into a feature workspace.
- [ ] Commit only after the precommit update/archive review passes.
- [ ] Run local gate and local MR review before local `main` integration.
- [ ] Merge into local `main` only after the feature branch is clean and user approval for local integration is present.
- [ ] Keep remote publication separate; do not push GitLab/GitHub unless the current user message explicitly approves remote publication.
- [ ] Retain evidence: command output summaries, changed paths, worktree receipt, rollback ref if created, and archive deferral reason if archive cannot run.

### 14.5 Never-skip execution rules

- [ ] Before every target-project write, confirm dirty/ownership preflight.
- [ ] Whenever a new checker is added, register it in the repo guard.
- [ ] After every completed OpenSpec change, archive it; if Comet bash is unavailable, record `x_archive_deferred_reason` and `x_archive_follow_up`.
- [ ] Before every local commit, run the precommit update/archive review.
- [ ] Before every local `main` integration, run the local gate and local MR review.
- [ ] If an expert, durable worker, GUI action, or target CLI times out, treat the result as missing evidence; retry, narrow, hand off, or record explicit main-session takeover.

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
- write fixtures must cover project on/off, session on/off, manual override retention, invalid-record skip, no-op, lock timeout, and atomic write.

Human acceptance:

- The document structure is same-level with the newer Pi sidecar plan: goal, architecture, source of truth, contracts, gates, rollback, risks, and self-checks are all present.
- `D:\PythonProject_paper_suggest` is not mislabeled as ready.
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
| Target project has Phase 1 but it is incomplete | Enter Repair Lane; do not allow GUI control |
| Target CLI read commands may have side effects | Use `--static-only` / `--no-exec-cli` first |
| Session ids can only be generated | Treat them as low-confidence and do not use them as hard identity isolation |
| Manual session override conflicts with project default | Session wins; show the conflict in the GUI; do not auto-fix |
| Manifest hash mismatch | Update/uninstall fail closed |
| Comet bash is unavailable | Record blocker and archive deferral; do not fake success |
| Remote lags behind local `main` | Report remote lag; do not push without approval |

## 18. Self-checklist

- [x] This document uses the full Comet implementation-plan structure.
- [x] `status: draft` is preserved and `plan_readiness` is used to separate structure readiness from runtime completion.
- [x] GUI source of truth stays in this repository and target-project state source of truth stays in the target project.
- [x] GUI does not edit JSON directly.
- [x] Ready / Ready-candidate / Bootstrap / Repair lane is explicit.
- [x] `D:\PythonProject_paper_suggest` is still not GUI ready.
- [x] Private prompt sources are referenced, not copied.
- [x] Install, update, uninstall, and rollback managed-artifact boundaries are explicit.
- [x] Verification commands and local-main / remote-publication boundaries are explicit.
- [x] Comet management record, phase gates, Monitoring return semantics, and evidence retention are explicit.
- [x] Implementation slices, file ownership map, and local integration order are explicit.
- [ ] Once the code implementation is complete, archive the corresponding OpenSpec change.
- [ ] Once real Ready Lane evidence exists for a target project, allow GUI control.

## 19. References

- `docs_bilingual/implementation_plans/pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`: newer executable-plan structure reference.
- `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md`: Comet management-record, phase-gate, Monitoring-return and evidence-retention semantics.
- `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md`: generic PySide6 runtime and cross-project GUI boundary.
- `openspec/changes/refresh-project-moe-gui-plan-comet/`: previous Project MOE GUI document fact-chain update trace.
- `openspec/changes/restructure-project-moe-gui-plan-modern/`: previous structure-refactor trace.
- `docs_bilingual/memory/project_moe_paper_suggest_static_readiness_evidence_2026-05-24.md` and `.zh-CN.md`: static-only readiness evidence for `D:\PythonProject_paper_suggest`.
