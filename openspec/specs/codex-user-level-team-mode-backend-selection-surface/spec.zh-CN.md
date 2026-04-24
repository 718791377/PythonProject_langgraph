# Codex 用户级 Team Mode Backend Selection Surface

## 目的

定义 Codex / oh-my-codex team mode 下 durable backend 选择的主用户级 operator-facing surface。

该能力确保操作者仅通过已安装的用户级 artifacts 就能在 `native_omx` 与 `langgraph` 之间做选择，同时保持 repository-local OpenSpec specs 与双语 implementation plans 继续作为策略演进时的开发权威层。

## 要求

### Requirement: 用户级安装必须暴露一个主 backend-selection policy surface

用户级安装必须在用户级 Codex home 下暴露一个主 operator-facing backend-selection policy surface。

这个主 surface 至少必须回答：

- 当前选中的 backend 是什么
- 稳定默认 backend 是什么
- 什么情况下优先 `native_omx`
- 什么情况下优先 `langgraph`
- backend-family 切换是显式还是自动
- 同一条 durable task 是否允许跨多个 backend family

这个主 surface 还必须指出哪些 supporting user-level policy views 会重复同一套 contract。

#### Scenario: 操作员检查主 backend-selection surface

- **WHEN** 操作员运行生成后的 backend status surface
- **THEN** 它必须报告当前选中的 backend 与稳定默认值
- **AND** 它必须报告 `native_omx` 与 `langgraph` 各自的优先使用场景
- **AND** 它必须报告 backend-family 切换保持显式或 manual-only
- **AND** 它必须报告一条 durable task 只能停留在一个 backend family 内

### Requirement: 用户级 backend-selection surface 必须区分 operator authority 与仓库开发 authority

用户级 backend-selection surface 必须说明：用户级 artifacts 是 backend choice 的 primary operator-facing source of truth。

它也必须说明：repository-local OpenSpec specs 与双语 implementation plans 仍然是演进该策略时的 development source of truth。

#### Scenario: 操作员不打开仓库文档也能读懂 backend policy

- **WHEN** 操作员阅读用户级 backend-selection surface
- **THEN** 该 surface 必须足以支持在 `native_omx` 与 `langgraph` 之间做出选择
- **AND** 它仍必须区分用户级 operator guidance 与 repository-local development authority

### Requirement: backend-selection surface 必须演进成“在已启用 capability 之上做 effective-lane selection”

用户级 backend-selection surface 必须从“单一全局 backend-family selector”演进成“在已启用 capability layers 之上做 effective-lane selection 的可检查 surface”。

它仍然必须让 operator 能看见：

- 当前已启用的 capability layers
- 当前 effective lane
- 为什么选中了这条 lane

#### Scenario: LangGraph 已启用但当前没有被选中

- **WHEN** LangGraph capability 已启用，但当前任务流被路由到另一条 effective lane
- **THEN** 用户级 surface 必须显示 LangGraph 仍处于 enabled 状态
- **AND** 仍必须单独显示当前任务流实际采用的 effective lane
