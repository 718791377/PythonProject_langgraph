---
doc_id: project_moe_gui_usage
lang: en
canonical: docs_bilingual/operations/project_moe_gui_usage.md
status: draft
doc_class: operations
related_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
related_docs:
  - docs_bilingual/operations/project_moe_gui_usage.zh-CN.md
---

# Project MOE GUI Toolchain Usage Guide

This guide covers the Phase 2A installer, updater, uninstaller, and checkers. Phase 2A installs only project-local managed artifacts such as the launcher, config, and manifest. The interactive PySide6 window GUI belongs to Phase 2B.

## Prerequisites

The target project must already provide:

- `.codex/agents/<agent>.toml`, with a top-level `name` matching the install argument;
- a project-local MOE CLI, defaulting to `tools/thesis_moe_mode.py`;
- CLI support for `project-status --json`, `list-sessions --json`, and `status --json`;
- `project-status --json` returning `cli_contract = project-moe-cli-v1`.

The installer does not read or copy the target project's private `MOE.md`, does not overwrite `.codex/agents/*.toml`, and does not write `.omx/state`.

## Phase 1 Read-Only Readiness Check

Before writing any CLI, wrapper, or GUI install artifact to a real target project, run the read-only readiness checker. It reads the target project but writes nothing:

```powershell
python tools/project_moe_gui_toolchain/check_project_moe_phase1_readiness.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --json
```

The checker verifies:

- whether the target project Git state is clean;
- whether `.codex/agents/<agent>.toml` exists and its core fields match;
- whether the private prompt source `MOE.md` remains inside the target project;
- whether `tools/thesis_moe_mode.py` exposes the read contract: `project-status --json`, `list-sessions --json`, and `status --json`;
- whether the CLI text exposes the Phase 1 write command surface: `project-on`, `project-off`, `on`, `off`, and `assert-on`;
- whether `thesis-moe-on.cmd` and `thesis-moe-off.cmd` call `project-on` and `project-off`;
- whether `AGENTS.md` or the startup summary contains a `status --json` activation checkpoint.

Only `read_only = true` and `writes_target_project = false` count as read-only evidence. If the payload returns tokens such as `blocked:dirty_target_project`, `blocked:missing_phase1_wrapper`, or `blocked:missing_moe_activation_hook`, fix the target project first or request a separate write authorization before continuing.

By default, execute-read-contract mode executes the target CLI only after the full static surface passes. If the target project is dirty, or if wrappers, startup files, operator docs, Agent TOML, private prompt source, or other static checks still have blockers, the checker skips target CLI execution and returns `execution_skipped = true`, `skip_reason = static_surface_blockers_present`, and `static_surface_blocking_codes` in `cli_contract_check`. This avoids triggering read commands that may update last-seen markers or state before the static gate is satisfied.

## Preview Install

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --dry-run --json
```

The preview output includes `planned_writes`, `planned_skips`, `planned_migrations`, `blockers`, and `rollback_hint`. `--dry-run` does not write target project files.

## Apply Install

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --json
```

Installed artifacts live inside the target project:

```text
tools/project_moe_gui/launcher.py
tools/project_moe_gui/project_moe_gui.config.json
tools/project_moe_gui/project_moe_gui.install-manifest.json
tools/project_moe_gui/README.md
project-moe-gui.cmd
```

`project-moe-gui.cmd --preflight --json` only runs launcher and target CLI preflight checks. The full window GUI is added in Phase 2B.

## Check and Update

```powershell
python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project D:\SomeProject --json
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:\SomeProject --dry-run --json
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:\SomeProject --json
```

The install checker verifies the manifest hashes for managed files. If the target project has modified a managed file, it returns `blocked:managed_file_hash_mismatch`, and the updater must not overwrite that file silently.

## Preview Uninstall / Cleanup Plan

When uninstalling or cleaning up Project MOE GUI, first generate a plan without deleting target project files:

```powershell
python tools/project_moe_gui_toolchain/plan_project_moe_gui_uninstall.py `
  --target-project D:\SomeProject `
  --json
```

The command reads only `project_moe_gui.install-manifest.json` and managed file hashes, then returns `planned_deletes` and `protected_paths_preserved`. It must satisfy:

- `read_only = true`;
- `writes_target_project = false`;
- `apply_supported = true`;
- `state_deletion_allowed = false`;
- `private_files_deletion_allowed = false`, meaning the uninstall plan must not delete project-private files such as `MOE.md` or `.codex/agents/*.toml`.

If a managed file hash does not match, the command returns `blocked:managed_file_hash_mismatch` and must not treat the locally modified managed file as deletable. The plan does not delete `.omx/state`, private `MOE.md`, or `.codex/agents/*.toml`.

After reviewing `planned_deletes`, explicitly pass `--apply` to perform the actual uninstall:

```powershell
python tools/project_moe_gui_toolchain/plan_project_moe_gui_uninstall.py `
  --target-project D:\SomeProject `
  --apply --json
```

`--apply` deletes only Project MOE GUI managed files that are both in the manifest allowlist and hash-verified. If the manifest tries to declare `MOE.md`, `.codex/agents/*.toml`, `.omx/state`, or any other path outside the allowlist, the command returns `blocked:uninstall_path_not_in_managed_allowlist` and `delete_executed = false`. On success it returns `delete_executed = true`, `applied_file_changes`, and `uninstall_receipt`.

## Rollback

Rollback depends on the target project Git history and `project_moe_gui.install-manifest.json`. Rolling back GUI artifacts must not delete `.omx/state`, private `MOE.md`, or Agent TOML files.

`project-moe-gui.cmd --preflight --json` first runs the Phase 1 readiness gate. If the static surface still has blockers, the launcher returns the repair order in `phase1_readiness_gate`, `remediation_plan`, and `operator_next_steps`, and it skips target CLI execution to avoid side effects in `.omx/state/<namespace>/`. The launcher enters the control path only when GUI control prerequisites are satisfied; blockers such as `blocked:dirty_target_project` must fail closed.
