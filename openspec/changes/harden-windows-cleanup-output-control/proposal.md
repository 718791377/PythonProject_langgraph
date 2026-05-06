# Proposal: Harden Windows cleanup output control

## Why

Wrapped `codex-ohmy` sessions can still leak benign Windows `taskkill` success lines into the conversation after native subagent or `/resume` cleanup. The existing `taskkill.cmd` shim covers normal PATHEXT lookup, but the recent subagent path shows that some cleanup callers may bypass that path or not inherit the expected shim behavior.

## What Changes

- Harden the existing Windows cleanup-output control instead of disabling `omx_*` MCP tools or avoiding native subagents.
- Keep the default wrapped launch conservative by continuing to prioritize `taskkill.cmd` for normal command lookup.
- Add an explicit opt-in `InstallTaskkillExeShim` installer switch that compiles and installs `taskkill.exe` from the managed C# shim source when direct `.exe` interception is needed.
- Extend generated startup launchers so `.EXE` PATHEXT precedence is only added when the opt-in EXE shim is installed.
- Extend checker and tests so cleanup-output control covers default CMD shimming, optional EXE shimming, scoped PATH/PATHEXT mutation, and preserved direct `omx_*` MCP startup overrides.

No breaking changes are intended.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`: add optional `taskkill.exe` shim hardening for cleanup paths that bypass `taskkill.cmd`, while keeping the default wrapped launch conservative and scoped.

## Impact

- Affected source:
  - `tools/install-codex-user-level-team-mode.ps1`, the user-level installer that generates managed wrappers and helper assets.
  - `tools/check_windows_cleanup_output_control.py`, the repository checker for Windows cleanup-output control.
  - `test/install-codex-user-level-team-mode.test.ps1`, the installer behavior test.
  - `test/check_windows_cleanup_output_control.test.py`, the checker behavior test.
  - `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md` and `.zh-CN.md`, the implementation plan pair for this hardening work.
  - `openspec/specs/codex-user-level-windows-cleanup-output-control/spec.md` and `.zh-CN.md`, the stable cleanup-output control contract after sync/archive.
- No change to `C:\Users\lenovo\.codex\config.toml`.
- No MCP Router dependency.
- No change to native Codex bypass launchers except preserving their no-wrapper behavior.

## Impact Scope

This is a cross-mainline maintenance hardening change under the Codex user-level orchestration maintenance line. It affects wrapped Windows launch behavior and generated user-level helper assets, not business-project runtime behavior.

## Explicit Non-Goals

- Do not disable `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace`.
- Do not require users to abandon the temporary-session-first `/resume` workflow.
- Do not route Codex-dedicated `omx_*` MCP tools through MCP Router.
- Do not globally filter the whole Codex TUI output stream.
- Do not install optional `taskkill.exe` interception by default without explicit operator or installer opt-in.

## Rollout Sequence

1. Update the existing implementation plan pair.
2. Add this OpenSpec change and delta spec.
3. Harden the installer, checker, and tests locally.
4. Run local validation only.
5. Recommend GitLab publication only after local validation passes.
6. After GitLab merge, reinstall user-level team-mode assets if the operator wants the hardening to affect future `codex-ohmy` launches.

## Rollback Plan

- Revert this repository change and reinstall the previous user-level team-mode assets.
- Or restore the relevant managed-install backup under `C:\Users\lenovo\.codex\backups`, the user-level backup directory produced by the installer.
- Remove only the generated optional `taskkill.exe` shim if the opt-in path causes an environment-specific issue; keep the default CMD shim path.

## Validation Path

- `python test/check_windows_cleanup_output_control.test.py`: validates cleanup-output checker behavior.
- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`: validates installer-generated wrapped launch and optional EXE shim behavior.
- `python tools/check_windows_cleanup_output_control.py --root . --json`: validates cleanup-output control source markers.
- `openspec validate --all`: validates OpenSpec artifacts.
- `python tools/run_openspec_guard.py --root . --tool codex --json`: runs repository guard checks.
- `git diff --check`: checks patch formatting.

## Mainline Classification

Existing cross-mainline maintenance issue under Codex user-level orchestration maintenance. It hardens an existing user-level Windows cleanup-output capability and does not create a new mainline.
