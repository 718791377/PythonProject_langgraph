# OMX MCP Windows Cleanup Output Control Plan

## Status

- Phase: active follow-up implementation.
- Mainline: Codex user-level orchestration maintenance.
- OpenSpec change: `harden-windows-cleanup-output-control`, the change that hardens the direct `omx_*` MCP workflow by suppressing benign Windows cleanup output across wrapped launch and subagent cleanup paths.

## Problem

The operator wants to start `codex-ohmy`, enter a temporary Codex TUI session, and then use `/resume` inside that session. With `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` enabled, the `/resume` path can clean up temporary-session child processes and leak normal Windows `taskkill` success output into the conversation.

The noise is not a functional failure, but it pollutes the session and can confuse later cold-start recovery.

## Goals

- Keep `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` enabled for `codex-ohmy` full mode.
- Keep the temporary-session-first `/resume` workflow.
- Suppress benign `taskkill` success output from the main Codex session.
- Preserve cleanup failures and non-zero exit diagnostics.
- Scope any PATH or shim change to the wrapped launch only.
- Avoid editing `C:\Users\lenovo\.codex\config.toml`, the user-level Codex configuration file controlled by the operator.

## Non-goals

- Do not disable `omx_*` MCP tools as the long-term fix.
- Do not require `codex-ohmy resume <session-id>` as the only supported resume path.
- Do not move `omx_*` MCP tools into MCP Router.
- Do not filter the whole interactive Codex TUI stream.
- Do not claim the final personal production-grade durable team is complete.

## Implementation Steps

1. Add OpenSpec artifacts for the cleanup-output control contract.
2. Add `win-shims` generation to `tools/install-codex-user-level-team-mode.ps1`, the user-level installer that writes managed launchers and helper scripts.
3. Generate `taskkill.cmd`, `taskkill.ps1`, and `taskkill-shim-source.cs`; these files are the CMD shim, PowerShell shim, and optional C# shim source used to call the real `taskkill.exe` while suppressing success output.
4. Add an opt-in `InstallTaskkillExeShim` installer switch; this switch compiles and installs `taskkill.exe` only when evidence shows a caller bypasses PATHEXT and invokes an `.exe` path directly.
5. Keep the default path conservative: by default, wrapped launch only prioritizes `taskkill.cmd`; with the explicit opt-in, wrapped launch also prioritizes `taskkill.exe`.
6. Update the generated startup launcher so it prepends `win-shims` to PATH only while invoking native Codex, then restores PATH in `finally`.
7. Add `tools/check_windows_cleanup_output_control.py`, a checker that validates source evidence for shim generation, optional EXE control, PATH restoration, and preserved `omx_*` MCP startup overrides.
8. Add tests for installer and checker behavior, including default non-EXE mode and explicit EXE opt-in.
9. Run validation and publish by GitLab-first MR.

## Validation

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`: validates installer-generated launchers and shims.
- `python test/check_windows_cleanup_output_control.test.py`: validates the checker.
- `python tools/check_windows_cleanup_output_control.py --root . --json`: runs the checker directly.
- `openspec validate --all`: validates OpenSpec artifacts.
- `python tools/run_openspec_guard.py --root . --tool codex --json`: runs the repository guard.
- `git diff --check`: checks patch formatting.

## Rollback

- Revert the repository change and reinstall user-level team-mode assets.
- Or restore the installer backup under `C:\Users\lenovo\.codex\backups`, the user-level backup directory produced by managed installs.
- No MCP Router rollback is needed because this plan does not use MCP Router.
