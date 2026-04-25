## MODIFIED Requirements

### Requirement: 安装器 SHALL 生成用户级 OMX team entrypoint 资产

安装器 SHALL 继续在目标 Codex home 中生成 additive 的用户级 team entrypoint 资产。

这些生成 wrapper 在 native Windows 下 SHALL 继续可用，并且 SHALL NOT 再默认假设 Unix `tmux` 是唯一支持的执行 backend。

#### Scenario: 在 native Windows 下使用生成的 team entrypoint

- **WHEN** 操作员在 native Windows 下运行 `omx-team-dev.ps1` 这类生成 wrapper
- **THEN** 该 wrapper SHALL 继续有效
- **AND** 当 runtime 提供 Windows backend 时，它 SHALL 路由到受支持的 native Windows 执行 backend
