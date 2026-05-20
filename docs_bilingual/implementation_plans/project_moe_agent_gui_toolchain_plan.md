---
doc_id: project_moe_agent_gui_toolchain_plan
lang: en
canonical: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
status: draft
doc_class: implementation_plan
created_at: 2026-05-20
related_docs:
  - docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md
---

# Project MOE Agent GUI Toolchain Plan

> Cold-start contract: this plan defines a repo-local MOE Agent control pattern and a dedicated PySide6 GUI toolchain. The GUI source is maintained in `D:\PythonProject_langgraph`, but installed launchers control only the target project where they are installed.

## 1. Goal

Create a repeatable way for each local project to define and control its own MOE AI Agent without mixing project-private agent state, prompt sources, or GUI tooling across repositories.

The immediate project is `D:\PythonProject_paper_suggest`, which needs a strict thesis-quality mentor MOE Agent controlled by `thesis-moe-on.cmd` and `thesis-moe-off.cmd`. Later projects should be able to add their own MOE Agents with the same structure.

## 2. Relationship to the PySide6 capability plan

`pyside6_cross_project_gui_capability_plan.md` defines general PySide6 availability for local projects. This file is narrower:

- it only covers MOE Agent control surfaces;
- it owns a dedicated `project_moe_gui` toolchain namespace;
- it must not be merged into generic GUI tooling;
- it defines how an installed GUI maps to the target project's sessions.

If the two plans conflict, use this plan for MOE Agent control behavior and use the PySide6 capability plan for general PySide6 setup guidance.

## 3. Non-goals

This plan does not:

- implement the GUI immediately;
- copy project-private `MOE.md` content into user-level configuration;
- install project-specific MOE Agents into `C:\Users\lenovo\.codex\agents` by default;
- create a cross-project MOE control dashboard in the first GUI version;
- allow a GUI installed in one project to read or write another project's `.omx/state`;
- treat workflow skills, plugin profiles, or GUI profile loading as native expert evidence.

## 4. Standard project MOE Agent TOML

Each project MOE Agent should live in the target repository:

```text
<project>/.codex/agents/<project-moe-agent>.toml
```

The TOML uses a fixed core plus extension sections.

Required top-level fields:

```toml
name = "project-moe-agent-name"
description = "Short human-readable description."
developer_instructions = """
Project-local MOE instructions.
"""
```

Recommended standard sections:

```toml
[project]
scope = "repo-local"
state_namespace = "project_moe"
private_prompt_source = "MOE.md"
private_prompt_policy = "do-not-copy-full-content"

[moe]
kind = "project-moe-agent"
family = "project-specific"
requires_manual_enable = true
project_default_state = ".omx/state/project_moe/project-default.json"
session_state_dir = ".omx/state/project_moe/sessions"

[dispatch]
mode = "brief-based"
forbidden = ["full-history-fork-with-custom-role"]
fallback = ["main-session-takeover", "durable-brief"]

[extensions]
# Project-specific keys are allowed here.
```

The checker may start with the existing `name`, `description`, and `developer_instructions` requirement, then later enforce these standard sections for projects that opt in to the MOE GUI toolchain.

## 5. Dispatch policy

Project MOE Agents must not be launched with the incompatible combination:

```text
full-history fork + specified custom role
```

Use one of these compatible patterns instead:

1. main-session takeover: the leader session reads the repo-local TOML and executes the MOE review directly;
2. brief-based fresh dispatch: the leader creates a minimal task brief and sends only that brief to a fresh compatible expert surface;
3. durable brief: a LangGraph or native_omx lane consumes a frozen brief stored under the target project's `.omx/state`.

A timeout, stalled expert, or failed full-history fork is not evidence. The session must either retry with a compatible brief, switch to a durable brief, or explicitly record main-session takeover.

## 6. Phase 1: urgent command-line control for `paper_suggest`

The urgent implementation extends the existing `D:\PythonProject_paper_suggest` thesis MOE controls.

Target behavior:

- `thesis-moe-on.cmd` enables the MOE Agent for the project default, all registered existing sessions, and later new sessions.
- `thesis-moe-off.cmd` disables the MOE Agent for the project default, all registered existing sessions, and later new sessions.
- CLI still supports single-session overrides through `--session-id`.
- Project-wide `.cmd` actions intentionally overwrite registered session states; the later GUI can set individual sessions again.

State layout:

```text
.omx/state/thesis_moe/project-default.json
.omx/state/thesis_moe/sessions/<session-id>.json
```

Registered existing sessions are the JSON records already present under `sessions/`. Sessions that have never written a record cannot be discovered automatically and inherit the project default when they first call `status` or `assert-on`.

Effective status rule:

1. if a valid session record exists, use that session record;
2. otherwise use the valid project default;
3. otherwise fail closed as disabled.

Recommended CLI surface:

```powershell
python .\tools\thesis_moe_mode.py project-on
python .\tools\thesis_moe_mode.py project-off
python .\tools\thesis_moe_mode.py project-status --json
python .\tools\thesis_moe_mode.py on --session-id <id>
python .\tools\thesis_moe_mode.py off --session-id <id>
python .\tools\thesis_moe_mode.py status --json
python .\tools\thesis_moe_mode.py assert-on
```

Backward compatibility:

- existing `status --json` remains machine-readable;
- existing session state files remain readable;
- corrupted, mismatched, or out-of-scope state fails closed.

Phase 1 implementation sequence:

1. extend `tools/thesis_moe_mode.py` with project-default state read/write helpers;
2. add `project-on`, `project-off`, and `project-status` commands;
3. make `status` and `assert-on` compute effective state from session override, then project default, then fail-closed disabled;
4. update `thesis-moe-on.cmd` and `thesis-moe-off.cmd` to call project-level commands by default;
5. add or update usage documentation and tests for project default, registered-session propagation, and single-session override behavior.

Phase 1 must not change paper content, private prompt content, browser automation, or literature-search behavior.

## 7. Phase 2: dedicated PySide6 project MOE GUI

The GUI source is maintained in this repository, but it is isolated from other GUI work.

Source-of-truth layout in `D:\PythonProject_langgraph`:

```text
tools/project_moe_gui_toolchain/
  src/project_moe_gui/
  install_project_moe_gui.py
  update_project_moe_gui.py
  check_project_moe_gui_install.py
  templates/
```

Target project install layout:

```text
<project>/tools/project_moe_gui/
  launcher.py
  project_moe_gui.config.json
<project>/project-moe-gui.cmd
```

Isolation rules:

- do not place MOE GUI source under generic `tools/gui` directories;
- do not reuse state directories from other GUI tools;
- do not import project-private `MOE.md` into the central toolchain;
- do not make a cross-project scan the default behavior;
- the installed GUI controls only the project root resolved from its launcher path or from an explicit `--project-root`.

First GUI version:

- shows project default status;
- lists registered session records;
- toggles project default on/off;
- toggles a selected session on/off;
- calls the same project-local CLI script used by `.cmd` files;
- displays the resolved project root and state namespace so accidental cross-project control is visible.

Installed GUI config:

```json
{
  "schema_version": 1,
  "toolchain": "project_moe_gui",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "mode_cli": "tools/thesis_moe_mode.py",
  "project_root_strategy": "launcher-parent-git-root",
  "pyside6_runtime": "project-or-shared-runtime"
}
```

The GUI must treat this config as target-project configuration. It must not read central toolchain state to decide target sessions.

## 8. Install and update model

`D:\PythonProject_langgraph` is the source of truth for the GUI toolchain. Target projects receive install artifacts only.

Install/update rules:

- installing to `<project>` writes only under that project root;
- updates may refresh launcher, config template, and GUI wrapper files;
- updates must not overwrite project-private `MOE.md`, `.codex/agents/*.toml`, or existing `.omx/state` records;
- updates must be idempotent and report changed files;
- rollback uses normal project Git history plus local backup refs when the target project workflow requires them.

PySide6 runtime can be supplied by either a documented shared GUI runtime or the target project's own virtual environment. The first implementation must record which runtime is used in the installed config and must fail with an actionable message if PySide6 is unavailable.

## 9. Safety and rollback rules

Implementation and update commands must:

- print the resolved target project root before writing;
- refuse to write outside the target project root;
- refuse to overwrite `MOE.md`, `.codex/agents/*.toml`, or `.omx/state` unless a later explicit repair command is created;
- create normal Git-reviewable changes in the target project;
- preserve enough status output for the user to see whether a project default or a session override was changed.

If an update fails halfway, rerunning the installer or updater must be safe. For project state changes, rollback is the target project's Git history plus the state JSON files under `.omx/state`.

## 10. Validation and acceptance

Document-level acceptance for this plan:

- English and Chinese plan files exist as a pair;
- the plan clearly separates the MOE GUI toolchain from generic GUI tooling;
- the plan defines project default plus session override behavior;
- the plan forbids `full-history fork + specified custom role` for project MOE Agents.

Phase 1 acceptance:

- `thesis-moe-on.cmd` enables project default and registered sessions;
- `thesis-moe-off.cmd` disables project default and registered sessions;
- new sessions inherit project default;
- explicit `--session-id` overrides work;
- `assert-on` follows the effective status rule.

Phase 2 acceptance:

- installing the GUI into `paper_suggest` controls only `paper_suggest`;
- installing into a second project controls only that second project;
- no target project's private agent TOML, `MOE.md`, or state is overwritten by GUI update;
- GUI actions and CLI status agree.

## 11. Immediate next implementation boundary

After this plan is accepted, implementation should proceed in this order:

1. implement and test Phase 1 in `D:\PythonProject_paper_suggest`;
2. update this repository with reusable project MOE TOML/checker expectations if Phase 1 exposes a reusable contract gap;
3. implement the dedicated `project_moe_gui` toolchain in this repository;
4. install the GUI into `paper_suggest` as the first target project;
5. only after the first target is stable, generalize the installer for additional projects.

Do not start the PySide6 GUI before the command-line state model is stable.
