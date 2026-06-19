# Codex 用户级 Capability Switches

## 目的

定义原生路由、oh-my-codex durable features 与 LangGraph availability 的分层用户级 capability switches。

该能力用于把“哪些 orchestration layers 已启用”和“每条任务流实际走哪条 effective lane”拆开。

## 要求

### Requirement: 用户级安装必须暴露分层 capability switches

用户级安装必须暴露以下分层 capability switches：

- 原生专家路由可用性
- oh-my-codex durable-feature 可用性
- LangGraph 可用性

这些开关必须对 operator 可见，不能重新退化回单一的 durable-backend-only 控制模型。

#### Scenario: 操作员检查分层 capability state

- **WHEN** 操作员检查用户级 control state
- **THEN** 该状态必须区分已启用的 capability layers
- **AND** 不得强迫操作者只能从单一 backend selector 的值去推断这些 capability 是否启用

### Requirement: 分层 switch 模型必须保留依赖规则

分层 switch 模型必须保留 capability layers 之间显式的依赖约束。

至少包括：

- 关闭 routing 会关闭更高层 orchestration capabilities
- 开启 LangGraph 依赖 oh-my-codex durable layer 仍然启用

#### Scenario: 无效的分层状态被拒绝或归一化

- **WHEN** operator 或 runtime 试图在 prerequisite durable layer 被关闭时启用 `langgraph`
- **THEN** 用户级模型必须拒绝或归一化该状态
- **AND** 归一化后的结果仍必须显式且可检查

### Requirement: Capability switches 必须按依赖链进行可执行检查
用户级 capability switch policy 必须由可执行 checker 支撑依赖链一致性。checker 必须验证：`subagent_routing=off` 会禁用更高 orchestration layers，`oh_my_codex=off` 会禁用 LangGraph，`langgraph=on` 要求 routing 可用且 oh-my-codex 为 on，`durable_orchestration_backend=langgraph` 要求 `langgraph=on`。

仓库必须提供 `tools/check_capability_switch_chain.py`，用于验证用户级 capability state JSON，并可结合 repo-local `.omx/state/langgraph/backend.json` 上下文。在干净 CI 且未要求必须存在 state 时，checker 可以把缺失用户级 state 报告为 warning；但只要存在无效状态组合，就必须失败。`langgraph_ready=true` 表示 backend ready，不表示 persistent team 已经运行。

#### Scenario: Capability chain checker 拒绝无效状态

- **WHEN** capability state 中出现 `subagent_routing=off` 但 `oh_my_codex=on` 或 `langgraph=on`
- **THEN** checker 必须失败并报告 capability-chain violation
- **AND** 它必须指出无效依赖关系，而不是在报告里静默归一化

#### Scenario: LangGraph backend selection 被检查

- **WHEN** capability state 中出现 `durable_orchestration_backend=langgraph`
- **THEN** checker 必须要求 `langgraph=on`、`oh_my_codex=on` 和 `subagent_routing!=off`
- **AND** 如果存在 `langgraph_ready=true`，则必须要求 LangGraph 是已选择的 durable backend

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
