## Why

The P0 control layer is already installed and validated, but it still stops at persisted state and helper scripts.

What is still missing is the startup binding that makes the global `oh_my_codex` and `subagent_routing` state affect normal `codex` launches without replacing the native Codex executable.

The user-level solution is not complete until a normal PowerShell `codex` launch can:

- keep native Codex available
- enter Codex + oh-my-codex mode when `oh_my_codex=on`
- stay in native mode when `oh_my_codex=off`
- disable role orchestration when `subagent_routing=off`
- recover safely if startup-binding installation fails

## What Changes

- Extend the repo-local installer to generate a startup-binding launcher script for PowerShell shells.
- Add a managed PowerShell profile block that routes `codex` through the launcher while preserving a raw `codex-native` escape hatch.
- Map `oh_my_codex` and `subagent_routing` state to runtime Codex CLI arguments rather than replacing the native `codex` binary.
- Preserve native `codex`, `codex.cmd`, and `codex.ps1` untouched.
- Extend install-time backup and rollback coverage to the PowerShell profile and startup-binding assets.
- Add tests that validate launcher argument mapping, profile-block installation, and rollback of partial startup-binding failures.

## Capabilities

### New Capabilities

- `codex-user-level-team-mode-startup-binding`
  - provide a reversible PowerShell startup binding that applies user-level team-mode state to normal Codex launches without replacing the native executable

### Modified Capabilities

- `codex-user-level-team-mode-controls`
  - extend the installer and validation surface to cover startup-binding assets and the PowerShell profile block

## Impact

- Affected paths:
  - `tools/install-codex-user-level-team-mode.ps1`
  - `test/install-codex-user-level-team-mode.test.ps1`
  - `openspec/changes/implement-codex-user-level-team-mode-p1-startup-binding/`
- This change will add a managed block to the user's PowerShell profile during real installation.
- This change will not replace or patch the native `codex` npm-installed files.
- This change standardizes the supported startup-binding path as native Windows PowerShell, not `cmd.exe` and not WSL2.

## impact_scope

- user-level startup binding for PowerShell-based Codex launches
- launcher-side mapping from persisted team-mode state to Codex CLI runtime overrides
- managed profile integration with backup and rollback
- preservation of the native Codex binary path plus a bypass entrypoint

## explicit_non_goals

- no replacement of `C:\Users\lenovo\AppData\Roaming\npm\codex*`
- no mandatory startup binding for `cmd.exe`
- no WSL2 startup path
- no mixed-pane compose orchestration in this phase
- no OpenClaw runtime configuration changes

## rollout_sequence

1. Create the P1 OpenSpec artifacts for startup binding.
2. Generate a launcher script that reads `user-level-team-mode.json` and computes Codex CLI overrides.
3. Generate a managed PowerShell profile block that defines `codex` and `codex-native`.
4. Extend backup snapshots and rollback to cover the profile path and startup-binding assets.
5. Validate profile installation, launcher argument mapping, and rollback behavior in a temporary environment.
6. Reinstall into the real user home only after repository validation passes.

## rollback_plan

- Remove the startup-binding launcher and profile block if the binding proves misleading or unsafe.
- Keep rollback narrow: restore the previous PowerShell profile content and remove only the new managed startup-binding assets.
- Do not touch the native npm-installed `codex` files during rollback.

## validation_path

- run the dedicated PowerShell test for startup-binding installation and launcher behavior
- verify the launcher preserves the native executable path and exposes a raw bypass entrypoint
- verify `oh_my_codex=off` clears omx-specific startup behavior
- verify `subagent_routing=off` disables multi-agent startup routing
- verify partial startup-binding installation failures restore the pre-install profile content
- run `openspec validate --all`
- run `python .\tools\run_openspec_guard.py --root .`
