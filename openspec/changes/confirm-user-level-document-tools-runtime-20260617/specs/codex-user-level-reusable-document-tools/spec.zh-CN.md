## ADDED Requirements

### Requirement: 用户级文档工具运行时确认

本仓库 SHALL 在声明可复用文档/PDF/向量工具 live runtime 完成前，维护一个 follow-up 运行时确认记录。

#### Scenario: Stage 1 冻结确认范围

- **GIVEN** 可复用文档工具源码已经存在于 `tools/user_level_document_tools/`
- **WHEN** follow-up 确认包被打开
- **THEN** 它 SHALL 识别仍然存在的 live runtime 缺口
- **AND** 它 SHALL 区分共享源码、本地-only runtime cache 与消费者自有状态。

#### Scenario: Stage 2 从共享仓库验证 live runtime

- **GIVEN** Stage 1 确认包已经集成到本地 `main`
- **WHEN** live runtime 实现继续执行
- **THEN** Poppler/PDF、文档流水线和向量/检索行为 SHALL 从 `D:\PythonProject_langgraph` 完成验证
- **AND** 真实消费者向量数据、来源权威与生成输出 SHALL 保持消费者自有。

### Requirement: 消费者项目 no-drift 边界

工具迁移确认 SHALL 将 `D:\project` 视为受 guard 保护的消费者/来源对比项目，而不是共享实现权威。

#### Scenario: 消费者项目存在无关 dirty files

- **GIVEN** `D:\project` 包含无关 dirty files
- **WHEN** 执行迁移确认或清理
- **THEN** 这些 dirty files SHALL NOT 被本仓库实现流程覆盖或清理
- **AND** 任何消费者侧 mutation SHALL 使用 `D:\project` guard 证据。
