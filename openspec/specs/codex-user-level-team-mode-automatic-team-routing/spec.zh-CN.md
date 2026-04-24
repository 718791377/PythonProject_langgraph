# codex-user-level-team-mode-automatic-team-routing Specification

## 目的

TBD - 由归档变更 `implement-codex-user-level-team-mode-p5-automatic-team-routing` 时创建。归档后补全 Purpose。

## 要求

### Requirement: 安装器 SHALL 生成 automatic durable-team routing helper

安装器 SHALL 在目标 Codex home 中生成一个附加式的用户级 durable-team routing helper。

生成的资产至少 SHALL 包含：

- `bin/omx-team-auto.ps1`

该 helper SHALL 保持 additive-only，并且 SHALL 调用解析后的原生 `omx` 命令路径，而不是替换原生可执行文件。

#### Scenario: 在临时 Codex home 中生成 P5 helper

- **WHEN** 安装器针对一个显式目标 Codex home 运行
- **THEN** 它 SHALL 生成 `bin/omx-team-auto.ps1`
- **AND** 它 SHALL 让该 helper 继续处于现有备份与回滚事务中

### Requirement: helper SHALL 输出可检查的 automatic durable-team routing plan

`omx-team-auto.ps1` SHALL 在真正修改状态之前输出结构化 routing plan。

该 plan 至少 SHALL 包含：

- 当前 mode 与 capability flags
- 请求的 phase
- 期望的 durable team 形态（如果有）
- 已跟踪的 team record（如果有）
- 决策：`no-team`、`launch`、`reuse`、`switch`、`shutdown` 或 `manual-inspection-required`

#### Scenario: execute-parallel planning 选择保守 worker swarm

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Task "implement rollout X" -Json`
- **THEN** 它 SHALL 报告一个 durable-team 决策
- **AND** 它 SHALL 推导出等价于 `2:team-executor` 的团队形态

#### Scenario: verify-accept planning 不保留 durable team

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase verify-accept -Task "final sign-off" -Json`
- **THEN** 它 SHALL 返回 `no-team` 或 `shutdown` 类决策
- **AND** 它 SHALL 不推导新的 durable worker launch

### Requirement: automatic routing SHALL 只管理被跟踪的 repo-local teams

该 helper SHALL 使用如下 repo-local tracked-team record：

- `.omx/state/team/codex-auto-managed-team.json`

只有当 tracked record 存在，且记录中的 team 在当前仓库 team state root 中仍然存在时，helper 才 SHALL 自动管理该 team。

默认情况下，它 SHALL NOT 自动接管一个未托管的既有 team。

#### Scenario: 未托管的现有 team 不会被自动接管

- **WHEN** 仓库中存在最新 team 目录，但不存在 tracked-team record
- **THEN** helper SHALL 返回 `manual-inspection-required` 或等价的安全非变更决策
- **AND** 它 SHALL NOT 自动 shutdown、reuse 或 switch 那个未托管 team

### Requirement: Apply mode SHALL 支持 launch、reuse、switch 与 shutdown

当显式提供 `-Apply` 时，helper SHALL 通过原生 `omx` CLI 执行计划中的 durable-team 变更。

至少：

- `launch` SHALL 调用 `omx team <workerspec> "<task>"`
- `reuse` SHALL 调用 `omx team api create-task`
- `switch` SHALL 关闭被跟踪 team，并启动新的目标 team
- `shutdown` SHALL 关闭被跟踪 team，并清除 tracked-team record

在原生 Windows 上，这 SHALL 表示使用受支持的原生 Windows backend，而不是硬依赖 Unix `tmux`。

#### Scenario: reuse 将工作派发到 tracked team

- **WHEN** 被跟踪 team 与期望的 worker role 和 worker count 匹配
- **AND** 操作员运行 `omx-team-auto.ps1 -Apply`
- **THEN** helper SHALL 通过 `omx team api create-task` 路由新任务
- **AND** 它 SHALL 保留 tracked-team record

#### Scenario: phase 变化触发 debug-team switch

- **WHEN** 当前被跟踪 team 是 development swarm
- **AND** 操作员运行 `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 2 -Apply`
- **THEN** helper SHALL 关闭该 development swarm
- **AND** 它 SHALL 启动等价于 `omx team 2:debugger "<task>"` 的 team
- **AND** 它 SHALL 更新 tracked-team record

#### Scenario: `omx-team-auto.ps1 -Apply` 在原生 Windows 上通过 P6 backend 启动 team

- **WHEN** 操作员在原生 Windows 上运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 2 -Apply`
- **THEN** helper SHALL 能通过 Windows backend 执行 launch
- **AND** 它 SHALL 继续保持 tracked-team record 合同

### Requirement: automatic durable routing 必须从已启用 capability 中按任务流选择 effective lane

automatic durable routing 必须从当前已启用的 orchestration capability set 中，按每条任务流选择 effective lane。

当任务流更适合另一条已启用 lane 时，不应要求 operator 先做一次全局 backend-family 切换。

#### Scenario: LangGraph 已启用时，worker-centric 任务流仍选择 native_omx

- **WHEN** 分层 capability set 同时启用了 oh-my-codex durable features 与 LangGraph
- **AND** 当前任务流更适合 worker-centric durable execution
- **THEN** automatic durable routing 层必须把 `native_omx` 选为 effective lane
- **AND** 不应要求先全局关闭 LangGraph capability
