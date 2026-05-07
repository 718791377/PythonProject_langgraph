## 1. Implementation

- [x] Make `taskkill.exe` cleanup shimming default-requested for wrapped installs, with explicit opt-out.
- [x] Make the generated launcher prioritize `.EXE` only when the generated `taskkill.exe` shim exists at runtime.
- [x] Update the cleanup-output checker to require explicit `taskkill.exe` coverage markers.
- [x] Update installer and checker tests for default, explicit, and opt-out behavior.
- [x] Add bilingual OpenSpec artifacts for this change.

## 2. Validation

- [x] Run `python .\tools\check_windows_cleanup_output_control.py --root . --json`.
- [x] Run `python .\test\check_windows_cleanup_output_control.test.py`.
- [x] Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1`.
- [x] Run `openspec validate --all`.
- [x] Run `python .\tools\run_openspec_guard.py --root . --tool codex --json`.
- [x] Run `git diff --check`.
