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

## 0. Current status and review conclusion

Review date: 2026-05-23.

Conclusion: the original plan already covered the architectural boundary, state model, safety rules, and phase gates, but it lacked an item-level implementation checklist. That made it hard for later sessions to distinguish implemented work from plan-only intent. This revision adds the item-level progress checklist in section 11 and updates section 13 to reflect current implementation facts.

Status note: this document remains `status: draft`. Draft here means it is not a global active governance policy and does not claim that the whole runtime is complete. Phase 2A central installer/checker/updater, the Phase 2B fixture-safe GUI shell, and the Phase 2C dual-fixture install/check/update/status isolation evidence are confirmed on local `main`; this follow-up adds the Phase 1 CLI read-contract fixture gate, the GUI write-command output-contract fixture gate, and the write-command `atomic_write` / `lock_status` fail-closed fixture gate. The real target-project Phase 1 CLI state model is still open, so the document remains `draft`.

Current known local facts:

- Phase 2A is merged into this repository's local `main`: `3e4e819c73c78472d948e68d5352085dcac6551d` (`实现项目 MOE GUI 第二阶段安装器`).
- Phase 2B is merged into this repository's local `main`: `47187a7da4b167341cf0a8fc01db415db601fe92`.
- This follow-up adds Phase 1 CLI read-contract fixture support: installer/checker preflight now validates the shared envelope, `effective_source`, session counts, list structure, and private-field redaction for `project-status`, `list-sessions`, and `status`, so the GUI cannot be installed against an incomplete target CLI.
- This follow-up also adds GUI write-command output-contract fixture support: after `project-on`, `project-off`, `session-on`, or `session-off`, the GUI now requires `before`, `after`, `changed_scope`, `changed_paths`, `skipped_invalid_records`, `lock_status`, `audit_path`, `atomic_write`, `no_op`, scope agreement, atomic-write declaration, safe lock state, and private-field redaction before accepting the result.
- These facts only mean repository fixture and contract-gate evidence exists; they do not mean `D:\PythonProject_paper_suggest` has completed Phase 1, and they do not mean a real target-project GUI is ready for operation.
- Without explicit remote-publication approval, GitLab/GitHub are outside this plan's automatic execution scope.

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

Project onboarding and template-generation boundary:

- new project onboarding defaults to "validate an existing Agent TOML, then install the GUI"; the installer must not auto-generate `.codex/agents/*.toml` in default mode;
- if template generation is added later, it must be an explicit command such as `scaffold-project-moe-agent --target-project <project> --agent-name <agent> --state-namespace <namespace> --dry-run --json`, and it defaults to dry run;
- template generation may create only a skeleton TOML, an empty project-private prompt-source placeholder note, and operator documentation; it must not invent long `developer_instructions` content and must not copy another project's `MOE.md`;
- `agent_name` must be cross-checked against top-level TOML `name`, installed config, manifest, and state namespace; name conflicts or namespace reuse by another agent fail closed;
- `state_namespace` must be project-unique and safe as a directory name; it must not contain path separators, whitespace control characters, or shell-special semantics;
- onboarding checkers must validate required top-level fields, recommended sections, private prompt source path, dispatch policy, scope, state paths, and schema version; failures return stable tokens and remediation hints;
- target projects may maintain their own private `MOE.md`, but scaffold/install/update must not read its full content to generate user-level configuration or central toolchain cache.

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

Minimum project-default JSON contract:

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "project-default",
  "enabled": true,
  "worktree": "D:\\PythonProject_paper_suggest",
  "branch": "main",
  "updated_at": "2026-05-20T00:00:00+00:00",
  "reason": "project-on"
}
```

Minimum session JSON contract:

```json
{
  "schema_version": 1,
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "scope": "session",
  "enabled": true,
  "session_id": "session-id",
  "session_id_source": "argument",
  "override_origin": "manual-session",
  "raw_session_id_sha256": "sha256",
  "worktree": "D:\\PythonProject_paper_suggest",
  "branch": "main",
  "first_seen_at": "2026-05-20T00:00:00+00:00",
  "last_seen_at": "2026-05-20T00:00:00+00:00",
  "updated_at": "2026-05-20T00:00:00+00:00",
  "reason": "manual-session-on"
}
```

Registered existing sessions are the JSON records already present under `sessions/`. Sessions that have never written a record cannot be discovered automatically and inherit the project default when they first call `status` or `assert-on`.

Effective status rule:

1. if a valid session record exists, use that session record;
2. otherwise use the valid project default;
3. otherwise fail closed as disabled.

Session identity rule:

- `--session-id` is the strongest identity source and is required for exact control of a known session from scripts or GUI.
- Runtime environment variables such as `THESIS_MOE_SESSION_ID`, `CODEX_SESSION_ID`, `OPENAI_CODEX_SESSION_ID`, `OH_MY_CODEX_SESSION_ID`, `OMX_SESSION_ID`, and `CODEX_SESSION` are accepted when present.
- If no stable session id exists, the CLI may generate a project-local compatibility id from worktree, branch, and user. This generated id is sufficient for a single local workflow but is not a hard isolation boundary for multiple simultaneous sessions in the same worktree and branch.
- The GUI must display the `session_id_source` so the user can distinguish real session ids from generated compatibility ids.

Session lifecycle and stale-record rules:

- `status --json` or `assert-on` may best-effort update `last_seen_at` when the current session id can be identified; that update must not change `enabled`;
- the first session record creation writes `first_seen_at`, and ordinary on/off operations must not overwrite it later;
- `list-sessions --json` must derive `lifecycle_status` with at least `active`, `stale`, `invalid`, and `orphan_candidate`; this field is for display and filtering only and does not directly change effective state;
- `stale` means `last_seen_at` exceeds a configured threshold or the session cannot be confirmed as still active; first version marks only and never auto-deletes or auto-disables;
- `orphan_candidate` means the record's worktree, branch, or session source can no longer be confirmed; it appears in a GUI invalid/needs-review group and must not be silently repaired by project-level on/off;
- the first version does not implement automatic pruning, archive, tombstone, or session-state cleanup; if needed later, add explicit commands such as `prune-sessions --dry-run` / `--apply`, audit records, and rollback rules;
- records created from generated compatibility ids must be shown as lower confidence in the GUI so the operator does not confuse them with strongly isolated real sessions.

Recommended CLI surface:

```powershell
python .\tools\thesis_moe_mode.py project-on
python .\tools\thesis_moe_mode.py project-off
python .\tools\thesis_moe_mode.py project-status --json
python .\tools\thesis_moe_mode.py list-sessions --json
python .\tools\thesis_moe_mode.py on --session-id <id>
python .\tools\thesis_moe_mode.py off --session-id <id>
python .\tools\thesis_moe_mode.py status --json
python .\tools\thesis_moe_mode.py assert-on
```

Command semantics:

| Command | Writes | Effect |
| --- | --- | --- |
| `project-on` | project default and registered valid session files | Enables default and known sessions. |
| `project-off` | project default and registered valid session files | Disables default and known sessions. |
| `project-status --json` | none | Reports project default, registered session counts, invalid records, and state paths. |
| `list-sessions --json` | none | Lists registered session records for GUI and diagnostics. |
| `on --session-id <id>` | one session file | Enables that session override. |
| `off --session-id <id>` | one session file | Disables that session override. |
| `status --json` | none | Reports effective state for current or explicit session. |
| `assert-on` | none | Exits zero only when effective state is enabled. |

Invalid registered session files must not block project-level on/off. They should be reported as skipped invalid records and left untouched.

Project-level propagation and manual session override rules:

- `project-on` / `project-off` update the project default and propagate only to valid session records whose `override_origin = "project-propagated"` or that have no explicit manual origin;
- `on --session-id <id>` / `off --session-id <id>` write `override_origin = "manual-session"` to mark an operator-explicit session setting;
- project-level commands must not silently overwrite records with `override_origin = "manual-session"`; if bulk override is needed later, add an explicit option such as `--include-manual-overrides` and list affected sessions in dry-run and JSON output;
- when a session record exists only because of project-level propagation, the GUI should display "follows project default propagation" so users do not confuse it with a manual exception;
- if project default conflicts with a manual session override, `effective_source = "session"` and `status --json` / GUI displays the conflict hint without auto-repairing it;
- clearing manual overrides is not required for Phase 1; if `clear-session-override` is later added, it must return to inheriting project default and must not delete audit history.

`list-sessions --json` should return only redacted identifiers and metadata needed for control: session id, source, enabled flag, validity, lifecycle status, status reason, branch, worktree, first seen, last seen, timestamps, reason, and state path. It must not expose raw session id values beyond the normalized stored session id, and it must not include private prompt content.

State compatibility and migration:

- existing `thesis_moe_mode.py` session records that do not yet contain `scope` or `state_namespace` must remain readable when their existing required fields are valid;
- when a project-level command rewrites a valid legacy session record, it should add `scope = "session"` and `state_namespace = "thesis_moe"`;
- project-level commands must preserve `created_at` when it already exists and update `updated_at` and `reason`;
- invalid or corrupt legacy records are never auto-repaired during normal on/off operations; they require a later explicit repair command if repair is needed.

Failure-mode and exit-code contract:

| Case | Exit code | Stable token |
| --- | ---: | --- |
| successful read or write | 0 | `ok` |
| `assert-on` sees effective disabled state | 1 | `disabled` |
| invalid command arguments or unsupported command | 2 | `usage_error` |
| corrupt or mismatched state blocks effective-state calculation | 3 | `state_corrupt`, `schema_version_mismatch`, `blocked:unsupported_schema_version`, `agent_name_mismatch`, `session_mismatch`, `worktree_mismatch`, `branch_mismatch` |
| unsafe target root, path, command invocation, or ownership preflight refusal | 4 | `blocked:unsafe_target_root`, `blocked:path_outside_project`, `blocked:path_traversal`, `blocked:unsafe_symlink_or_junction`, `blocked:command_invocation_unsafe`, `blocked:ownership_precheck_failed`, `blocked:dirty_unowned_files` |
| missing dependency, invalid launcher config, or missing required project file | 5 | `blocked:missing_agent_toml`, `blocked:missing_mode_cli`, `blocked:pyside6_unavailable`, `blocked:python_runtime_unavailable`, `blocked:launcher_config_invalid` |
| concurrent write lock cannot be acquired, or a suspected stale lock needs human confirmation | 6 | `blocked:state_lock_timeout`, `blocked:stale_state_lock` |

CLI and GUI outputs should include both a human-readable message and a stable machine-readable token. GUI code should branch on tokens, not localized prose.

CLI JSON output contract:

- every `--json` command returns a shared envelope: `schema_version`, `command`, `ok`, `token`, `exit_code`, `message`, `project_root`, `agent_name`, `state_namespace`, `generated_at`, `warnings`, and `errors`;
- `status --json` additionally returns `effective_enabled`, `effective_source` (`session`, `project-default`, `fail-closed`), `session_id`, `session_id_source`, `session_confidence`, `lifecycle_status`, `project_default_enabled`, `session_override_enabled`, and `state_path`;
- `project-status --json` additionally returns `project_default`, `registered_session_count`, `valid_session_count`, `invalid_session_count`, `stale_session_count`, `orphan_candidate_count`, `state_paths`, and `cli_contract`;
- `list-sessions --json` returns a `sessions` array, `counts`, `redaction_policy`, and `source_paths`; each session row may include only redacted session id, source, confidence, enabled flag, effective enabled flag, validity, lifecycle status, status reason, branch, worktree, first seen, last seen, updated at, reason summary, and state path;
- JSON output for write commands must include `before`, `after`, `changed_scope`, `changed_paths`, `skipped_invalid_records`, `lock_status`, `audit_path`, `atomic_write`, and `no_op`;
- failure JSON must include stable `token`, `remediation_hint`, and optional redacted `details`; it must not embed private prompt text, raw session ids, paper text, raw environment variable values, or full stderr output.

Backward compatibility:

- existing `status --json` remains machine-readable;
- existing session state files remain readable;
- corrupted, mismatched, or out-of-scope state fails closed.

Session activation and auto-effect rules:

- `project-on` / `project-off` only write project and session state; by themselves they cannot instantly mutate the model context of already-open Codex sessions across processes, so they must be paired with a target-project startup/resume check surface;
- Phase 1 for `paper_suggest` must add a short rule to the target project's `AGENTS.md`, equivalent startup summary, or launcher helper: on first substantive task, `resume` / `continue`, reload / restart, phase change, or an explicit user question about MOE state, read `python .\tools\thesis_moe_mode.py status --json`, and use `assert-on` only when a hard enabled assertion is required;
- new sessions inherit the project default at startup; already-open sessions re-read effective state at the next activation checkpoint above; the plan must not claim that `.cmd` files can instantly inject state into an already-open session's history;
- when the effective state is enabled, the session applies strict mentor review using `.codex/agents/thesis-moe-mentor.toml` and the summary/reference policy for the project-private `MOE.md`; when disabled or fail-closed, it must not load the private prompt text in full;
- if the activation hook is missing, the CLI is missing, or the CLI returns a blocker token, the session must report a named blocker such as `blocked:missing_moe_activation_hook` or `blocked:missing_mode_cli` instead of silently treating MOE as enabled;
- GUI state must come from the same `status` / `project-status` / `list-sessions` JSON contract and must not maintain a second state source.

Phase 1 implementation sequence:

1. extend `tools/thesis_moe_mode.py` with project-default state read/write helpers;
2. add `project-on`, `project-off`, and `project-status` commands;
3. make `status` and `assert-on` compute effective state from session override, then project default, then fail-closed disabled;
4. update `thesis-moe-on.cmd` and `thesis-moe-off.cmd` to call project-level commands by default;
5. update the target project's `AGENTS.md`, startup summary, or launcher helper so new and already-open sessions re-read MOE state at activation checkpoints;
6. add or update usage documentation and tests for project default, registered-session propagation, single-session override behavior, and the session auto-effect chain.

Phase 1 must not change paper content, private prompt content, browser automation, or literature-search behavior.

Target-project preflight before Phase 1 writes:

- run `git status --short --branch` in `D:\PythonProject_paper_suggest` and stop if unrelated dirty or untracked files would be touched;
- run the target project's ownership precheck when available, for example `python .\tools\check_session_ownership_claims.py --root . --precheck-task "thesis MOE project-default session toggle" --target-path tools/thesis_moe_mode.py --json`;
- confirm the existing `.codex/agents/thesis-moe-mentor.toml`, `tools/thesis_moe_mode.py`, `thesis-moe-on.cmd`, `thesis-moe-off.cmd`, and usage document are present before editing;
- create a normal local Git commit in the target project after tests pass; do not push or publish that target-project change without a separate remote-publication request.

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
  project_moe_gui.install-manifest.json
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

First GUI layout:

- top banner: resolved project root, agent name, state namespace, and current branch;
- project-default card: effective default state, last update time, and on/off buttons;
- session table: session id, source, effective state, override state, branch, updated time, reason, and validity;
- action panel: refresh, enable selected session, disable selected session, clear selected session override if a later CLI command supports it;
- log panel: exact CLI command invoked, exit code, and short stdout/stderr summary.

The GUI must never edit JSON files directly in the first version. All state changes go through the project-local CLI so CLI and GUI behavior cannot drift.
The GUI session table should be populated through `list-sessions --json`; if that command is unavailable, the GUI must fail with an actionable message instead of scanning `.omx/state` directly in v1.

First GUI interaction and accessibility rules:

- every status badge must express state with both text and color, for example `Project default: enabled`, `Session override: disabled`, and `Invalid record`; never rely on red/green color alone;
- on/off buttons must name their scope clearly: `Enable project default`, `Disable project default`, `Enable selected session`, and `Disable selected session`;
- refresh only reads `project-status --json` and `list-sessions --json`; it must not trigger writes, migrations, or installs;
- while a write command is running, buttons for the same scope are disabled and a loading state is shown; after completion, the GUI rereads state instead of trusting a local predicted value;
- errors show the stable token, a short explanation, and an actionable next step; stdout/stderr summaries remain copyable but must not expose private content;
- the session table must support empty state, invalid-record state, and load-failed state; empty state must not be confused with "MOE is disabled";
- the table supports at least updated-time sorting and validity filtering; sorting/filtering operates only on already-returned redacted rows and never rescans `.omx/state`;
- keyboard operation is required for refresh, project-default toggles, selected-session toggles, and copying error summaries; default focus must not land on dangerous write buttons;
- high-contrast or system theme must still make status, disabled buttons, and error banners distinguishable;
- localized GUI text is never a machine decision surface; code branches only on CLI JSON fields and stable tokens.

Installed GUI config:

```json
{
  "schema_version": 1,
  "toolchain": "project_moe_gui",
  "toolchain_version": "0.1.0",
  "cli_contract": "project-moe-cli-v1",
  "agent_name": "thesis-moe-mentor",
  "state_namespace": "thesis_moe",
  "mode_cli": "tools/thesis_moe_mode.py",
  "project_root_strategy": "launcher-parent-git-root",
  "pyside6_runtime": "project-or-shared-runtime",
  "python_runtime_strategy": "project-venv-then-shared-gui-runtime",
  "python_utf8": true
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

Installer command surface:

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py --target-project <project> --agent-name <agent> --state-namespace <namespace>
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project <project>
python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project <project> --json
```

Installers and updaters should support `--dry-run --json`. Dry run only computes the resolved target project root, files that would be written or updated, private files that would be skipped, required migration actions, and rollback hints. It must not write files. Real writes must clearly report `mode = "apply"`; when nothing changes, output `no_op = true` and do not rewrite files just to create a commit.

The installer must fail if the target project has no matching `.codex/agents/<agent>.toml` unless an explicit template-generation mode is added later.

PySide6 runtime can be supplied by either a documented shared GUI runtime or the target project's own virtual environment. The first implementation must record which runtime is used in the installed config and must fail with an actionable message if PySide6 is unavailable.

### 8.1 Versioning, compatibility, and upgrade policy

`schema_version = 1` is the first supported target-project config and state contract. `toolchain_version` identifies the GUI toolchain version or release marker maintained by this repository, and `cli_contract` identifies the stable command contract expected from the installed target-project CLI. Install, update, and check commands must report at least these JSON fields: `installed_toolchain_version`, `target_toolchain_version`, `config_schema_version`, `cli_contract`, `migration_actions`, and `rollback_hint`.

Compatibility policy:

- v1 readers must ignore unknown extra fields so additive later fields do not break older tools immediately;
- v1 writers should preserve unknown fields where practical and only update fields they own;
- a missing, non-integer, lower-than-1, or higher incompatible `schema_version` must fail closed with stable token `blocked:unsupported_schema_version`;
- additive migrations within the same `schema_version` must be idempotent, repeatable, and local to the target project;
- migrations must not read, copy, or overwrite `MOE.md`, `.codex/agents/*.toml`, private prompt text, or existing `.omx/state` content unless a later explicit repair/change adds that behavior;
- downgrade is never automatic. Downgrade requires an explicit user request and uses the target project's Git history, backup refs, or the previous version recorded in an install receipt;
- if the central toolchain is newer but the target-project CLI lacks required `project-moe-cli-v1` commands, the GUI reports `blocked:missing_mode_cli` or a more specific CLI-contract token instead of directly scanning or modifying state files.

Upgrade acceptance requirements:

- `check_project_moe_gui_install.py --json` must distinguish `up_to_date`, `upgrade_available`, `migration_required`, `blocked:unsupported_schema_version`, and `blocked:missing_mode_cli`;
- `update_project_moe_gui.py` must print the install artifacts it will modify before writing and must emit an update receipt after writing;
- the update receipt must include at least the target project root, old/new `toolchain_version`, `schema_version`, changed files, skipped private files, timestamp, and rollback hint;
- a failed migration is never evidence that the MOE Agent was successfully enabled.

### 8.2 Runtime and launcher contract

The GUI source is maintained by this repository, but the runtime used to launch an installed GUI must be explainable, diagnosable, and replaceable inside the target project. The first launcher version must not depend on the operator's accidental shell `PATH` or global Python package state:

- `project-moe-gui.cmd` should resolve the target project root from the installed config and prefer the target project's recorded Python runtime; only fall back to a documented shared GUI runtime when no project runtime is configured;
- launchers must not permanently mutate user-level `PATH`, `PYTHONPATH`, pip config, or system environment variables; any environment override is scoped to the child process only;
- Windows launchers must force UTF-8-safe output, for example by setting child-process `PYTHONUTF8=1` or an equivalent mechanism, so Chinese paths, status tokens, and logs do not become mojibake;
- when the GUI invokes the project-local CLI, it must pass the resolved `--project-root` or an equivalent context and must not depend on the current working directory being accidentally correct;
- missing or non-executable Python runtime returns `blocked:python_runtime_unavailable`; missing required config fields or out-of-scope paths return `blocked:launcher_config_invalid`;
- launcher logs only record resolution steps, runtime path category, exit code, stdout/stderr summaries, and stable tokens; they must not record private prompts, raw session ids, paper text, or raw environment variable values;
- `check_project_moe_gui_install.py --json` must validate launcher presence, config, Python runtime, PySide6 importability, and the project-local CLI contract; failures include actionable remediation hints.

### 8.3 Installed artifact manifest and ownership boundary

The target project must contain an installed artifact manifest that distinguishes central-toolchain-managed install artifacts from target-project private files. The recommended first-version manifest path is:

```text
<project>/tools/project_moe_gui/project_moe_gui.install-manifest.json
```

The manifest records at least:

- `schema_version`, `toolchain`, `toolchain_version`, `source_repo`, and `source_commit`;
- `target_project_root`, `agent_name`, `state_namespace`, `installed_at`, and `updated_at`;
- `managed_files`: files owned by the installer and safe to rewrite during updates, such as the launcher, GUI wrapper files, and config templates;
- `protected_project_files`: files the installer must treat as read-only, such as `MOE.md`, `.codex/agents/*.toml`, paper content, private prompt sources, and `.omx/state`;
- each managed file's relative path, sha256, write reason, and previous-version hash;
- a summary or path for `last_dry_run` and `last_apply_receipt`.

Ownership rules:

- the updater may automatically modify only files listed under `managed_files`; if a managed file was manually edited in the target project and its hash no longer matches, report `blocked:managed_file_modified` or enter an explicit three-way merge/repair flow instead of overwriting it;
- when the manifest is missing, `check_project_moe_gui_install.py --json` reports `migration_required` or `blocked:launcher_config_invalid`; explicit install/update may regenerate it, but GUI startup must not;
- uninstall, cleanup, manifest deletion, launcher deletion, and audit/session-state deletion are not first-version automatic behaviors; if needed later, they require explicit uninstall/cleanup commands, dry runs, acceptance criteria, and rollback rules;
- the manifest must not copy project-private prompts, raw session ids, paper content, or audit-log content.

## 9. Safety and rollback rules

Implementation and update commands must:

- print the resolved target project root before writing;
- refuse to write outside the target project root;
- refuse to overwrite `MOE.md`, `.codex/agents/*.toml`, or `.omx/state` unless a later explicit repair command is created;
- create normal Git-reviewable changes in the target project;
- preserve enough status output for the user to see whether a project default or a session override was changed.
- distinguish implementation writes, state writes, install/update writes, and read-only status commands in output so an operator can audit what changed.

If an update fails halfway, rerunning the installer or updater must be safe. For project state changes, rollback is the target project's Git history plus the state JSON files under `.omx/state`.

### 9.1 State-write atomicity and concurrency control

The MOE control surface may be called by multiple Codex sessions, command-line wrappers, and the GUI at the same time. The first version must use a simple, auditable, cross-process local-file strategy to avoid corrupting state during concurrent writes:

- before writing project defaults, session overrides, or audit logs, acquire a state-namespace lock file such as `.omx/state/<state_namespace>/.lock`;
- lock-file content contains only operational metadata: pid, command, normalized session id, target state path, created_at, and lock timeout; it must not contain private prompt text or raw session ids;
- lock acquisition must use a short timeout and retry backoff; timeout returns `blocked:state_lock_timeout` and must not proceed with the write;
- suspected stale locks only report `blocked:stale_state_lock` plus the lock-file path and are not deleted automatically unless a later explicit repair/unlock command is added;
- JSON state writes must use a temporary file, flush/fsync, and atomic replace inside the same directory so partial files are not observed;
- `list-sessions --json`, `status --json`, and `project-status --json` are read-only by default and should not take the write lock; if they observe an in-progress write, they may retry briefly or report that state is changing;
- the GUI must serialize in-process button actions: while one on/off operation is in flight, duplicate buttons for the same scope are disabled;
- concurrency conflicts, lock timeouts, or atomic-replace failures are never evidence that a mode was enabled or disabled, and must surface stable tokens in CLI/GUI output and audit summaries.

### 9.2 Preview, apply, and operator-confirmation boundaries

To avoid silent writes in the wrong project, the first version must distinguish read-only checks, dry-run previews, and real apply operations:

- `check_project_moe_gui_install.py` is always read-only; it may report `up_to_date`, `upgrade_available`, or blockers, but it must not write;
- install/update `--dry-run --json` output must list `planned_writes`, `planned_skips`, `planned_migrations`, `target_project_root`, `state_namespace`, `agent_name`, and `rollback_hint`;
- real install/update writes require explicit apply semantics, for example the command name itself is install/update and output includes `mode = "apply"`, or a later implementation adds `--apply`; `check` and GUI startup must never implicitly install;
- `project-on`, `project-off`, `on --session-id`, and `off --session-id` may execute directly as explicit write commands, but JSON output must report before/after effective state, changed scope, and `no_op`;
- when the GUI first connects to a target project, it must display the target project root, agent name, state namespace, and current branch; before the user clicks on/off, button labels must make clear whether they affect the project default or one session;
- opening the GUI window, refreshing the session table, or reading status must not automatically perform install, update, migration, on/off, or repair;
- no-op operations should return success token `ok` with `no_op = true` and emit an audit summary or stdout summary so the operator can confirm no state changed;
- deletion, cleanup, unlock, repair, retention pruning, or uninstall of GUI artifacts are outside first-version implicit behavior and require later explicit commands and acceptance rules.

### 9.3 Path resolution and command-invocation safety boundary

Target project paths, installed artifact paths, and GUI-to-CLI command invocations are security boundaries. The first version must not rely on string prefixes or shell concatenation to decide safety:

- `--target-project`, `--project-root`, `mode_cli`, and all manifest managed/protected paths must be normalized and resolved to real paths before use; the resolved path must still be inside the target project root;
- reject `..` path traversal, absolute-path injection, UNC path escape, Windows drive switching, and symlinks or junctions that point managed files outside the project;
- permitted in-project symlinks or junctions must be explicitly reported in check output with `link_target_status`; unverifiable targets fail closed;
- when the GUI invokes the project-local CLI, it must use argv/list subprocess invocation and must not concatenate user input, session ids, paths, or reasons into shell strings;
- command logs may display redacted argv summaries, but must not log raw session ids, private reason content, or unnormalized user input;
- `reason`, session id, and agent name are data fields and must be validated for length, character set, and JSON serialization safety; they must not be reused as path fragments or shell fragments;
- any path escape, path traversal, external link target, or unsafe command invocation returns a stable blocker token and must not degrade to plain `usage_error`.

## 10. Audit log, privacy, and retention boundaries

MOE control tooling should emit a small local audit record for state-changing actions:

```text
.omx/state/<state_namespace>/audit/<yyyy-mm-dd>.jsonl
```

Each audit entry should contain only operational metadata: timestamp, command, stable token, exit code, project root, branch, normalized session id when applicable, state path, changed scope, and reason. Audit records must not contain `MOE.md` content, `developer_instructions`, raw session ids, raw environment variable values, thesis text, paper content, or browser/literature-search payloads.

Privacy and retention rules:

- retain `raw_session_id_sha256`, not raw session id values;
- keep project-private prompts and documents inside the target project;
- do not copy audit logs into `D:\PythonProject_langgraph` when installing or updating the GUI;
- make audit writing best-effort for state changes: failure to write the audit log should be reported but must not silently change the state without an error token;
- retention pruning is a later explicit feature and must not delete audit or session state in the first implementation.

## 11. Implementation slices and test matrix

Recommended Phase 1 target-project file ownership:

- `tools/thesis_moe_mode.py`: state model, command surface, effective status, and list output;
- `thesis-moe-on.cmd` and `thesis-moe-off.cmd`: project-level default wrappers;
- `docs_bilingual/operations/thesis_moe_mode_usage.zh-CN.md`: operator usage and failure modes;
- `AGENTS.md` or the target project's equivalent startup summary / launcher helper: session activation checkpoints and MOE state-reading rules;
- tests such as `tests/test_thesis_moe_mode.py` or the target project's existing test location: project default, session override, list output, invalid records, legacy compatibility, and the session activation chain.

Recommended Phase 2 central-repository file ownership:

- `tools/project_moe_gui_toolchain/src/project_moe_gui/`: GUI implementation;
- `tools/project_moe_gui_toolchain/install_project_moe_gui.py`: target-project install;
- `tools/project_moe_gui_toolchain/update_project_moe_gui.py`: idempotent update;
- `tools/project_moe_gui_toolchain/check_project_moe_gui_install.py`: installed artifact checker;
- `docs_bilingual/operations/project_moe_gui_usage.zh-CN.md`: operator documentation.

### 11.1 Implementation progress checklist

This checklist is ordered by concrete item. An item is not the same thing as an implementation slice. A phase-level checkbox means the whole phase definition of done has been satisfied; an item-level checkbox means there is local repository evidence or the contract is explicitly fixed by this plan. Do not read unchecked items under a phase as evidence that this plan is incomplete; they mean the item still needs target-project evidence, GUI evidence, or cross-project acceptance evidence.

Phase-level summary:

| Phase | Phase checkbox | Current status | Anti-ambiguity note |
| --- | --- | --- | --- |
| Phase 1: target-project command-line state model | [ ] | Pending target-project implementation/verification | It is unchecked because the `D:\PythonProject_paper_suggest` CLI, wrappers, startup hooks, and tests have not yet been confirmed by this repository. This repository now has a read-contract fixture gate, but the real target project remains incomplete. |
| Phase 2A: central installer, checker, and updater in this repository | [x] | Complete and merged into local `main` | Backed by this repository's local commit `3e4e819c73c78472d948e68d5352085dcac6551d` and local-gate evidence. |
| Phase 2B: PySide6 GUI application | [x] | Fixture-safe GUI shell complete and merged into local `main` | Covers import-safe shell, view model, write readback, same-scope pending disable, keyboard/high-contrast semantics, and explicit visible-window boundary; real visible-window/QTest evidence remains later operational evidence and does not block the repository fixture-safe definition. |
| Phase 2C: cross-project reuse and target install | [x] | Dual-fixture contract closed | Two isolated fixture projects now pass the same install/check/update/status contract, project A/B isolation, and private Agent TOML / `MOE.md` / state preservation on update; real target-project install still needs target-project Phase 1 completion and separate approval. |

#### Documentation and architecture contract

- [x] Define the project-level MOE Agent GUI toolchain goal and non-goals.
- [x] Define the boundary with the general PySide6 GUI capability plan.
- [x] Define required project-level MOE Agent TOML top-level fields.
- [x] Define recommended extension sections: `project`, `moe`, `dispatch`, and `extensions`.
- [x] Define default onboarding as validation of an existing Agent TOML, not default private-agent generation.
- [x] Define template generation as explicit dry run that must not copy another project's `MOE.md`.
- [x] Define the dispatch boundary forbidding `full-history fork + specified custom role`.
- [x] Define the compatible paths: main-session takeover, brief-based fresh dispatch, and durable brief.

#### Phase 1: target-project command-line state model

- [ ] Run read-only dirty/ownership preflight in `D:\PythonProject_paper_suggest`.
- [ ] Confirm the target project has `.codex/agents/<project-moe-agent>.toml` with fields matching this plan.
- [ ] Confirm the target project's private prompt source `MOE.md` stays inside that project.
- [ ] Implement or verify `tools/thesis_moe_mode.py project-on`.
- [ ] Implement or verify `tools/thesis_moe_mode.py project-off`.
- [ ] Implement or verify `tools/thesis_moe_mode.py project-status --json`.
- [x] Validate the `project-status --json` shared envelope, CLI contract, default-state fields, and session-count fields in this repository installer/checker fixtures.
- [ ] Implement or verify `tools/thesis_moe_mode.py list-sessions --json`.
- [x] Validate the `list-sessions --json` sessions array, counts object, row-level session identifier, enabled/effective fields, and stable token in this repository installer/checker fixtures.
- [ ] Implement or verify `tools/thesis_moe_mode.py on/off --session-id <id>`.
- [ ] Implement or verify `tools/thesis_moe_mode.py status --json` and `assert-on`.
- [x] Validate `status --json` boolean `effective_enabled`, supported `effective_source`, and raw/private-field fail-closed behavior in this repository installer/checker fixtures.
- [ ] Cover project default, session override, invalid records, legacy compatibility, and no-op tests.
- [x] Cover install-preflight fail-closed behavior for incomplete target CLI read contracts: missing `effective_source`, missing session counts, and exposed raw/private fields.
- [x] Cover GUI write-action fail-closed behavior for incomplete target CLI write contracts: missing `changed_paths`, mismatched `changed_scope`, and exposed raw/private fields.
- [x] Cover state lock, atomic write, lock timeout, and stale lock blocker fail-closed tests in the repository GUI shell fixtures: missing `atomic_write`, `atomic_write=false`, and `lock_timeout` / stale lock blockers must not be accepted as valid GUI write results.
- [ ] Wire `thesis-moe-on.cmd` and `thesis-moe-off.cmd`.
- [ ] Add MOE state-read checkpoints to the target project's startup / launcher / AGENTS surfaces.
- [ ] Write or update target-project operator documentation.
- [ ] Run the target-project local gate / smoke test and preserve evidence.

#### Phase 2A: central installer, checker, and updater in this repository

- [x] Create the `tools/project_moe_gui_toolchain/` toolchain directory.
- [x] Create the `tools/project_moe_gui_toolchain/src/project_moe_gui/` package boundary.
- [x] Implement `install_project_moe_gui.py`.
- [x] Implement `check_project_moe_gui_install.py`.
- [x] Implement `update_project_moe_gui.py`.
- [x] Implement install manifest and managed/protected file boundaries.
- [x] Fail closed when the target Agent TOML is missing.
- [x] Ensure dry run does not write target-project files.
- [x] Ensure apply writes target-project install artifacts and manifest.
- [x] Fail closed on hash mismatch.
- [x] Fail closed on path traversal / unsafe target blocker.
- [x] Write `docs_bilingual/operations/project_moe_gui_usage.zh-CN.md`.
- [x] Write `test/project_moe_gui_toolchain.test.py`.
- [x] Register tests in `tools/ci/ci_test_manifest.json`.
- [x] Pass local gate and merge Phase 2A into this repository's local `main`.

#### Phase 2B: PySide6 GUI application

- [x] Define the import-safe GUI shell entrypoint, window-structure descriptor, and guarded visible-launch boundary.
- [x] Implement target-project config reading from `project_moe_gui.config.json`.
- [x] Implement the top-banner view model: project root, agent name, state namespace, and current branch.
- [x] Implement the project-default status-card view model.
- [x] Implement the session-table view model and empty / invalid / load-failed states.
- [x] Implement the refresh action plan as read-only.
- [x] Implement project-default on/off action plans with explicit scope wording.
- [x] Implement selected-session on/off action plans with explicit scope wording.
- [x] Invoke the CLI from the GUI using argv/list, never shell string concatenation.
- [x] Prevent the GUI shell from directly writing `.omx/state` JSON.
- [x] Show stable tokens, short messages, and redacted stdout/stderr summaries in the GUI shell view model.
- [x] Disable same-scope buttons while write commands run, then re-read state.
- [x] Support keyboard operation and high-contrast/system-theme readability.
- [x] Add import-only fixture GUI tests and the explicit visible-window launch boundary; headless Qt / QTest / manual visual verification remains follow-up evidence for the real GUI.
- [x] Register GUI shell fixture coverage through the already registered `project_moe_gui_toolchain.test.py` local-gate test.

#### Phase 2C: cross-project reuse and target install

- [x] Verify the full install/check/update/status flow in at least one fixture project.
- [x] Verify the same contract in a second fixture or real project.
- [x] Confirm installing the GUI into project A controls only project A.
- [x] Confirm installing the GUI into project B controls only project B.
- [x] Confirm update never overwrites target-project private Agent TOML, `MOE.md`, or state.
- [x] Define dirty/ownership preflight before any real target-project install.
- [x] State that real target-project remote publication remains controlled by the target project's own publication workflow.
- [x] Record cross-project reuse acceptance evidence and decide whether this document should move beyond `draft`: because real target-project Phase 1 CLI is not complete, this document stays `draft` for now.

Minimum test matrix:

| Area | Required evidence |
| --- | --- |
| Project default | `project-on`, `project-off`, `project-status --json`, and new-session inheritance. |
| Session override | explicit `--session-id` on/off beats project default. |
| Session list | `list-sessions --json` returns redacted, valid, GUI-usable rows. |
| Invalid state | corrupt or mismatched state is reported and not auto-repaired. |
| GUI install | install refuses missing agent TOML and writes only inside the target project. |
| GUI actions | GUI action results match CLI `status --json` and `project-status --json`. |
| Concurrent writes | two commands writing the same namespace concurrently result in one success and the other either waiting then succeeding or returning a stable lock token; no partial JSON is produced. |
| Dry run / no-op | install/update dry run writes no files; repeated enable/disable outputs `no_op = true` and does not create meaningless file diffs. |
| Runtime/launcher | launcher does not depend on accidental `PATH`, UTF-8 output is clean, and missing Python runtime, PySide6, or bad config returns stable blocker tokens. |
| Installed artifact manifest | updates touch only declared managed files; private files remain read-only; hash mismatches fail closed. |
| Path and command safety | path traversal, outside-project link targets, and shell-concatenated command invocation are rejected; GUI-to-CLI calls use argv/list. |
| GUI usability | status badges include text semantics, error banners show stable tokens, refresh is read-only, button scope is explicit, and keyboard operation works. |
| Session lifecycle | `last_seen_at` updates only activity observation and not enabled state; stale/orphan are marked only; generated ids show lower confidence. |
| Session auto-effect | new sessions inherit project default; already-open sessions re-read `status --json` at resume/continue/reload/phase-change checkpoints; missing hook or CLI shows a blocker. |
| JSON output contract | `status`, `project-status`, `list-sessions`, and write commands return a shared envelope, stable tokens, redacted fields, and GUI-needed counts. |
| New project onboarding | existing Agent TOML is validated by default; template generation is explicit dry run; other projects' `MOE.md` content and invented private prompts are not copied. |
| Override conflict | project-level propagation does not overwrite manual session overrides; conflicts prefer session source and show effective source explicitly. |

Test execution and CI registration rules:

- central toolchain tests in this repository must use temporary directories or fixture projects that simulate the target project layout; ordinary unit tests must not write directly to `D:\PythonProject_paper_suggest`;
- real target-project smoke tests are explicit manual or integration-test steps and must first run the target project's dirty/ownership preflight;
- CLI JSON contracts require contract fixtures covering success, failure, no-op, lock timeout, invalid state, stale/orphan, and manual override conflict;
- install/update/check tests must verify dry run writes no files, apply writes the manifest, hash mismatch fails closed, and path traversal fails closed;
- PySide6 GUI tests should use headless Qt / QTest / pytest-qt or equivalent automation where possible; if no GUI runtime is available, CLI/installer tests remain required and GUI visual verification is recorded as manual evidence;
- screenshots or visual snapshots are supporting evidence only and must not replace CLI JSON contract checks and state-file assertions;
- new tests, checkers, or tool entrypoints must be registered in this repository's `tools/ci/ci_test_manifest.json` or the shared local-gate call chain so they are not local-only;
- target-project tests must be registered in the target project's own test entrypoint in that project's commit; this repository must not assume other projects' CI automatically covers these scripts.

Implementation phase gates and rollback points:

| Phase | Go/no-go condition | Rollback point |
| --- | --- | --- |
| Phase 0: read-only inventory | target-project dirty/ownership preflight passes, and existing Agent TOML, CLI, wrapper, and documentation paths are confirmed. | no writes; no rollback needed. |
| Phase 1A: CLI state model | fixture tests cover JSON envelope, project default, session override, lock, and invalid state; target-project local tests pass. | before target-project commit, discard the working tree; after commit, use target-project Git rollback. |
| Phase 1B: `paper_suggest` wrapper integration | `thesis-moe-on/off.cmd` calls project-level commands; real-project smoke test passes; no remote push. | revert the target-project wrapper and CLI commit; keep audit logs as local facts. |
| Phase 2A: central installer/checker | temporary fixture project verifies dry run/apply/manifest/hash/path blockers; local gate registration passes. | revert this repository's feature commit; delete target fixtures. |
| Phase 2B: PySide6 GUI | headless GUI automation or manual visual evidence satisfies usability rules; GUI never writes JSON directly. | remove or revert target-project managed install artifacts; never delete `.omx/state`. |
| Phase 2C: cross-project reuse | at least two different fixture or real projects pass the same contract; no cross-project state leakage. | revert installed artifacts; preserve project-private Agent TOMLs and prompt sources. |

Definition of done for each phase:

- the phase's contract, tests, documentation, and operator commands are updated;
- any new checker/test introduced by the phase is registered in this repository or target project's test entrypoint;
- the working tree is clean, and the commit message names the phase and rollback approach;
- without an explicit remote-publication instruction, do not push to GitLab/GitHub and do not mutate target-project remotes.

## 12. Validation and acceptance

Document-level acceptance for this plan:

- English and Chinese plan files exist as a pair;
- the plan clearly separates the MOE GUI toolchain from generic GUI tooling;
- the plan defines project default plus session override behavior;
- the plan forbids `full-history fork + specified custom role` for project MOE Agents;
- the plan defines state-write locking, atomic writes, concurrency failure tokens, and GUI serialization boundaries;
- the plan defines check, dry-run, apply, no-op, and GUI operator-confirmation boundaries;
- the plan defines runtime/launcher resolution, UTF-8 output, environment-variable boundaries, and missing-dependency blockers;
- the plan defines the installed artifact manifest, managed/protected file ownership, and uninstall/cleanup non-goals;
- the plan defines path normalization, symlink/junction, path traversal, and command-invocation safety boundaries;
- the plan defines GUI status badges, error banners, refresh semantics, button scope, empty states, and keyboard accessibility;
- the plan defines session lifecycle, last seen, stale/orphan marking, and pruning non-goals;
- the plan defines the auto-effect chain for new and already-open sessions to read MOE state at startup, resume, continue, reload, and phase-change checkpoints;
- the plan defines the CLI JSON envelope, status fields, count fields, write-result fields, and redacted failure fields;
- the plan defines new project onboarding, scaffold dry run, Agent TOML/namespace validation, and private prompt-source boundaries;
- the plan defines project-level propagation, manual session overrides, conflict display, and clear-override non-goals;
- the plan defines test fixtures, contract tests, GUI automation/manual evidence boundaries, and CI registration rules;
- the plan defines Phase 0/1/2 gates, go/no-go conditions, definitions of done, and rollback points.

Phase 1 acceptance:

- `thesis-moe-on.cmd` enables project default and registered sessions;
- `thesis-moe-off.cmd` disables project default and registered sessions;
- new sessions inherit project default;
- already-open sessions re-read MOE state at resume/continue/reload/phase-change activation checkpoints;
- explicit `--session-id` overrides work;
- `assert-on` follows the effective status rule.

Phase 2 acceptance:

- installing the GUI into `paper_suggest` controls only `paper_suggest`;
- installing into a second project controls only that second project;
- no target project's private agent TOML, `MOE.md`, or state is overwritten by GUI update;
- GUI actions and CLI status agree.

## 13. Immediate next implementation boundary

Next implementation should proceed as: close the target-project CLI first, keep GUI work fixture-backed first, and defer real target install until the target CLI contract exists.

1. To control real `D:\PythonProject_paper_suggest` sessions, complete Phase 1 in the target project first: CLI state model, `list-sessions --json`, `status --json`, `assert-on`, `thesis-moe-on/off.cmd`, and target-project startup checkpoints.
2. If there is no target-project write approval, this repository may continue with Phase 2B only against fixture/mock target projects; it must not write real `paper_suggest` `.omx/state`.
3. The Phase 2B GUI may change state only by invoking the target-project CLI; if that CLI is missing, the GUI must show a blocker instead of scanning or writing state files directly.
4. Phase 2C is closed at the repository fixture layer after two isolated fixtures passed the same contract; this follow-up also adds the Phase 1 read-contract fixture gate, the GUI write-command output-contract fixture gate, and the write-command atomic/lock fixture gate, while real-project install still depends on later target-project approval and Phase 1 readiness.
5. This document does not move from `draft` yet: Phase 2B, fixture-level Phase 2C, the repository Phase 1 read-contract gate, the GUI write-command output-contract gate, and the write-command atomic/lock gate now have local evidence, but the real target-project Phase 1 CLI / wrapper / startup checkpoint remains incomplete.

Phase gate rules:

- Phase 1 is complete only after command-line tests prove project default, registered-session propagation, session override, invalid-record skip, and legacy-record readability.
- Phase 2A is complete on this repository's local `main`; it covers only the central installer/checker/updater and does not remove the Phase 1 prerequisite for real GUI use.
- Phase 2B may start in fixture mode in this repository; real target-project GUI install still requires the Phase 1 CLI contract.
- Any GUI source, checker, or test added to this repository should be implemented as a separate local change and run through this repository's local gate.
- Remote publication is outside this plan and requires the repository publication workflow.
