## ADDED Requirements

### Requirement: 治理方案 SHALL 使用新版实施方案结构

用户级 MCP、skills、browser automation 与 CLI harness 治理方案 SHALL 使用 Pi sidecar 与 Comet runtime 方案同族的新型实施方案结构展示实施模型。

#### Scenario: 结构包含 runtime 与治理章节

- **WHEN** 本次重构后复核该方案
- **THEN** 它 SHALL 包含关系边界、目标/非目标、运行时架构、Codex 使用、repo-local source of truth、用户级产物与 receipts、state contract、phase gates、implementation slices、task backlog、本地集成顺序、acceptance criteria、evidence、rollback 与 risks
- **AND** 它 SHALL 保留 `skills2cli`、`mcp2cli`、`chrome-devtools-mcp`、CDP Bridge、OpenCLI、CLI-Anything、`wecom-cli`、port registry、`codex-port`、`pending_bind`、`registry_revision`、`39000-39299`、`40000-40999`、authorization receipt、update receipt 与 evidence-redaction governance markers

#### Scenario: runtime 动作保持门禁

- **WHEN** 某个 lane 仍缺少 wrapper、smoke、receipt 或 rollback evidence
- **THEN** 方案 SHALL 保持该 lane 低于 `active`
- **AND** 它 SHALL 要求 sensitive MCP/browser/CDP/OpenCLI/WXWork actions 必须有当前明确 authorization receipts
