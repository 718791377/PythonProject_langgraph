## Why

wrapped `codex-ohmy` 会话在 `/resume` 或 subagent 清理之后，仍可能泄漏 `SUCCESS: The process with PID ... has been terminated.` 这类 Windows 正常清理输出。当前清理输出控制已经安装 `taskkill.cmd` 和 `taskkill.ps1`，但显式 `taskkill.exe` shim 仍是可选项，当前用户级 helper 没有安装它。凡是直接调用 `taskkill.exe` 的清理路径，都可能绕过 scoped shim。

## What Changes

- 默认尝试安装 `taskkill.exe` 清理 shim，同时保留兼容性显式启用开关，并新增显式跳过开关。
- wrapped launcher 只有在生成的 `taskkill.exe` shim 存在时才优先使用 `.EXE` 清理 shim；否则回退到现有 `.CMD` shim。
- native bypass 不引入 wrapper 专属的 PATH/PATHEXT 变更。
- 补强 checker 和测试，防止后续改动静默退化 explicit `taskkill.exe` 输出控制。

## Capabilities

### New Capabilities

- 无。

### Modified Capabilities

- `codex-user-level-windows-cleanup-output-control`：补强 explicit `taskkill.exe` 调用路径的清理输出控制。

## Impact

- impact_scope：用户级 installer 源码、清理输出 checker、installer 测试、checker 测试，以及本 OpenSpec change。
- explicit_non_goals：不修改 `C:\Users\lenovo\.codex\config.toml`，不改 MCP Router，不禁用 `omx_*` MCP，不启动 durable team，不写入仓库 durable state。
- rollout_sequence：先实现源码补强，本地验证通过后如 change 已完成则归档到 stable spec，再按 GitLab-first MR 发布，合并后刷新用户级 helper。
- rollback_plan：回滚本 change，并重新运行 installer，恢复之前仅 `.cmd` / `.ps1` 的清理控制。
- validation_path：运行清理输出 checker、checker 单测、installer PowerShell 测试、`openspec validate --all`、`python .\tools\run_openspec_guard.py --root . --tool codex --json`、`git diff --check`。