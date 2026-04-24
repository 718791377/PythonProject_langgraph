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
