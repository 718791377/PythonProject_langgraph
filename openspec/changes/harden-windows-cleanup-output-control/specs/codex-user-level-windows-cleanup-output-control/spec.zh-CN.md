## ADDED Requirements

### Requirement: Cleanup-output control SHALL support opt-in taskkill executable interception

用户级 team-mode installer SHALL 提供显式 opt-in 开关，用于在 cleanup 调用方绕过默认 `taskkill.cmd` shim 时安装已编译的 `taskkill.exe` shim。team-mode installer 是生成用户级 wrapper 和 helper assets 的安装脚本。

installer SHALL NOT 默认安装或启用已编译的 `taskkill.exe` shim。

使用 opt-in 开关时，installer SHALL 从仓库托管源码编译 shim，把它写入生成的 `win-shims` 目录，并报告是否尝试和完成编译。`win-shims` 是 wrapped launch 临时放入 PATH 前面的 shim 目录。

#### Scenario: Default installation keeps executable interception disabled

- **WHEN** installer 在没有显式 EXE shim 开关的情况下运行
- **THEN** 生成的 startup binding SHALL 报告 `taskkill_exe_shim_enabled=false`
- **AND** wrapped launch SHALL NOT 在既有 PATHEXT 顺序前优先 `.EXE`

#### Scenario: Explicit executable interception is installed

- **WHEN** installer 使用显式 EXE shim 开关运行
- **THEN** installer SHALL 把 `taskkill-shim-source.cs` 编译为 `win-shims\taskkill.exe`
- **AND** 生成的 startup binding SHALL 报告 `taskkill_exe_shim_enabled=true`
- **AND** wrapped launch SHALL 在 wrapped child process tree 内优先 `.EXE`

#### Scenario: Explicit executable interception cannot be compiled

- **WHEN** installer 使用显式 EXE shim 开关运行
- **AND** 没有可用的 C# compiler
- **THEN** installation SHALL 用诊断原因失败
- **AND** managed-install rollback path SHALL 恢复之前的托管状态

### Requirement: Cleanup-output checker SHALL guard optional executable hardening

仓库 cleanup-output checker SHALL 验证 installer source 包含 optional executable shim switch、compile function、scoped launcher flag 和 JSON report fields。cleanup-output checker 是仓库内验证清理输出控制合同的脚本。

#### Scenario: Optional executable hardening source is removed

- **WHEN** cleanup-output checker 针对不再暴露 optional executable shim switch 的 installer source 运行
- **THEN** checker SHALL 失败
- **AND** checker output SHALL 标识缺失的 executable-hardening marker
