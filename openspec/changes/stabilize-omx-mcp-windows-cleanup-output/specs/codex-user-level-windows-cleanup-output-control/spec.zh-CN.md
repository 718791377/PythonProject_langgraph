## ADDED Requirements

### Requirement: Wrapped Codex launch 必须抑制正常 Windows cleanup 成功输出

用户级 team-mode startup launcher 必须为 wrapped `codex-ohmy` launch 安装并使用 scoped Windows cleanup-output control layer。

control layer 必须从主 Codex 会话中抑制正常成功的 `taskkill` 输出，包括英文 `SUCCESS: The process with PID ... has been terminated.` 行和中文“成功: 已终止 PID ... 的进程。”行。

control layer 必须保留非零 cleanup 失败：它必须把捕获的失败输出转发到 stderr，并返回原始退出码。

#### Scenario: `/resume` 清理临时 wrapped session

- **WHEN** 操作者启动 `codex-ohmy`，进入临时会话，然后使用 `/resume`
- **THEN** 临时会话 Windows 子进程树的成功 cleanup 不得把 `taskkill` 成功行打印进恢复后的会话
- **AND** cleanup control 不得要求禁用 `omx_state`、`omx_memory`、`omx_code_intel` 或 `omx_trace`

#### Scenario: Cleanup 失败

- **WHEN** cleanup shim 调用真实 Windows `taskkill.exe` 并收到非零退出码
- **THEN** 它必须返回同一个非零退出码
- **AND** 它必须把捕获的诊断输出转发到 stderr

### Requirement: Cleanup-output control 必须限定在 wrapped launch

startup launcher 必须只在 wrapped launch 中让 cleanup-output control 对 native Codex 子进程树可见。

launcher 必须在 native Codex 命令退出后恢复之前的 PATH。

仓库实现不得通过修改 `C:\Users\lenovo\.codex\config.toml` 来启用该控制。该文件是用户级 Codex 配置文件。

#### Scenario: Wrapped launch 启动

- **WHEN** `codex-ohmy` 调用 native Codex 命令
- **THEN** 生成的 `win-shims` 目录必须被放到该子进程树的 PATH 前面
- **AND** native 命令返回后必须恢复原始 PATH

#### Scenario: Native bypass 启动

- **WHEN** 操作者直接运行 `codex-raw`、`codex-native` 或 native `codex` executable
- **THEN** bypass 路径不需要 cleanup-output control layer
- **AND** bypass 必须不受 wrapper-specific PATH mutation 影响

### Requirement: Cleanup-output control 必须保留 direct `omx_*` MCP 可用性

当 `oh_my_codex=on` 时，wrapped launcher 必须继续为 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 启用 direct Codex MCP entries。

#### Scenario: Full wrapped mode 启动

- **WHEN** wrapped launcher 在 `oh_my_codex=on` 状态下计算 startup arguments
- **THEN** 它必须传入 `omx_state`、`omx_memory`、`omx_code_intel` 和 `omx_trace` 的 enabled overrides
- **AND** 它也必须启用 cleanup-output control layer

### Requirement: Cleanup-output control 必须有脚本化验证

仓库必须包含一个可执行 checker，用于验证 cleanup-output control 源码合同。

当安装器不再生成 scoped shim，或 wrapped launcher 不再应用 scoped PATH control 时，该 checker 必须失败。

#### Scenario: 仓库 checker 运行

- **WHEN** 操作者运行 cleanup-output control checker
- **THEN** 它必须验证安装器会生成 `win-shims` cleanup artifacts
- **AND** 它必须验证 wrapped launch 会在调用 native Codex 后恢复 PATH
- **AND** 它必须验证 full wrapped mode 中 `omx_*` MCP startup overrides 仍保持启用
