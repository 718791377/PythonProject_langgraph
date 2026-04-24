## MODIFIED Requirements

### Requirement: 安装器 SHALL 生成用户级 OMX team entrypoint 资产

安装器 SHALL 在目标 Codex home 中生成 additive 的用户级 team entrypoint 资产。

生成的资产集至少 SHALL 包含：

- `bin/omx-team-dev.ps1`
- `bin/omx-team-debug.ps1`
- `bin/omx-team-verify.ps1`
- `bin/omx-team-ops.ps1`
- `bin/omx-team-hybrid.ps1`
- `bin/omx-team-auto.ps1`
- `docs/team-mode-playbook.md`

#### Scenario: 在临时 Codex home 中生成 P2 加 P5 的 entrypoint 层

- **WHEN** 安装器针对显式目标 Codex home 运行
- **THEN** 它 SHALL 在该处生成手动与自动 team entrypoint wrapper
- **AND** 它 SHALL 保持这些新资产 additive-only

## ADDED Requirements

### Requirement: 自动 team helper SHALL 把阶段和工作量信号映射到已批准的 durable-team preset

`omx-team-auto.ps1` SHALL 接受显式的 phase 和 workload signal，并按以下方式解释：

- 早期阶段和最终验收阶段保持 subagent-only
- 执行与集成阶段在 parallel-slice 阈值满足时，映射到保守的 `team-executor` swarm
- 稳定化阶段在 blocking-issue 阈值满足时，映射到 `debugger` swarm

它 MAY 可选地执行该计划动作。

它 SHALL NOT 宣称每个自动决策都会变成 mixed persistent pane 拓扑。

#### Scenario: 自动 helper 在更宽并行执行时选择 `3:team-executor`

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 3 -Task "ship rollout X" -Json`
- **THEN** 它 SHALL 推导出等价于 `omx team 3:team-executor "ship rollout X"`

#### Scenario: 自动 helper 在稳定化阶段选择 `2:debugger`

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 1 -Task "stabilize regression X" -Json`
- **THEN** 它 SHALL 推导出等价于 `omx team 2:debugger "stabilize regression X"`
