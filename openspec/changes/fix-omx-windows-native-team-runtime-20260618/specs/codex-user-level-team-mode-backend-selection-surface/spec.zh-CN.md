## ADDED Requirements

### Requirement: Backend selection surface 必须暴露四层编排模型

用户级 backend-selection surface SHALL 区分能力开关、后端家族、effective lane 和运行能力。

#### Scenario: 操作者在 Windows 上检查 native OMX

- **WHEN** 操作者检查 Windows worker-centric task 的 backend state
- **THEN** surface SHALL 分开展示 enabled capability layers 与 selected backend family
- **AND** SHALL 分开展示 task-flow effective lane 与 operational ability
- **AND** SHALL NOT 暗示 selected `native_omx` 在没有 preflight evidence 时可启动。

### Requirement: Backend default 不得覆盖 task-flow effective lane evidence

backend-selection surface SHALL 保留 durable backend default 与 task-flow effective lane 的区别。

#### Scenario: LangGraph enabled 但 worker-centric native OMX 被评估

- **GIVEN** LangGraph enabled 且可能是 ready durable default
- **WHEN** worker-centric task 被评估到 `native_omx`
- **THEN** surface SHALL 报告 effective lane 的 task-fit reason
- **AND** SHALL 在启动 persistent team 前仍要求 operational preflight。
