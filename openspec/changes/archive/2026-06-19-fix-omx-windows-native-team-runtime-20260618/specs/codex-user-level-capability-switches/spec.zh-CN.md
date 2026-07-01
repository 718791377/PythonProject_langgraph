## ADDED Requirements

### Requirement: Capability readiness 不得被当作 operational launchability

Capability readiness records SHALL 区分 installed、enabled、selected、ready 和 operational readiness。

#### Scenario: Native OMX selected 但 runtime evidence 缺失

- **GIVEN** `native_omx` installed、enabled、selected
- **AND** 没有可启动的 Windows runtime backend 或显式 Unix/tmux runtime evidence
- **WHEN** readiness 被投影
- **THEN** projection SHALL NOT 声称具备 operational launchability
- **AND** SHALL 暴露 `blocked:runtime_backend_unavailable`、`blocked:tmux_only_backend` 或 `blocked:not_in_tmux_session` 等 blocker。

### Requirement: Readiness projection 必须显式保留非启动 smoke evidence

Readiness projection receipts SHALL 标明 backend 只是 inspect 还是实际 launch。

#### Scenario: Readiness refresh 未启动团队

- **WHEN** durable readiness projection 被刷新
- **THEN** receipt SHALL 保留 `durable_workflow_adopted=false` 和 `persistent_team_launched=false`，除非真实 launch 已发生
- **AND** SHALL NOT 把 wrapper 生成或 selector 存在当成 launch receipt。
