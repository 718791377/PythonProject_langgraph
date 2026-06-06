# 设计：Durable Capability Readiness R4 运行时刷新

## 运行时边界
`codex-durable-state-status.ps1` 默认保持只读。R4 只新增显式 `-RefreshReadiness` 路径，写入 `<repo>/.omx/state/readiness/durable-capability-readiness-projection.json`。

## Receipt 结构
Receipt 记录 `schema_version`、`receipt_kind`、`promotion_marker=smoke-tested`、`generated_at`、`repo_root`、`selected_backend`、`backend_default`、`backend_ready`、`capability_readiness`、`blockers`、`source_receipts`、`selector_evidence`、`version_evidence`、`durable_workflow_adopted=false`、`persistent_team_launched=false` 与 smoke 元数据。

## 安全性
Refresh 只复制已计算的 status projection 证据，不运行后端启动命令。默认 status 读取不得创建 `.omx`。
