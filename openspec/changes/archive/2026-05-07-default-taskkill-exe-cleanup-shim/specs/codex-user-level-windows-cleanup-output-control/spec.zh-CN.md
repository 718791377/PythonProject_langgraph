## ADDED Requirements

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

用户级 installer 默认应为 wrapped `codex-ohmy` 启动请求 explicit `taskkill.exe` 清理输出 shim。

生成的 launcher 只有在运行时确实存在生成的 `win-shims\taskkill.exe` 文件时，才应在 `PATHEXT` 中优先 `.EXE`。如果这个可执行 shim 不可用，launcher 应回退到现有 `.CMD` shim，且不能破坏 wrapped 启动。

installer 应提供显式 opt-out 开关，用于不能或不应编译可执行 shim 的环境。

#### Scenario: Default install can intercept explicit taskkill.exe cleanup

- **WHEN** installer 能够编译生成的 `taskkill.exe` shim
- **THEN** wrapped launcher 应把 `win-shims` 目录前置到 PATH
- **AND** 应在该 wrapped 子进程树的 `PATHEXT` 中优先 `.EXE`
- **AND** explicit `taskkill.exe` 成功清理输出应由 shim 抑制

#### Scenario: Executable shim is unavailable

- **WHEN** 已请求可执行 shim，但运行时不存在该 shim
- **THEN** wrapped launcher 不应优先 `.EXE`
- **AND** 应保留现有 `.CMD` fallback 清理输出控制
- **AND** wrapped Codex 启动不应仅因为可执行 shim 不可用而失败

#### Scenario: Operator explicitly opts out

- **WHEN** 使用显式 opt-out 开关运行 installer
- **THEN** 不应创建 `win-shims\taskkill.exe`
- **AND** wrapped launcher 不应优先 `.EXE`
- **AND** 现有 `.CMD` 和 `.ps1` 清理 shim 应继续安装