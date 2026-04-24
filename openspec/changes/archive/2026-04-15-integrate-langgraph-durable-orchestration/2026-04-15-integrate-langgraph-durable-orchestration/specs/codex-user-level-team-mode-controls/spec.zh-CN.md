## ADDED Requirements

### Requirement: 生成 controls 必须持久化 durable orchestration backend 选择器
生成出来的用户级 control surface 必须把 durable orchestration backend 作为一项独立且显式的选择器持久化。

至少必须支持：

- `native_omx`
- `langgraph`

在显式选择 LangGraph 前，默认 durable orchestration backend 仍然必须保持当前 native 路径。

#### Scenario: fresh install 默认保留当前 backend
- **WHEN** installer 创建一份新的用户级 control state
- **THEN** durable orchestration backend selector 必须默认是 `native_omx`
- **AND** LangGraph 必须保持为 additive，而不是自动替换当前 durable 路径
