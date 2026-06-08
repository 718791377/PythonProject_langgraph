# 设计：R4 Capability Receipt Runtime 治理

本实现扩展现有 deterministic `user_level_receipt_governance` helper，而不是新增 runtime runner。该 helper 仍保持只读：它加载 JSON receipts、校验必填字段、输出 sanitized hash-first summaries，并报告自身不会 mutate user-level state、run external tools 或 read browser data。

R4 支持由新的 smoke receipt contract 表达。有效 smoke receipt 必须识别 tool/lane，将 `runtime_stage` 声明为 R4 或 `smoke-tested`，指向 prior install receipt evidence，使用 bounded read-only smoke type（`help`、`version`、`status`、`safe-discovery` 或 `read-only`），记录 passing smoke result，包含 timeout release evidence，携带 rollback readiness 与 rollback pointer，并对 command transcript evidence 通过 redaction checks。任何 write/live marker 都必须 fail closed。

Rollback evidence 由独立 receipt validation command 表达。它校验 dry-run/apply receipt fields，并要求 apply receipts 具备 explicit operator authorization，同时仍然不执行 rollback commands。这为后续 runtime lanes 提供可复用 rollback executor evidence 格式，又不会让本 slice 修改 user-level runtime state。
