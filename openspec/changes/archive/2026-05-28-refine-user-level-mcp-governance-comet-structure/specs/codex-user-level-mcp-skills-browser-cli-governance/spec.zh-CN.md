## ADDED Requirements

### Requirement: 治理方案必须使用可执行新版 Comet 结构

用户级 MCP、skills、browser automation 与 CLI harness 治理方案必须包含面向 worker 的 Goal、Architecture、Tech Stack 开头块，并包含文件职责、就绪定义、任务级 backlog、验收、证据、回滚和风险等执行型章节。

#### Scenario: 新版章节存在

- **WHEN** 人工复核方案结构
- **THEN** 方案必须包含 Goal、Architecture、Tech Stack、文件职责图、实施前就绪定义、任务级 Backlog、验收标准、需要保留的证据、回滚与风险
- **AND** 必须保留 Token/risk priority、authorization receipt、update receipt、evidence redaction、port registry/lease、codex-port allocator、pending_bind、registry_revision、39000-39299、40000-40999、OpenSpec slice 和 fail closed 治理 marker

#### Scenario: 运行时 lane 继续按风险门禁治理

- **WHEN** 某个 lane 缺少 install、smoke、receipt 或 rollback evidence
- **THEN** 它不得标记为 active
- **AND** sensitive MCP、browser、CDP Bridge、OpenCLI、CLI-Anything 和 WeCom 操作必须需要当前授权 receipt 证据
