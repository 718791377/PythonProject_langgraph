## ADDED Requirements

### Requirement: 安装器必须生成用户级 OMX team 入口资产

安装器必须把 additive-only 的用户级 team 入口资产生成到目标 Codex home。

至少包括：

- `bin/omx-team-dev.ps1`
- `bin/omx-team-debug.ps1`
- `bin/omx-team-verify.ps1`
- `bin/omx-team-ops.ps1`
- `bin/omx-team-hybrid.ps1`
- `docs/team-mode-playbook.md`

#### Scenario: 在临时 Codex home 中生成 P2 team 入口层

- **WHEN** 安装器对显式目标 Codex home 运行
- **THEN** 它必须在该目录下生成这些 team 入口 wrapper 与 playbook
- **AND** 它必须保持这些新资产是 additive-only

### Requirement: 生成后的 wrapper 必须调用解析出的原生 OMX 命令路径

安装器必须解析原生 `omx` 命令路径，或者接受显式覆盖；生成后的 wrapper 必须直接调用这个解析结果。

安装器不得替换或覆盖原生 `omx` 可执行文件。

#### Scenario: 测试安装使用 fake OMX 目标

- **WHEN** 安装器用显式 fake `omx` 命令路径运行
- **THEN** 生成后的 wrapper 必须调用这个 fake 路径
- **AND** wrapper 行为必须能在不修改真实用户安装的情况下被测试

### Requirement: 开发与调试 wrapper 必须编码批准过的持久团队默认值

`omx-team-dev.ps1` 必须编码一个持久开发团队 preset。

至少包括：

- 默认 worker 数：`2`
- 默认 worker role：`team-executor`
- 可选切换到 `executor`

`omx-team-debug.ps1` 必须编码一个持久调试团队 preset。

至少包括：

- 默认 worker 数：`2`
- 默认 worker role：`debugger`

#### Scenario: 开发 wrapper 启动保守型 worker swarm

- **WHEN** operator 运行 `omx-team-dev.ps1 -Task "ship feature X"`
- **THEN** 它必须调用等价于 `omx team 2:team-executor "ship feature X"` 的命令

#### Scenario: 调试 wrapper 启动 debugger swarm

- **WHEN** operator 运行 `omx-team-debug.ps1 -Task "stabilize regression X"`
- **THEN** 它必须调用等价于 `omx team 2:debugger "stabilize regression X"` 的命令

### Requirement: ops wrapper 必须暴露已支持的团队生命周期命令和安全只读检查面

`omx-team-ops.ps1` 必须包装以下生命周期命令：

- `status`
- `await`
- `resume`
- `shutdown`

它还必须支持安全只读的 team API 操作，例如：

- `list-tasks`
- `mailbox-list`
- `get-summary`
- `read-manifest`

#### Scenario: ops wrapper 显示 team 状态

- **WHEN** operator 运行 `omx-team-ops.ps1 -Action status -TeamName my-team`
- **THEN** 它必须调用等价于 `omx team status my-team` 的命令

#### Scenario: ops wrapper 使用只读 team API 检查

- **WHEN** operator 运行 `omx-team-ops.ps1 -Action list-tasks -TeamName my-team`
- **THEN** 它必须调用相应的只读 `omx team api` 操作
- **AND** 必须把 team name 作为 API 输入传入

### Requirement: hybrid wrapper 必须把异构编制映射为 leader 侧专家角色 + 一组同构持久 worker 团队

`omx-team-hybrid.ps1` 必须接受 architect、planner、executor、verifier 等计数。

它必须按如下方式解释：

- 专家角色保留为 leader 侧原生 subagent
- executor 计数映射为一组同构持久 worker swarm
- 输出一个结构化 plan，说明专家计数、持久 worker 启动形态，以及专家角色的预期检查点

它可以选择性地启动这组持久 worker swarm。

它不得宣称“每个请求角色默认都会变成 persistent pane”。

#### Scenario: hybrid wrapper 解释专家计数，但不创建 mixed persistent panes

- **WHEN** operator 运行 `omx-team-hybrid.ps1 -Architect 1 -Planner 1 -Executor 2 -Verifier 1 -Task "implement rollout X"`
- **THEN** 它必须报告 architect、planner、verifier 仍然是 leader 侧原生角色
- **AND** 它必须从 executor 计数推导出一组持久 worker swarm

### Requirement: verify wrapper 必须强化 leader 侧原生验证角色

`omx-team-verify.ps1` 必须输出 leader 侧原生验证计划，而不是默认启动持久 verifier swarm。

至少能够规划：

- `verifier`
- `test-engineer`
- `security-reviewer`
- `writer`

#### Scenario: verification wrapper 规划最终签收，而不启动 verifier pane

- **WHEN** operator 对一个会改变行为的多文件变更运行 `omx-team-verify.ps1`
- **THEN** 它必须推荐 leader 侧原生验证角色
- **AND** 它不得把持久 verifier pane 设为默认路径

### Requirement: 安装器必须生成可跨仓库复用的 playbook

安装器必须生成一份用户级 playbook，说明：

- team-mode 状态含义
- wrapper 用法
- team 生命周期命令
- hybrid staffing 解释
- 开放式研究角色与实现角色的分离

#### Scenario: 用户在其他仓库里阅读生成后的 playbook

- **WHEN** 用户在本仓库外打开生成后的 playbook
- **THEN** 它仍然必须描述一套可复用的 operator workflow
- **AND** 不得依赖 OpenClaw 专有 runtime 命令
