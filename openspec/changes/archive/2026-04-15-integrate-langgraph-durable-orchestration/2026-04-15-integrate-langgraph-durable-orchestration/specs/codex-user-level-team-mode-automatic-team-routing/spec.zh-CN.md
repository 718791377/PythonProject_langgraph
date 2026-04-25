## ADDED Requirements

### Requirement: 自动 durable routing 必须尊重 durable orchestration backend selector
自动 durable routing 层必须尊重 durable orchestration backend selector，而不是假设所有 durable decision 都会直接通过当前 native `omx team` 路径执行。

当被选中的 backend 是 `langgraph` 时，计划中的 durable execution 结果必须把 LangGraph 标记为目标 durable 路径。

#### Scenario: 自动路由规划出 LangGraph durable execution
- **WHEN** durable orchestration backend selector 是 `langgraph`
- **AND** 当前任务已经满足 durable execution 阈值
- **THEN** 自动 durable routing plan 必须把 LangGraph 标记为所选 backend
- **AND** 它不得把该决策误报成 direct `omx team` launch
