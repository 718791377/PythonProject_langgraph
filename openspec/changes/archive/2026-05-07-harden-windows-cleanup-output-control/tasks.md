# Tasks

## 1. Plan and OpenSpec Artifacts

- [x] 1.1 Update `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md`, the English implementation plan that documents the Windows cleanup-output hardening scope.
- [x] 1.2 Update `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.zh-CN.md`, the Chinese companion implementation plan for the same cleanup-output hardening scope.
- [x] 1.3 Create `openspec/changes/harden-windows-cleanup-output-control/proposal.md`, the OpenSpec proposal that records why this hardening is needed.
- [x] 1.4 Create `openspec/changes/harden-windows-cleanup-output-control/design.md`, the OpenSpec design that records how optional EXE shimming remains scoped and opt-in.
- [x] 1.5 Create `openspec/changes/harden-windows-cleanup-output-control/specs/codex-user-level-windows-cleanup-output-control/spec.md`, the delta spec for the cleanup-output control capability.

## 2. Installer and Checker Implementation

- [x] 2.1 Update `tools/install-codex-user-level-team-mode.ps1`, the user-level team-mode installer, to add the `InstallTaskkillExeShim` opt-in switch.
- [x] 2.2 Update `tools/install-codex-user-level-team-mode.ps1` so explicit opt-in compiles `taskkill-shim-source.cs`, the managed C# shim source, into `win-shims\taskkill.exe`.
- [x] 2.3 Update generated startup launcher logic so `.EXE` PATHEXT precedence is enabled only when the optional EXE shim is installed.
- [x] 2.4 Update installer JSON output so `taskkill_exe_shim_enabled`, `taskkill_exe_shim_path`, and `taskkill_exe_shim_compile` describe the optional EXE shim state.
- [x] 2.5 Update `tools/check_windows_cleanup_output_control.py`, the cleanup-output checker, to guard the optional executable hardening markers.

## 3. Tests and Validation

- [x] 3.1 Update `test/check_windows_cleanup_output_control.test.py`, the cleanup-output checker test, to fail when optional executable hardening markers are removed.
- [x] 3.2 Update `test/install-codex-user-level-team-mode.test.ps1`, the installer behavior test, to verify default EXE interception stays disabled.
- [x] 3.3 Update `test/install-codex-user-level-team-mode.test.ps1` to verify explicit `InstallTaskkillExeShim` opt-in creates `win-shims\taskkill.exe` and scopes `.EXE` PATHEXT precedence.
- [x] 3.4 Run `python test/check_windows_cleanup_output_control.test.py`, the checker unit test command for cleanup-output control.
- [x] 3.5 Run `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`, the installer integration test command for generated user-level assets.
- [x] 3.6 Run `python tools/check_windows_cleanup_output_control.py --root . --json`, the direct cleanup-output checker command.
- [x] 3.7 Run `openspec validate --all`, the OpenSpec validation command for all specs and changes.
- [x] 3.8 Run `python tools/run_openspec_guard.py --root . --tool codex --json`, the repository guard command.
- [x] 3.9 Run `git diff --check`, the whitespace validation command for the patch.
