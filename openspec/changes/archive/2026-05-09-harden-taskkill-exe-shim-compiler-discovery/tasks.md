## 1. Implementation

- [x] Harden installer compiler discovery for `taskkill.exe` shim.
- [x] Move compiler capture files to generated shim directory.
- [x] Extend cleanup-output checker markers.
- [x] Add regression tests for framework compiler fallback and Chinese success-output suppression.
- [x] Patch authorized Twilio plugin cache SKILL metadata.

## 2. Validation

- [x] Run `test/check_windows_cleanup_output_control.test.py`.
- [x] Run installer compile smoke and confirm `taskkill.exe` is produced when Framework `csc.exe` is available.
- [x] Run `python tools/run_openspec_guard.py --root .` using the repository venv Python.
- [x] Regenerate/install user-level wrapper and verify installed `win-shims\taskkill.exe` exists.
- [x] Verify Twilio cache frontmatter parses and description length is under 1024 characters.
