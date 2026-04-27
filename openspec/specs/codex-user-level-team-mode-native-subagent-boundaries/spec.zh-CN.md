# codex-user-level-team-mode-native-subagent-boundaries Specification

## 目的

定义用户级 Codex / oh-my-codex 工作流中可复用的原生 Codex subagent 合同，包括显式的 leader 侧拉起语义、custom-agent 放置规则、有上限的 fan-out、写多型并行门控规则，以及 OMX 术语边界。

## 要求

### Requirement: 原生 Codex subagent 必须保持为显式 leader 编排能力

这套可复用的用户级 team-mode 工作流必须把原生 Codex subagent 描述为一种官方原生能力：由 leader lane 显式拉起，并在 leader 侧完成 fan-in。

生成出来的 routing policy、leader profile 和 operator 指南不得把裸 Codex 描述成默认会自动拉起专家角色。

#### Scenario: 操作员检查原生路由模式说明

- **WHEN** 操作员检查 wrapped native-routed 启动模式下的生成指南
- **THEN** 该指南必须把专家角色描述为由 leader lane 选择并调用的原生 Codex subagent
- **AND** 必须把这种行为与 durable `omx team` worker 以及裸未包装 Codex 默认行为区分开

### Requirement: custom 原生 subagent TOML 必须采用分层位置与最小独立 schema

这套工作流必须保留两层 custom-agent 位置规则：

- 用户级可复用角色位于 Codex home 下的 agent 目录
- 仓库特化角色位于 `<repo>/.codex/agents/`

这套工作流所使用的每个独立 custom-agent TOML 至少必须定义：

- `name` - required native-agent TOML field for the agent role name.
- `description` - required native-agent TOML field for the role summary.
- `developer_instructions` - required native-agent TOML field for role-specific behavior instructions.

#### Scenario: 维护者检查角色放置规则

- **WHEN** 维护者读取面向可复用角色与仓库特化角色的生成指南
- **THEN** 该指南必须区分用户级可复用 agent TOML 与仓库级 agent TOML
- **AND** 必须写出独立 custom-agent 的最小字段要求

### Requirement: 原生 subagent fan-out 必须保持有上限且可检查

这套工作流必须通过显式、可被 operator 看到的控制面来约束原生 subagent fan-out，其中至少包括 `agents.max_threads` 与 `agents.max_depth`。

生成出来的控制面或指导文档必须说明：提高这些值会增加 token 消耗、延迟和本地资源压力。

#### Scenario: 操作员检查受管 fan-out 上限

- **WHEN** 操作员查看生成出来的 native-subagent 上限控制面
- **THEN** 该控制面必须暴露 `agents.max_threads` 与 `agents.max_depth`
- **AND** 必须说明 fan-out 变宽或变深带来的成本与延迟影响

### Requirement: 原生 subagent 并行执行必须区分读多型与写多型任务

路由策略必须优先把原生 subagent 并行 fan-out 用在读多型或边界非常清晰的任务上。

对于写多型多 agent 执行，只有在以下条件全部显式成立时，这套工作流才可以把任务视为有效：

- 通过文件切片或 worktree 明确 ownership 隔离
- 已定义热点串行规则
- 最终集成仍由 leader 负责

#### Scenario: planner 看到读多型有界任务

- **WHEN** 任务主要是探索、分析或其他读多型工作
- **THEN** 路由策略必须允许有界的原生 subagent fan-out

#### Scenario: planner 看到未隔离 ownership 的写多型任务

- **WHEN** 任务需要多个 writer，但尚未定义 ownership 隔离或热点串行规则
- **THEN** 这套工作流必须把该任务归类为“尚未准备好做写多型并行执行”
- **AND** 必须要求先补齐 ownership 隔离后才能继续多 writer 执行

### Requirement: OMX 术语边界必须保持为“覆盖在 Codex 之上的一层”，而不是替代 Codex

生成出来的 leader、playbook 和 operator-facing 资产必须把 oh-my-codex 描述为构建在 Codex 之上的工作流层与持久状态层，而不是 Codex 的替代品。

这些资产还必须区分：

- 原生 Codex subagent 是会话内的受限委派
- durable `omx team` 是长运行执行与恢复
- `LangGraph`、`AutoGen`、`CrewAI` 这类名字属于另一类通用可编程编排运行时

生成指南必须优先使用 `OpenHands`，而不是归档后的 `OpenDevin` 术语。

#### Scenario: 操作员阅读术语边界章节

- **WHEN** 操作员阅读生成出来的 playbook 或 leader 指南
- **THEN** 这些资产必须把 OMX 描述成覆盖在 Codex 之上的一层，而不是替代品
- **AND** 必须把 `OpenHands` 与通用编排运行时术语同原生 Codex subagent 区分开

### Requirement: 原生 subagent 的 lifecycle monitoring 必须能区分“仍在工作”与“已经卡住”

生成出来的 leader 指引、routing policy 与 operator-facing 文档必须描述一套 retention-aware 的原生 subagent lifecycle contract，其中包括 dynamic wait windows 与 periodic progress/liveness check-ins。

这套 contract 至少必须：

- 保持 `completed_subagent_retention = close | keep` 作为持久化的 policy switch
- completed agent 的完成后行为必须由当前 retention policy 推导，而不是写死成一直 `close`
- 对 subagent 的等待必须是 bounded dynamic windows，而不是对所有 subagent 都复用一个固定的短 timeout
- 对较长时间运行的原生 subagent 必须要求 concise periodic progress/liveness 更新
- 当 repeated quiet check-ins 出现时，必须将其视为 stall evidence，而不是默默无限等待

#### Scenario: retention policy 为 `keep`

- **WHEN** 当前 completed-subagent retention policy 是 `keep`
- **THEN** 生成出来的指引必须说明：completed subagent 在 fan-in 后仍应保持 available，直到 explicit close
- **AND** 不得仍然把 `close by default` 写成不附条件的绝对规则

#### Scenario: 运行时间较长的原生 subagent 仍在活跃

- **WHEN** 一个原生 subagent 超过了初始 wait window 但仍在继续执行
- **THEN** 生成出来的指引必须要求在继续等待期间发出 concise progress/liveness updates
- **AND** 这些更新必须足以区分“正常地在推进”与“很可能已经 stall”

#### Scenario: repeated quiet check-ins 暗示 stall

- **WHEN** repeated progress/liveness checks 显示没有新进展
- **THEN** 生成出来的 lifecycle contract 必须指示 leader 去 inspect、redirect 或 respawn 该原生 subagent
- **AND** 不得指示 leader 长时间默默等待
