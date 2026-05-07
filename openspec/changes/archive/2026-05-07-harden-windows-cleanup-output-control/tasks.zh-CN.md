# Tasks

## 1. Plan and OpenSpec Artifacts

- [x] 1.1 更新 `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.md`，这是记录 Windows cleanup-output hardening 范围的英文 implementation plan。
- [x] 1.2 更新 `docs_bilingual/implementation_plans/omx_mcp_windows_cleanup_output_control_plan.zh-CN.md`，这是同一 cleanup-output hardening 范围的中文对照 implementation plan。
- [x] 1.3 创建 `openspec/changes/harden-windows-cleanup-output-control/proposal.md`，这是记录为什么需要本次硬化的 OpenSpec proposal。
- [x] 1.4 创建 `openspec/changes/harden-windows-cleanup-output-control/design.md`，这是记录 optional EXE shimming 如何保持受限和 opt-in 的 OpenSpec design。
- [x] 1.5 创建 `openspec/changes/harden-windows-cleanup-output-control/specs/codex-user-level-windows-cleanup-output-control/spec.md`，这是 cleanup-output control capability 的 delta spec。

## 2. Installer and Checker Implementation

- [x] 2.1 更新 `tools/install-codex-user-level-team-mode.ps1`，这是用户级 team-mode installer，用来增加 `InstallTaskkillExeShim` opt-in 开关。
- [x] 2.2 更新 `tools/install-codex-user-level-team-mode.ps1`，让显式 opt-in 把 `taskkill-shim-source.cs` 这个托管 C# shim 源码编译为 `win-shims\taskkill.exe`。
- [x] 2.3 更新生成的 startup launcher logic，让 `.EXE` PATHEXT 优先级只在 optional EXE shim 已安装时启用。
- [x] 2.4 更新 installer JSON 输出，让 `taskkill_exe_shim_enabled`、`taskkill_exe_shim_path` 和 `taskkill_exe_shim_compile` 描述 optional EXE shim 状态。
- [x] 2.5 更新 `tools/check_windows_cleanup_output_control.py`，这是 cleanup-output checker，用来守护 optional executable hardening markers。

## 3. Tests and Validation

- [x] 3.1 更新 `test/check_windows_cleanup_output_control.test.py`，这是 cleanup-output checker test，用来在 optional executable hardening markers 被移除时失败。
- [x] 3.2 更新 `test/install-codex-user-level-team-mode.test.ps1`，这是 installer behavior test，用来验证默认 EXE interception 保持禁用。
- [x] 3.3 更新 `test/install-codex-user-level-team-mode.test.ps1`，验证显式 `InstallTaskkillExeShim` opt-in 创建 `win-shims\taskkill.exe` 并限定 `.EXE` PATHEXT 优先级作用域。
- [x] 3.4 运行 `python test/check_windows_cleanup_output_control.test.py`，这是 cleanup-output control 的 checker unit test 命令。
- [x] 3.5 运行 `powershell -NoProfile -ExecutionPolicy Bypass -File test/install-codex-user-level-team-mode.test.ps1`，这是生成用户级 assets 的 installer integration test 命令。
- [x] 3.6 运行 `python tools/check_windows_cleanup_output_control.py --root . --json`，这是直接运行 cleanup-output checker 的命令。
- [x] 3.7 运行 `openspec validate --all`，这是验证全部 specs 和 changes 的 OpenSpec validation 命令。
- [x] 3.8 运行 `python tools/run_openspec_guard.py --root . --tool codex --json`，这是仓库 guard 命令。
- [x] 3.9 运行 `git diff --check`，这是补丁空白格式验证命令。
