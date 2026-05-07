## 1. Implementation

- [x] 让 wrapped 安装默认请求 `taskkill.exe` 清理 shim，并提供显式跳过开关。
- [x] 让生成的 launcher 只有在运行时存在 `taskkill.exe` shim 时才优先 `.EXE`。
- [x] 更新清理输出 checker，要求覆盖 explicit `taskkill.exe` 控制标记。
- [x] 更新 installer 和 checker 测试，覆盖默认、显式启用、显式跳过行为。
- [x] 为本 change 添加双语 OpenSpec artifacts。

## 2. Validation

- [x] 运行 `python .\tools\check_windows_cleanup_output_control.py --root . --json`。
- [x] 运行 `python .\test\check_windows_cleanup_output_control.test.py`。
- [x] 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\test\install-codex-user-level-team-mode.test.ps1`。
- [x] 运行 `openspec validate --all`。
- [x] 运行 `python .\tools\run_openspec_guard.py --root . --tool codex --json`。
- [x] 运行 `git diff --check`。
