## ADDED Requirements

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
