# Codex 用户级 Windows 清理输出控制

## Purpose

定义 scoped cleanup-output control，用于阻止 wrapped `codex-ohmy` 会话显示正常的 Windows `taskkill` 成功输出，同时保留 direct `omx_*` MCP 可用性和失败诊断。

## Requirements

### Requirement: Wrapped Codex launches SHALL suppress benign Windows cleanup success output

用户级 team-mode startup launcher 应为 wrapped `codex-ohmy` 启动安装并使用 scoped Windows cleanup-output control layer。

该 control layer 应抑制正常成功的 `taskkill` 输出，包括英文 `SUCCESS: The process with PID ... has been terminated.` 行，以及中文成功终止行，不让它们进入主 Codex 会话。

该 control layer 应保留非零 cleanup failure：把捕获到的失败输出转发到 stderr，并返回原始 exit code。

#### Scenario: `/resume` cleans up a temporary wrapped session

- **WHEN** 操作者启动 `codex-ohmy`，进入临时会话，然后使用 `/resume`
- **THEN** 临时会话的 Windows 子进程树成功 cleanup 时，不应把 `taskkill` 成功行打印进 resumed session
- **AND** cleanup control 不应要求禁用 `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace`

#### Scenario: Cleanup fails

- **WHEN** cleanup shim 调用真实 Windows `taskkill.exe` 并收到非零 exit code
- **THEN** 它应返回相同的非零 exit code
- **AND** 它应把捕获到的诊断输出转发到 stderr

### Requirement: Cleanup-output control SHALL be scoped to wrapped launches

startup launcher 应只在 wrapped launch 的 native Codex 子进程树中暴露 cleanup-output control。

launcher 应在 native Codex 命令退出后恢复之前的 PATH。

仓库实现不得通过修改 `C:\Users\lenovo\.codex\config.toml` 来启用该 control。

#### Scenario: Wrapped launch starts

- **WHEN** `codex-ohmy` 调用 native Codex 命令
- **THEN** 生成的 `win-shims` 目录应为该子进程树前置到 PATH
- **AND** native 命令返回后应恢复原始 PATH

#### Scenario: Native bypass starts

- **WHEN** 操作者直接运行 `codex-raw`、`codex-native` 或 native `codex` executable
- **THEN** 该 bypass 路径不应要求 cleanup-output control layer
- **AND** bypass 应保持不受 wrapper-specific PATH mutation 影响

### Requirement: Cleanup-output control SHALL preserve direct `omx_*` MCP availability

当 `oh_my_codex=on` 时，wrapped launcher 应继续为 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 启用 direct Codex MCP entries。

#### Scenario: Full wrapped mode starts

- **WHEN** wrapped launcher 以 `oh_my_codex=on` 计算 startup arguments
- **THEN** 它应传入 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 的 enabled overrides
- **AND** 它也应启用 cleanup-output control layer

### Requirement: Cleanup-output control SHALL have script-backed validation

仓库应包含一个可执行 checker，用于验证 cleanup-output control source contract。

当 installer 不再生成 scoped shim，或 wrapped launcher 不再应用 scoped PATH control 时，该 checker 应失败。

#### Scenario: Repository checker runs

- **WHEN** 操作者运行 cleanup-output control checker
- **THEN** 它应验证 installer 会生成 `win-shims` cleanup artifacts
- **AND** 它应验证 wrapped launch 在调用 native Codex 后会恢复 PATH
- **AND** 它应验证 full wrapped mode 中 `omx_*` MCP startup overrides 仍保持 enabled

### Requirement: Wrapped cleanup-output control SHALL cover explicit taskkill.exe paths by default

用户级 installer 默认应为 wrapped `codex-ohmy` 启动请求 explicit `taskkill.exe` cleanup-output shim。

生成的 launcher 只有在运行时确实存在生成的 `win-shims\taskkill.exe` 文件时，才应在 `PATHEXT` 中优先 `.EXE`。如果该 executable shim 不可用，launcher 应回退到现有 `.CMD` shim，且不应破坏 wrapped launch。

installer 应提供显式 opt-out 开关，用于不能或不应编译 executable shim 的环境。

#### Scenario: Default install can intercept explicit taskkill.exe cleanup

- **WHEN** installer 能够编译生成的 `taskkill.exe` shim
- **THEN** wrapped launcher 应把 `win-shims` 目录前置到 PATH
- **AND** 它应在该 wrapped 子进程树的 `PATHEXT` 中优先 `.EXE`
- **AND** successful explicit `taskkill.exe` cleanup output 应由 shim 抑制

#### Scenario: Executable shim is unavailable

- **WHEN** 已请求 executable shim，但运行时不存在该 shim
- **THEN** wrapped launcher 不应优先 `.EXE`
- **AND** 它应保持现有 `.CMD` fallback cleanup-output control active
- **AND** wrapped Codex launch 不应仅因为 executable shim 不可用而失败

#### Scenario: Operator explicitly opts out

- **WHEN** installer 使用显式 opt-out 开关运行
- **THEN** 它不应创建 `win-shims\taskkill.exe`
- **AND** wrapped launcher 不应优先 `.EXE`
- **AND** 现有 `.CMD` 和 `.ps1` cleanup shims 应继续安装