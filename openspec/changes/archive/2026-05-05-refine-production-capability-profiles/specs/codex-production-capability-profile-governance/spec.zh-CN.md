# codex-production-capability-profile-governance 规格增量

## ADDED Requirements

### Requirement: Production Plan Separates Durable-Team Dependencies From Business Runtime Dependencies

生产级持久化团队方案必须说明：评测、GUI 控制、队列、embedding、vector retrieval 和恢复工具等第三方依赖，默认属于 Codex CLI durable-team runtime；除非具体业务项目单独声明并拥有，否则不得复用为具体 business runtime dependency。

#### Scenario: PySide6 appears in the production durable-team plan

- **GIVEN** 方案把 `PySide6` 列为本地 GUI 控制中心依赖
- **WHEN** 某个具体业务项目也需要桌面 GUI
- **THEN** 方案把 Codex CLI durable-team GUI 与 concrete business GUI 视为两个独立系统
- **AND** 业务项目必须自己拥有 GUI 依赖、打包、状态和发布规则

### Requirement: Local Llama Model Service Is The Only Shared Dependency Exception

生产级持久化团队方案只能把本地 Llama 模型部署作为共享依赖例外；该模型服务必须通过 provider adapter 使用，并隔离 policy、logging、permissions、prompts、secrets 和 data boundaries。

#### Scenario: A business workload and the durable team both use a local model

- **GIVEN** business surface 和 durable team surface 都调用同一个本地模型服务
- **WHEN** 调用通过 provider profiles 路由
- **THEN** durable team state、business state、secrets、prompts 和 logs 保持隔离

### Requirement: Business Capability Profiles Stay Abstract In The Main Plan

生产级持久化团队方案必须描述抽象 capability profiles，而不是在主方案正文中写入具体业务名称。

#### Scenario: A new concrete workload is evaluated

- **GIVEN** 维护者收到新的 workload example
- **WHEN** 维护者规划该 workload 的支持方式
- **THEN** workload 映射到一个或多个 abstract capability profiles
- **AND** 具体名称只记录在单独参考对照表中
