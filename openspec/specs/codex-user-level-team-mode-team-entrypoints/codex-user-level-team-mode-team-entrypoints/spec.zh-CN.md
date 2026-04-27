# codex-user-level-team-mode-team-entrypoints Specification

## 目的

TBD - 本文件由归档变更 `implement-codex-user-level-team-mode-p2-team-entrypoints` 时创建。归档后请补全 Purpose。

## 要求

### Requirement: 安装器 SHALL 生成用户级 OMX team entrypoint assets

安装器 SHALL 向目标 Codex home 生成 additive 的用户级 team entrypoint assets。

生成的 wrappers 在原生 Windows 上 SHALL 保持可用，并且 SHALL NOT 假设 Unix `tmux` 是唯一受支持的执行 backend。

生成资产集合至少 SHALL 包含：

- `bin/omx-team-dev.ps1` - 默认开发 durable team 的用户级 launcher。
- `bin/omx-team-debug.ps1` - debugger-focused durable team 的用户级 launcher。
- `bin/omx-team-verify.ps1` - 输出 leader-side verification plan 的用户级 wrapper。
- `bin/omx-team-ops.ps1` - 面向 team lifecycle 和安全只读 API 操作的用户级 wrapper。
- `bin/omx-team-hybrid.ps1` - 把 heterogeneous staffing request 转接到 leader-side experts 加一个 worker team 的用户级 bridge。
- `bin/omx-team-auto.ps1` - 执行 threshold-gated automatic durable-team routing 的用户级 launcher。
- `docs/team-mode-playbook.md` - 记录 team-mode 用法和操作规则的生成 playbook。

#### Scenario: 在临时 Codex home 中生成 P2 与 P5 entrypoint 层

- **WHEN** 安装器针对一个显式目标 Codex home 运行
- **THEN** 它 SHALL 在该目标中生成手动与自动 team entrypoint wrappers
- **AND** 它 SHALL 保持这些新资产为 additive-only

#### Scenario: 在 P6 之后于原生 Windows 使用生成的 team entrypoint

- **WHEN** 操作员在原生 Windows 上运行 `omx-team-dev.ps1` 之类的生成 wrapper
- **THEN** 该 wrapper SHALL 保持有效
- **AND** 当 runtime 提供 Windows backend 时，它 SHALL 路由到受支持的原生 Windows 执行 backend

### Requirement: 生成的 wrappers SHALL 调用已解析的原生 OMX 命令路径

安装器 SHALL 解析原生 `omx` 命令路径，或接受显式 override；生成的 wrappers SHALL 直接调用该已解析路径。

安装器 SHALL NOT 替换或覆盖原生 `omx` 可执行文件。

#### Scenario: 测试安装使用 fake OMX target

- **WHEN** 安装器在显式 fake `omx` 命令路径下运行
- **THEN** 生成的 wrappers SHALL 调用该 fake 命令路径
- **AND** wrapper 行为 SHALL 在不修改真实用户安装的前提下保持可测试

### Requirement: development 与 debug wrappers SHALL 编码已批准的 durable-team 默认值

`omx-team-dev.ps1` SHALL 编码一个 durable development-team preset。

至少包括：

- 默认 worker 数量：`2`
- 默认 worker 角色：`team-executor`
- 可选 override 到 `executor`

`omx-team-debug.ps1` SHALL 编码一个 durable debug-team preset。

至少包括：

- 默认 worker 数量：`2`
- 默认 worker 角色：`debugger`

#### Scenario: development wrapper 启动保守 worker swarm

- **WHEN** 操作员运行 `omx-team-dev.ps1 -Task "ship feature X"`
- **THEN** 它 SHALL 调用等价于 `omx team 2:team-executor "ship feature X"` 的命令

#### Scenario: debug wrapper 启动 debugger swarm

- **WHEN** 操作员运行 `omx-team-debug.ps1 -Task "stabilize regression X"`
- **THEN** 它 SHALL 调用等价于 `omx team 2:debugger "stabilize regression X"` 的命令

### Requirement: ops wrapper SHALL 暴露受支持的 team lifecycle 与安全只读的 team inspection surface

`omx-team-ops.ps1` SHALL 包装以下受支持的 lifecycle commands：

- `status` - 读取 team state 的 lifecycle action。
- `await` - 等待 team work 到达终止状态的 lifecycle action。
- `resume` - 继续 paused 或 resumable team run 的 lifecycle action。
- `shutdown` - 安全停止 team 的 lifecycle action。

它也 SHALL 支持安全只读的 team API 操作，例如：

- `list-tasks` - 读取 team tasks 的只读 API operation。
- `mailbox-list` - 读取 worker mailbox messages 的只读 API operation。
- `get-summary` - 读取 team summary 的只读 API operation。
- `read-manifest` - 读取 team manifest 的只读 API operation。

#### Scenario: ops wrapper 显示 team status

- **WHEN** 操作员运行 `omx-team-ops.ps1 -Action status -TeamName my-team`
- **THEN** 它 SHALL 调用等价于 `omx team status my-team` 的命令

#### Scenario: ops wrapper 使用只读 team API inspection

- **WHEN** 操作员运行 `omx-team-ops.ps1 -Action list-tasks -TeamName my-team`
- **THEN** 它 SHALL 调用相应的 `omx team api` 只读操作
- **AND** 它 SHALL 将 team name 作为 API 输入提供

### Requirement: hybrid wrapper SHALL 将异构 staffing 映射为 leader-side experts 加一个同构 durable worker team

`omx-team-hybrid.ps1` SHALL 接受诸如 architect、planner、executor 和 verifier 的 staffing counts。

它 SHALL 按如下方式解释：

- 保持 expert 角色为 leader-side native subagents
- 将 executor 数量映射为一个同构 durable worker swarm
- 输出一个结构化 plan，说明 expert counts、durable worker 启动形态以及 expert 使用检查点

它 MAY 选择性地启动 durable worker swarm。

它 SHALL NOT 声称每个请求角色默认都会变成 persistent pane。

#### Scenario: hybrid wrapper 在不创建 mixed persistent panes 的情况下解释 expert counts

- **WHEN** 操作员运行 `omx-team-hybrid.ps1 -Architect 1 -Planner 1 -Executor 2 -Verifier 1 -Task "implement rollout X"`
- **THEN** 它 SHALL 报告 architect、planner 和 verifier 仍然是 leader-side native roles
- **AND** 它 SHALL 根据 executor 数量推导出一个 durable worker swarm

### Requirement: verify wrapper SHALL 强化 leader-side native verification roles

`omx-team-verify.ps1` SHALL 输出针对 leader-side native roles 的 verification plan，而不是默认转为 persistent verifier swarm。

至少它 SHALL 能规划使用：

- `verifier` - 用于 final acceptance 和 evidence validation 的 leader-side role。
- `test-engineer` - 用于 test strategy 和 regression-risk validation 的 leader-side role。
- `security-reviewer` - 用于 security 和 trust-boundary review 的 leader-side role。
- `writer` - 用于 documentation 和 operator-guidance review 的 leader-side role。

#### Scenario: verification wrapper 在不启动 verifier pane 的情况下规划最终验收

- **WHEN** 操作员针对行为变更型多文件改动运行 `omx-team-verify.ps1`
- **THEN** 它 SHALL 推荐 leader-side native verification roles
- **AND** 它 SHALL 不把 persistent verifier pane 作为默认路径

### Requirement: 安装器 SHALL 生成一个可跨仓库复用的 playbook

安装器 SHALL 生成一个用户级 playbook，记录：

- team-mode 状态含义
- wrapper 用法
- team lifecycle commands
- hybrid staffing 解释
- open-ended research roles 与 implementation roles 的分离

#### Scenario: 用户在其他仓库读取生成的 playbook

- **WHEN** 用户在本仓库之外打开生成的 playbook
- **THEN** 它 SHALL 仍然描述一个可复用的 operator workflow
- **AND** 它 SHALL 不依赖下游应用特定 runtime commands

#### Scenario: 生成的 playbook 解释用户级 backend policy surface

- **WHEN** 操作员在其他仓库中阅读生成的 playbook
- **THEN** 它 SHALL 识别 primary backend-policy surface 与 supporting backend-policy views
- **AND** 它 SHALL 解释稳定默认 backend、优先 backend 使用场景以及 backend-family switching 规则
- **AND** 它 SHALL 说明 repository-local specs 和双语 implementation plans 仍然是 backend-policy 演进的 development source of truth

### Requirement: automatic team helper SHALL 将 phase 与 workload signals 映射为已批准的 durable-team presets

`omx-team-auto.ps1` SHALL 接受显式 phase 与 workload signals，并按如下方式解释：

- 早期阶段与最终阶段保持 subagent-only
- 当 parallel-slice threshold 命中时，将 execution 与 integration 阶段映射到保守的 `team-executor` swarm
- 当 blocking-issue threshold 命中时，将 stabilize 阶段映射到 `debugger` swarm

它 MAY 选择性地应用已规划动作。

它 SHALL NOT 声称每个自动决策都会变成 mixed persistent pane topology。

#### Scenario: automatic helper 为更宽的并行执行选择 `3:team-executor`

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase execute-parallel -ParallelSlices 3 -Task "ship rollout X" -Json`
- **THEN** 它 SHALL 推导出等价于 `omx team 3:team-executor "ship rollout X"` 的命令

#### Scenario: automatic helper 为 stabilize 选择 `2:debugger`

- **WHEN** 操作员运行 `omx-team-auto.ps1 -Phase stabilize -BlockingIssues 1 -Task "stabilize regression X" -Json`
- **THEN** 它 SHALL 推导出等价于 `omx team 2:debugger "stabilize regression X"` 的命令

### Requirement: 安装器 SHALL 生成 LangGraph durable orchestration entrypoints

安装器 SHALL 向目标 Codex home 生成 additive 的 LangGraph-oriented durable orchestration entrypoints。

生成的 LangGraph 资产集合至少 SHALL 包含以下 operator surfaces：

- run 或 start
- status 或 inspect
- resume
- interrupt inspection

生成的 playbook SHALL 记录这些 LangGraph entrypoints 与现有 `omx team` entrypoints 的关系。

#### Scenario: 操作员检查生成的 LangGraph entrypoints

- **WHEN** 安装器将用户级 team-mode assets 渲染到目标 Codex home
- **THEN** 它 SHALL 在该目标中生成 additive 的 LangGraph entrypoint assets
- **AND** 生成的 playbook SHALL 解释它们如何与现有 `omx team` wrappers 共存

### Requirement: 生成的 playbook SHALL 记录 orchestration activation 与 retrofit 规则

生成的用户级 playbook SHALL 记录：

- 强制 orchestration re-check triggers
- 对 `omx` 或 `LangGraph` 的显式请求属于 hard routing directives
- 既有项目中的新会话会自动遵循当前用户级 policy
- 既有 live sessions 会在 reload、restart、显式用户指令或 tracked durable-state detection 时 retrofit

#### Scenario: 操作员为一个既有仓库阅读生成的 playbook

- **WHEN** 操作员在既有仓库中工作，或在继续一个既有工作流时阅读生成的 playbook
- **THEN** 该 playbook SHALL 描述 orchestration activation 如何被重新检查与 retrofit
- **AND** 它 SHALL NOT 暗示 orchestration 规则只适用于全新仓库或全新会话

### Requirement: 生成的 team entrypoints SHALL 参与 canonical inspectable durable-state surface

生成的用户级 team entrypoint layer SHALL 参与 canonical inspectable durable-state surface，而不是让 durable-team inspection 只散落在不相关的 wrapper 描述中。

至少包括：

- 生成的只读 team inspection paths SHALL 暴露足够信息，以推导 tracked native durable-team state 的共享 summary fields
- 生成的 playbook SHALL 解释 canonical inspectable state surface 与 `omx-team-ops.ps1` 及其他 backend-specific helpers 的关系

#### Scenario: 操作员从生成的 entrypoints 检查当前 native durable-team state

- **WHEN** 操作员对一个 tracked native durable team 使用已批准的只读 team inspection entrypoints
- **THEN** 这些 entrypoints SHALL 提供或馈送 canonical inspectable durable-state summary 所需的数据
- **AND** 操作员 SHALL 不需要仅靠分散的 wrapper 文案去推断当前 worker 形态、tracked identity 和下一步 inspection path

### Requirement: 生成的 playbook SHALL 链接到一个 quick-reference companion

生成的用户级 playbook SHALL 链接到一个简明的 quick-reference companion，用于最常见的 operator commands。

该 companion SHALL 位于用户级 docs 层，并与实际已安装的用户级命令面保持一致。

#### Scenario: 操作员从完整 playbook 出发，但只需要常用命令

- **WHEN** 操作员打开生成的 playbook，但只需要最常见的命令
- **THEN** 该 playbook SHALL 指向 quick-reference companion
- **AND** 操作员 SHALL 不需要通读完整 playbook 才能找到最常见的 command entrypoints

### Requirement: 当 mixed persistent pane compose 被启用时，生成的 team entrypoint layer SHALL 包含 advanced compose entrypoint

当 advanced mixed persistent pane compose layer 被启用时，生成的用户级 team entrypoint layer SHALL 包含一个用户级 compose entrypoint 与 manifest guidance。

生成的 playbook SHALL 将该 compose mode 描述为 advanced opt-in 路径，而不是默认 workflow。

#### Scenario: 操作员阅读 advanced compose mode 的生成入口指引

- **WHEN** 操作员在 compose assets 安装完成后阅读生成的用户级 playbook
- **THEN** 该 playbook SHALL 识别 compose entrypoint 及其 manifest requirement
- **AND** 它 SHALL 将 mixed persistent pane compose 描述为 advanced opt-in mode
