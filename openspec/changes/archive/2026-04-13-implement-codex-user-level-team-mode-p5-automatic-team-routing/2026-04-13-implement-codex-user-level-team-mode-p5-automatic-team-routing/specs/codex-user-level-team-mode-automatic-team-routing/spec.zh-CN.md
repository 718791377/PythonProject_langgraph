## ADDED Requirements

### Requirement: 安装器 SHALL 生成自动 durable-team 路由 helper

安装器 SHALL 在目标 Codex home 中生成 additive 的用户级 durable-team routing helper。

生成的资产集 SHALL 包含：

- `bin/omx-team-auto.ps1`

该 helper SHALL 保持 additive-only，并且 SHALL 调用解析后的原生 `omx` 命令路径，而不是替换原生可执行文件。

#### Scenario: 在临时 Codex home 中生成 P5 helper

- **WHEN** 安装器针对显式目标 Codex home 运行
- **THEN** 它 SHALL 生成 `bin/omx-team-auto.ps1`
- **AND** 它 SHALL 将该 helper 纳入现有备份与回滚事务

### Requirement: helper SHALL 在变更前输出可检查的 automatic durable-team routing plan

`omx-team-auto.ps1` SHALL 在修改状态前输出结构化 routing plan。

该 plan 至少 SHALL 包含：

- 当前 mode 与 capability flags
- 请求的 phase
- 目标 durable team 形状（如果有）
- tracked team record（如果有）
- 决策结果：`no-team`、`launch`、`reuse`、`switch`、`shutdown`、`manual-inspection-required`

#### Scenario: `execute-parallel` planning 选择保守 worker swarm

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Task "implement rollout X" -Json`
- **THEN** 它 SHALL 报告一个 durable-team 决策
- **AND** 它 SHALL 推导出等价于 `2:team-executor`

#### Scenario: `verify-accept` planning 不保留 durable team

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase verify-accept -Task "final sign-off" -Json`
- **THEN** 它 SHALL 返回 no-team 或 shutdown 类决策
- **AND** 它 SHALL 不推导新的 durable worker 启动

### Requirement: 自动路由 SHALL 只管理 tracked 的 repo-local team

helper SHALL 使用以下仓库级 tracked-team record：

- `.omx/state/team/codex-auto-managed-team.json`

只有 tracked record 存在，并且记录中的 team 仍存在于当前仓库 team state root 中时，helper 才 SHALL 自动管理该 team。

helper 默认 SHALL NOT 自动接管 unmanaged 的既有 team。

#### Scenario: 已有 unmanaged team 不会被自动接管

- **WHEN** 仓库里存在最新 team 目录，但没有 tracked-team record
- **THEN** helper SHALL 返回 `manual-inspection-required` 或等价的安全非变更决策
- **AND** 它 SHALL 不自动 shutdown、reuse 或 switch 该 unmanaged team

### Requirement: Apply 模式 SHALL 支持 launch、reuse、switch、shutdown

显式带 `-Apply` 时，helper SHALL 通过原生 `omx` CLI 执行 durable-team 变更。

至少包括：

- `launch` SHALL 调用 `omx team <workerspec> "<task>"`
- `reuse` SHALL 调用 `omx team api create-task`
- `switch` SHALL 先 shutdown tracked team，再启动新的目标 team
- `shutdown` SHALL shutdown tracked team 并清除 tracked-team record

#### Scenario: `reuse` 将任务派发给 tracked team

- **WHEN** tracked team 与期望 worker role 和 worker count 匹配
- **AND** 操作员运行 `omx-team-auto.ps1 -Apply`
- **THEN** helper SHALL 通过 `omx team api create-task` 派发新任务
- **AND** 它 SHALL 保留 tracked-team record

#### Scenario: phase 变化触发 debug-team 切换

- **WHEN** tracked team 当前是 development swarm
- **AND** 操作员运行 `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 2 -Apply`
- **THEN** helper SHALL 先 shutdown tracked development swarm
- **AND** 它 SHALL 启动等价于 `omx team 2:debugger "<task>"`
- **AND** 它 SHALL 更新 tracked-team record
