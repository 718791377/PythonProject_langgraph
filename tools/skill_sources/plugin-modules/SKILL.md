---
name: plugin-modules
description: Load Codex plugin modules on demand with soft-load references or hard-load startup profiles. Use for skills budget, plugin profiles, module switching, or plugin guidance.
---

# Plugin Modules

Use this skill when the operator wants a task-scoped plugin capability module instead of keeping every plugin skill always visible.

## Core workflow

1. List available modules when the requested module is unclear:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/list_module.ps1
   ```
2. For current-session guidance, soft-load the module:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/load_module.ps1 <module> -Json
   ```
   Read only the returned `skill_docs` that are relevant to the user task. This does not edit `config.toml` and does not require restart.
3. For next-startup plugin visibility or plugin MCP/app availability, preview the profile first:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/set_plugin_profile.ps1 <module> -Json
   ```
4. Apply a hard-load profile only after explicit operator approval:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/set_plugin_profile.ps1 <module> -Apply
   ```
   The script backs up `config.toml`, edits only `[plugins."..."] enabled = ...`, and prints restart/resume instructions.

## Skills budget and standalone user-skill pressure

Plugin profiles only edit plugin enablement in `config.toml`. They do not hide or disable standalone user skills under `CODEX_HOME/skills`.

When `skills2cli profile suggest` reports `standalone_user_skill_pressure.user_layer_pressure=true`, do not keep reapplying `core-dev` as the primary fix. Instead:

```powershell
skills2cli visibility plan --profile core-dev --json
skills2cli visibility apply --profile core-dev --apply --operator-confirmation --json
skills2cli visibility restore --receipt <receipt_id> --apply --operator-confirmation --json
```

`visibility plan/status` are read-only. `visibility apply/restore` require both `--apply` and `--operator-confirmation`, write a rollback receipt, move only standalone user-skill directories, and do not edit plugin cache or `config.toml`.

## Safety rules

- Do not delete plugin cache files.
- Do not bulk-edit bundled plugin `SKILL.md` files.
- Prefer soft-load for guidance, planning, code generation, and API ordering.
- Use hard-load only when startup-visible skills or plugin MCP/app tools are needed.
- Treat disabled plugins as dormant; restore with `set_plugin_profile.ps1 full -Apply` or `set_plugin_profile.ps1 -RestoreLatest -Apply`.
- Keep direct Codex MCP entries and oh-my-codex orchestration settings outside profile edits.

## Module names

The modules are `core-dev`, `web-saas`, `company-ops`, `market-research`, `customer-comms`, `creative-content`, `pyside6-gui`, and `full`.

Use `pyside6-gui` when a task asks for local desktop GUI, PySide6, Qt, Windows desktop tooling, a local operator console, or GUI packaging preflight. It is a repo-local soft-load module: it reads the project-local PySide6 skill, helper, and templates, but it does not install PySide6, mutate `config.toml`, enable unrelated plugins, launch a visible GUI, or package executables by itself.
