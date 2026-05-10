## Why

The previous Windows cleanup-output fix suppresses benign `taskkill` success output when the wrapped `codex-ohmy` child process keeps the generated `win-shims` directory on PATH. The leak can still recur when a spawned Windows PowerShell login shell resets PATH from Machine/User environment and removes the wrapped shim directory before cleanup runs.

That regression reintroduces lines such as `SUCCESS: The process with PID ... has been terminated.` or localized Chinese `成功: 已终止 PID ...` into the Codex session even though cleanup succeeded.

## What Changes

- Add a scoped launcher-to-login-shell environment bridge that exposes the generated `win-shims` path as `CODEX_USER_LEVEL_CLEANUP_SHIM_DIRECTORY` only during wrapped `codex-ohmy` launches.
- Extend the managed PowerShell profile block so login shells spawned inside a wrapped session re-prepend the cleanup shim directory after any PATH reset.
- Preserve `.EXE`/`.CMD` `PATHEXT` behavior so `taskkill.exe` still resolves to the generated shim when available and falls back to the CMD shim otherwise.
- Restore the environment bridge after the native Codex command exits.
- Add checker and regression-test coverage for the profile bridge.

## Impact

- `tools/install-codex-user-level-team-mode.ps1` - generates the launcher/profile bridge and installs user-level wrappers.
- `tools/check_windows_cleanup_output_control.py` - verifies cleanup-output control source markers.
- `test/install-codex-user-level-team-mode.test.ps1` - covers generated launcher/profile behavior.
- `test/check_windows_cleanup_output_control.test.py` - covers checker regressions for required markers.
- `docs_bilingual/implementation_plans/plugin_modules_profile_helper_plan.md` records the separate operator-approved future Option C skills/profile-helper plan.

## Non-goals

- Do not disable `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace`.
- Do not mutate `C:\Users\lenovo\.codex\config.toml`.
- Do not globally modify Windows Machine/User PATH.
- Do not suppress non-zero cleanup failures.
- Do not implement the future `plugin-modules` skill/profile helper in this change.