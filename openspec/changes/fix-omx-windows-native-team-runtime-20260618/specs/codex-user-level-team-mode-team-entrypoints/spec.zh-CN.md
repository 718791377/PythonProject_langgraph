## ADDED Requirements

### Requirement: Automatic team Apply 在 operational preflight 失败时必须 fail closed

`omx-team-auto.ps1 -Apply` SHALL 在修改 tracked team state 或 active selector 前执行 operational preflight。

#### Scenario: Windows 上 native OMX preflight 失败

- **GIVEN** automatic helper 计划在 Windows 上启动 `native_omx` worker team
- **AND** runtime backend preflight 返回 `operational_ready=false`
- **WHEN** 操作者运行 `omx-team-auto.ps1 -Apply -Json`
- **THEN** helper SHALL 返回结构化 blocked 结果
- **AND** SHALL NOT 创建或更新 `.omx/state/team/codex-auto-managed-team.json`
- **AND** SHALL NOT 写入表示 team running 的 active native selector。

### Requirement: Automatic team output 必须暴露 runtime backend evidence

automatic team helper SHALL 在 plan 与 apply 输出中包含 runtime backend evidence。

#### Scenario: 操作者检查 automatic plan 输出

- **WHEN** 操作者运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Json`
- **THEN** 输出 SHALL 包含 `runtime_backend`、`preflight_passed`、`operational_ready`、`blockers`
- **AND** wrapper 存在本身 SHALL NOT 被报告为 launch evidence。
