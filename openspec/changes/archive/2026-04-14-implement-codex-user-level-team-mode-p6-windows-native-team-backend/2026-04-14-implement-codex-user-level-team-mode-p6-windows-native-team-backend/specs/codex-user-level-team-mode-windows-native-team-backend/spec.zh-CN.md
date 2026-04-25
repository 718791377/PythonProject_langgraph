## ADDED Requirements

### Requirement: `omx team` SHALL 支持原生 Windows durable-team backend

durable-team runtime SHALL 支持一个不依赖 WSL2 或 Unix `tmux` 的原生 Windows backend。

#### Scenario: 在原生 Windows 下启动 durable execution team

- **WHEN** 操作员在原生 Windows 下运行 `omx team 2:team-executor "ship feature X"`
- **THEN** runtime SHALL 通过 Windows backend 启动该 team
- **AND** 它 SHALL 不会仅因为缺少 Unix `tmux` 而失败

### Requirement: 原生 Windows backend SHALL 保持 repo-local team state contract

原生 Windows backend SHALL 保持 `.omx/state/team/...` 下的同一套 repo-local state 布局。

至少 SHALL 保持：

- team manifest 与 config
- task files
- mailbox state
- worker identity
- worker heartbeat

#### Scenario: Windows 启动后读取 team state

- **WHEN** team 在原生 Windows 下被启动
- **THEN** repo-local `.omx/state/team/<team>/...` 合同 SHALL 仍可被现有 lifecycle 与 API 命令读取

### Requirement: 原生 Windows backend SHALL 支持生命周期对齐

原生 Windows backend SHALL 支持：

- `status`
- `await`
- `resume`
- `shutdown`

#### Scenario: 在原生 Windows 下有序关闭 team

- **WHEN** 操作员在原生 Windows 下运行 `omx team shutdown <team-name>`
- **THEN** runtime SHALL 有序停止 tracked workers
- **AND** 它 SHALL 把 team state 留在终态生命周期状态
