## ADDED Requirements

### Requirement: 安装器必须生成一个 PowerShell 启动绑定 launcher

安装器必须生成一个 launcher 脚本，读取持久化的用户级 team-mode 状态，并为 PowerShell 型 `codex` 启动计算 Codex CLI 运行时覆盖参数。

这个 launcher 必须保留原生 Codex 可执行文件路径，而不是替换它。

#### Scenario: startup-binding 资产被生成到目标 Codex home

- **WHEN** 安装器执行 startup binding 安装
- **THEN** 它必须在目标 Codex home 下生成一个 launcher 资产
- **AND** 这个 launcher 必须知道如何在不递归的情况下调用原生 Codex 命令路径

### Requirement: 安装器必须添加一个托管的 PowerShell profile block，且不能替换原生可执行文件

安装器必须向选定的 PowerShell profile 路径添加一个托管 block，定义包装后的 `codex` 函数和原始 `codex-native` bypass 函数。

它不得修改 npm 安装的 `codex`、`codex.cmd`、`codex.ps1` 文件。

#### Scenario: 新 PowerShell 会话加载启动绑定

- **WHEN** PowerShell 会话加载了托管 profile block
- **THEN** 调用 `codex` 必须路由到生成的 launcher
- **AND** 调用 `codex-native` 必须直接路由到原生 Codex 命令
- **AND** 原生 Codex 安装文件必须保持不变

### Requirement: launcher 必须把 `oh_my_codex` 状态映射到启动行为

launcher 必须从持久化状态文件读取 `oh_my_codex`，并把它映射到 Codex CLI 的运行时覆盖行为。

至少需要满足：

- `oh_my_codex=on` 时保持 omx 启动行为启用
- `oh_my_codex=off` 时，对包装后的启动禁用 omx 相关启动行为

#### Scenario: 当 omx 关闭时，包装后的启动运行在 native 模式

- **WHEN** 包装后的 `codex` 启动看到 `oh_my_codex=off`
- **THEN** 它必须为本次启动禁用 omx 相关 MCP 启动面
- **AND** 它必须为本次启动使用 native-mode developer-instruction 预设

### Requirement: launcher 必须把 `subagent_routing` 状态映射到 multi-agent 可用性

launcher 必须从持久化状态文件读取 `subagent_routing`，并把它映射到 Codex CLI 的路由行为。

至少需要满足：

- `auto` 时保持 multi-agent 可用，并使用自动路由说明
- `manual` 时保持 multi-agent 可用，并使用手动路由说明
- `off` 时对包装后的启动禁用 multi-agent

#### Scenario: 在 no-routing 模式下，包装后的启动会禁用 multi-agent

- **WHEN** 包装后的 `codex` 启动看到 `subagent_routing=off`
- **THEN** 它必须传递等价于 `--disable multi_agent` 的效果
- **AND** 它必须使用 no-routing developer-instruction 预设

### Requirement: startup-binding 安装必须被备份快照与回滚覆盖

安装器必须把 PowerShell profile 路径与 startup-binding launcher 资产纳入同一个时间戳备份与回滚事务。

#### Scenario: 部分失败的 startup-binding 安装会恢复之前的 profile 内容

- **WHEN** startup-binding 安装在 profile 或 launcher 写入开始后失败
- **THEN** 安装器必须恢复安装前的 PowerShell profile 内容
- **AND** 它必须把 startup-binding 资产恢复或删除到安装前状态
- **AND** 它必须保留备份元数据用于诊断
