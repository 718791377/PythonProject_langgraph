## ADDED Requirements

### Requirement: Durable capability readiness refresh SHALL write an explicit R4 projection receipt only on request / durable capability readiness refresh 只能在显式请求时写入 R4 projection receipt

`codex-durable-state-status.ps1` 默认 SHALL 保持只读；只有 operator 传入显式 readiness refresh switch 时，才 SHALL 创建 repo-local readiness projection receipt。

该 receipt SHALL 为 `native_omx` 与 `langgraph` 保留互不折叠的 `installed`、`enabled`、`selected`、`ready` readiness fields。它 SHALL 包含 `generated_at`、source receipt evidence、selector evidence、version/install evidence、blockers，以及 R4 `smoke-tested` marker。它还 SHALL 声明本次 refresh 没有 adopted durable workflow，也没有 launched persistent team。

#### Scenario: Default status remains read-only / 默认 status 保持只读

- **WHEN** operator 运行 `codex-durable-state-status.ps1 -RepoRoot <repo> -Json`
- **AND** `<repo>` 没有 `.omx` 目录
- **THEN** helper SHALL 在不创建 `.omx` 的情况下报告 durable state 与 readiness
- **AND** helper SHALL 以 metadata 暴露显式 refresh command

#### Scenario: Explicit refresh writes a projection receipt / 显式 refresh 写入 projection receipt

- **WHEN** operator 运行 `codex-durable-state-status.ps1 -RepoRoot <repo> -RefreshReadiness -Json`
- **THEN** helper SHALL 写入 `<repo>/.omx/state/readiness/durable-capability-readiness-projection.json`
- **AND** receipt SHALL 包含 `promotion_marker=smoke-tested`
- **AND** receipt SHALL 包含 `generated_at`、`source_receipts`、`selector_evidence`、`version_evidence` 与 `blockers`
- **AND** receipt SHALL 保留互不折叠的 `installed`、`enabled`、`selected`、`ready` fields
- **AND** receipt SHALL 报告 durable workflow adoption 与 persistent-team launch 均为 false