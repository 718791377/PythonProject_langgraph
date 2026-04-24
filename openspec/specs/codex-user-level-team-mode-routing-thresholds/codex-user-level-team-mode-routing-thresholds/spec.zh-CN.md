# Codex 用户级 Team Mode 路由阈值

## Purpose

定义 Codex / oh-my-codex team mode 的用户级路由阈值、启动路径和运行态隔离规则。

该能力让包装后的 `codex` 启动行为保持可检查、可跨仓库复用，同时保持原生 Codex 始终作为永久基础层。

## Requirements

### Requirement: 安装器 SHALL 生成一个可检查的用户级 routing-policy surface

安装器 SHALL 向目标 Codex home 生成一个 additive 的用户级 routing-policy inspection script。

生成资产集合 SHALL 包含：

- `bin/codex-routing-policy.ps1`

inspection 输出 SHALL 是只读的，并且 SHALL 反映包装后 `codex` 启动所使用的同一套 routing-policy model。

inspection 输出还 SHALL 暴露：

- 已生成的 burst-review role set 以及每个 burst-review role 是否已安装
- automatic durable-team routing section
- automatic durable-team routing 的 helper path
- tracked-team record path 与 unmanaged teams 的 non-adoption rule

#### Scenario: 在 P5 安装后检查 routing policy

- **WHEN** 操作员运行 `codex-routing-policy.ps1 -Json`
- **THEN** 它 SHALL 报告当前 startup mode、routing mode 和 role-routing availability
- **AND** 它 SHALL 暴露 durable-team phase map、helper path、reuse or switch or shutdown 规则以及 tracked-team safety boundary

#### Scenario: routing policy 复述已提升的 backend-selection contract

- **WHEN** 操作员运行 `codex-routing-policy.ps1 -Json`
- **THEN** 它 SHALL 暴露与用户级 backend status surface 相同的 backend-selection contract
- **AND** 它 SHALL 报告 primary backend-policy surface 和 supporting views
- **AND** 它 SHALL 保持 backend-family switching 仍然是 explicit 或 manual-only 的规则

### Requirement: 包装启动 SHALL 从结构化 routing-policy model 派生 developer instructions

生成的 shared support script SHALL 暴露一个结构化 routing-policy model，覆盖：

- general routing principles
- role-specific thresholds
- research-to-implementation handoff rules
- adversarial bug-review rules
- 包装后的 `codex` 与 `codex-native` 的 startup-path semantics
- enhanced auto mode 下的 automatic durable-team routing semantics

startup launcher SHALL 从该 shared model 派生 developer-instruction payload，而不是依赖不相关的手写摘要。

#### Scenario: enhanced auto mode 暴露 durable-team helper 而不改变 startup 语义

- **WHEN** 包装后的 `codex` 在 `oh_my_codex=on` 且 `subagent_routing=auto` 时启动
- **THEN** 它 SHALL 注入 developer instructions，说明 automatic durable-team helper 与 phase thresholds
- **AND** 它 SHALL 说明 startup 本身仍然不会 auto-launch durable team

### Requirement: routing policy SHALL 保持已批准的 startup 语义

routing policy SHALL 区分：

- wrapped native-routed startup
- enhanced startup
- pure debugging startup

它 SHALL 保持这样一条规则：启用 oh-my-codex 会改变 startup mode 与 capability flags，但不会在每次 `codex` 启动时自动拉起 durable team。

#### Scenario: enhanced mode 在操作员启动 team 之前仍然只是 startup-only

- **WHEN** 操作员全局启用 oh-my-codex 后再启动包装后的 `codex`
- **THEN** routing policy SHALL 报告为 enhanced startup
- **AND** 它 SHALL NOT 声称 durable team 已自动启动

### Requirement: 生成的 leader 与 playbook assets SHALL 镜像路由和隔离规则

生成的 `team-leader.toml` 与 `docs/team-mode-playbook.md` SHALL 记录：

- wrapped `codex` 与 `codex-native`
- role-routing thresholds
- research-to-implementation handoff discipline
- adversarial bug-review usage
- 多项目运行态隔离来自每个仓库自己的 `.omx` state roots 这一规则

当 burst-review roles 已生成时，这些资产 SHALL 将其描述为真实、可由 leader-side 调用的角色，而不是抽象的未来占位符。

#### Scenario: 用户在另一个仓库中阅读 P4 后生成的 assets

- **WHEN** 用户在当前仓库之外打开生成的 leader profile 或 playbook
- **THEN** 这些资产 SHALL 仍然描述一个可跨仓库复用的 operating model
- **AND** 它们 SHALL NOT 依赖下游应用特定的 runtime commands
- **AND** 它们 SHALL 将 burst-review triad 描述为已生成、可调用的用户级角色

### Requirement: Automatic expert routing SHALL 被描述为建立在显式原生 spawning 之上的 leader-side overlay

这套可复用 routing policy SHALL 将 automatic expert-role routing 描述为 leader-side policy，建立在显式 native Codex subagent spawning 之上。

它 SHALL NOT 将裸 Codex 描述为默认会自动拉起 specialist roles。

#### Scenario: 操作员在 native-routed mode 下检查 routing policy

- **WHEN** 操作员检查 wrapped native-routed startup 的 routing-policy surface
- **THEN** 它 SHALL 将 expert selection 描述为 leader-side routing over native Codex subagents
- **AND** 它 SHALL NOT 将 raw Codex 描述为默认自动拉起这些角色

### Requirement: routing policy SHALL 对 write-heavy fan-out 施加比 read-heavy fan-out 更严格的 gating

routing policy SHALL 优先 read-heavy 或边界非常清晰的 native-subagent fan-out。

对于 write-heavy multi-agent execution，routing policy SHALL 要求显式 ownership isolation、hotspot serialization 和 leader-owned final integration，之后任务才可被视为符合并行路由条件。

#### Scenario: routing policy 评估一个缺少 ownership isolation 的 write-heavy 任务

- **WHEN** 任务需要多个 writer，但 ownership isolation 尚未定义
- **THEN** routing policy SHALL 将该任务归类为尚不适合 write-heavy parallel execution
- **AND** 它 SHALL 要求先定义 ownership isolation 或 worktree separation，之后才批准 write-heavy fan-out

### Requirement: routing policy SHALL 暴露强制 orchestration re-check triggers

用户级 routing policy SHALL 暴露超出首轮 startup 之外的 orchestration re-check triggers。

至少包括：

- task-phase change
- 从一个 slice 扩展到两个或更多 execution slices
- tracked durable-state detection
- 对 `omx`、`LangGraph`、resume、continue 或 parallel execution 的显式用户请求

#### Scenario: 操作员检查 orchestration re-check triggers

- **WHEN** 操作员运行 `codex-routing-policy.ps1 -Json`
- **THEN** 它 SHALL 暴露强制 orchestration re-check triggers
- **AND** 它 SHALL NOT 将 activation 描述为仅首轮有效的决策

### Requirement: routing policy SHALL 将显式 orchestration 请求视为 hard directives

用户级 routing policy SHALL 将对 `omx` 或 `LangGraph` 的显式用户请求视为 hard routing directives。

当 activation thresholds 命中且不存在具体 blocker 时，Codex CLI SHALL 实际采用 orchestration path，而不是停留在 explanation-only mode。

#### Scenario: 用户显式请求 `LangGraph`

- **WHEN** 用户显式请求 `LangGraph`
- **THEN** Codex CLI SHALL 将其视为 hard routing directive
- **AND** 除非存在具体 blocker，否则它 SHALL 采用对应 orchestration path
- **AND** 如果没有采用 orchestration path，它 SHALL 解释具体 blocker

### Requirement: routing thresholds SHALL 将 mixed persistent pane compose 保持在默认路径之外

用户级 routing-threshold model SHALL 将 mixed persistent pane compose 保持在默认路径之外。

除非操作员显式调用 compose mode，否则 automatic routing SHALL 继续使用普通 hybrid model。

#### Scenario: ordinary durable execution 已命中 thresholds

- **WHEN** 一个任务已命中 ordinary durable-routing thresholds
- **THEN** workflow SHALL 继续选择默认 hybrid operating model
- **AND** 它 SHALL NOT 在没有显式 compose request 的情况下静默启用 mixed persistent pane compose
