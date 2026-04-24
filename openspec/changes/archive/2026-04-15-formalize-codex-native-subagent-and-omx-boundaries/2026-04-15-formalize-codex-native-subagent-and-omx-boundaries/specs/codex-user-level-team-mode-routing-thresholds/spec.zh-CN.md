## ADDED Requirements

### Requirement: 自动专家路由必须被描述为建立在显式原生触发之上的 leader 侧 overlay
这套可复用 routing policy 必须把自动专家角色路由描述为一种 leader 侧策略，建立在原生 Codex subagent 的显式触发之上。

它不得把裸 Codex 描述成默认会自动拉起专家角色。

#### Scenario: 操作员在原生路由模式下检查 routing policy
- **WHEN** 操作员检查 wrapped native-routed 启动模式下的生成 routing-policy 表面
- **THEN** 它必须把专家角色选择描述为“leader 侧在原生 Codex subagent 之上做路由”
- **AND** 不得把裸 Codex 描述成默认自动拉起这些角色

### Requirement: routing policy 对写多型 fan-out 的 gating 必须强于读多型 fan-out
这套路由策略必须优先允许读多型或边界非常清晰的原生 subagent fan-out。

对于写多型多 agent 执行，只有在 ownership 隔离、热点串行规则以及 leader 最终集成都已经显式成立时，路由策略才可以把任务视为允许并行。

#### Scenario: 路由策略评估一个没有 ownership 隔离的写多型任务
- **WHEN** 任务需要多个 writer，但 ownership 隔离尚未定义
- **THEN** 路由策略必须把该任务归类为“尚未满足写多型并行执行条件”
- **AND** 必须要求先补齐 ownership 隔离或 worktree 分离，才能批准写多型 fan-out
