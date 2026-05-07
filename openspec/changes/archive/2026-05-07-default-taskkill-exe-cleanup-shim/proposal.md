## Why

Wrapped `codex-ohmy` sessions can still leak benign Windows cleanup lines such as `SUCCESS: The process with PID ... has been terminated.` after `/resume` or subagent cleanup. The current cleanup-output control installs `taskkill.cmd` and `taskkill.ps1`, but the explicit `taskkill.exe` shim is only optional and is not present in the installed user-level helper. Cleanup paths that invoke `taskkill.exe` directly can bypass the scoped shims.

## What Changes

- Attempt installation of the `taskkill.exe` cleanup shim by default, while keeping a compatibility opt-in switch and adding an explicit opt-out switch.
- Make the wrapped launcher prioritize `.EXE` cleanup shimming only when the generated `taskkill.exe` shim exists; otherwise it falls back to the existing `.CMD` shim.
- Keep native bypasses free of wrapper-specific PATH/PATHEXT mutation.
- Strengthen the checker and tests so future changes cannot silently regress explicit `taskkill.exe` output control.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`: hardens cleanup-output control for explicit `taskkill.exe` invocation paths.

## Impact

- impact_scope: user-level installer source, cleanup-output checker, installer tests, checker tests, and this OpenSpec change.
- explicit_non_goals: no `C:\Users\lenovo\.codex\config.toml` edits, no MCP Router changes, no disabling of `omx_*` MCP entries, no durable team launch, and no repository durable state mutation.
- rollout_sequence: implement source hardening, validate locally, archive the completed change into stable spec if validation passes, publish via GitLab-first MR, then refresh user-level helpers after merge.
- rollback_plan: revert this change and rerun the installer to restore the previous `.cmd`/`.ps1`-only cleanup control.
- validation_path: run the cleanup-output checker, checker unit test, installer PowerShell test, `openspec validate --all`, `python .\tools\run_openspec_guard.py --root . --tool codex --json`, and `git diff --check`.