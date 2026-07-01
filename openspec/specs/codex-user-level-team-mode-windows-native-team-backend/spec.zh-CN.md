# codex-user-level-team-mode-windows-native-team-backend Specification

## 目的

定义 `omx team` 的原生 Windows durable-team backend 合同，使用户级 team mode 在不依赖 WSL2 的前提下可运行，同时保持 repo-local team state 与生命周期接口稳定。

## 要求

### Requirement: `omx team` SHALL 支持原生 Windows durable-team backend

durable-team runtime SHALL 支持一个不依赖 WSL2 或 Unix `tmux` 的原生 Windows backend。

#### Scenario: 在原生 Windows 上启动 durable execution team

- **WHEN** 操作员在原生 Windows 上运行 `omx team 2:team-executor "ship feature X"`
- **THEN** runtime SHALL 通过 Windows backend 启动该 team
- **AND** 它 SHALL 不会仅因为缺少 Unix `tmux` 而失败

### Requirement: 原生 Windows backend SHALL 保持 repo-local team state contract

原生 Windows backend SHALL 保持 `.omx/state/team/...` 下相同的 repo-local state 布局。

至少 SHALL 保持：

- team manifest 与 config
- task files
- mailbox state
- worker identity
- worker heartbeat

#### Scenario: Windows 启动后读取 team state

- **WHEN** team 在原生 Windows 上被启动
- **THEN** repo-local `.omx/state/team/<team>/...` 合同 SHALL 继续可被现有 lifecycle 与 API 命令读取

### Requirement: 原生 Windows backend SHALL 支持生命周期对齐

原生 Windows backend SHALL 支持：

- `status` - lifecycle action for reading team or backend state.
- `await` - lifecycle action for waiting until team work reaches a terminal state.
- `resume` - lifecycle action for continuing a paused or resumable team run.
- `shutdown` - lifecycle action for stopping a team safely.

#### Scenario: 在原生 Windows 上有序关闭 team

- **WHEN** 操作员在原生 Windows 上运行 `omx team shutdown <team-name>`
- **THEN** runtime SHALL 有序停止被跟踪的 workers
- **AND** 它 SHALL 将 team state 留在终态生命周期状态

### Requirement: Native OMX 必须区分 runtime backend 与 backend family

`native_omx` durable backend family SHALL 暴露用于运行态检查的具体 `runtime_backend`。

至少支持：

- `windows_prompt_process_controller`：Windows 原生默认后端。
- `unix_tmux`：Unix/tmux 实现后端。
- `unknown`：无法证明运行时后端。

#### Scenario: Windows 不把 tmux 当成 native_omx 本身

- **GIVEN** 操作者在没有 `tmux` 且不在 `tmux` 会话内的 native Windows 上
- **WHEN** worker-centric durable task 选择 `native_omx` backend family
- **THEN** runtime SHALL 评估 `windows_prompt_process_controller`
- **AND** SHALL NOT 把 `native_omx` 定义成只有 `unix_tmux`。

### Requirement: Windows 原生 operational preflight 必须显式

Native Windows `omx team` execution SHALL 在 launch/reuse 前报告 preflight 字段。

至少包含 `runtime_backend`、`preflight_passed`、`operational_ready`、`blockers`。

#### Scenario: 没有可启动的 Windows runtime backend

- **GIVEN** selected backend family 是 `native_omx`
- **AND** Windows prompt/process controller 与显式 Unix/tmux backend 都不能启动
- **WHEN** runtime 评估运行能力
- **THEN** SHALL 报告 `operational_ready=false`
- **AND** SHALL 包含 `blocked:windows_backend_not_implemented`、`blocked:tmux_only_backend` 或 `blocked:not_in_tmux_session` 等命名 blocker。
