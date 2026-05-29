# 设计：Project MOE CLI envelope schema 加固

## 当前状态

`require_cli_envelope()` 校验 read-contract 命令的公共 JSON envelope。它已经拒绝非对象 payload、缺失公共字段、命令回显不匹配、ok/token 错误、CLI contract 不匹配和私有字段泄露。

## 缺口

目标 Mode CLI 目前可以返回一个存在但不受支持的 `schema_version`，同时通过其他公共 envelope 校验。这会让 GUI readiness gate 进入不明确的兼容状态。

## 决策

当 `payload["schema_version"] != SCHEMA_VERSION` 时返回专用 blocker：`blocked:cli_envelope_schema_version_mismatch`。该 blocker 属于 `mode_cli_contract` repair 类别，需要目标项目写入才能修复，并通过既有 readiness checker remediation plan 输出。

## 安全说明

- 该检查只读，只检查安全读命令已经输出的 JSON。
- static-only 仍然不执行目标 CLI。
- 静态 blocker 和 dirty target 状态仍会在执行 CLI 之前阻断。
- 本变更不读取或写入私有提示源、Agent TOML 或 `.omx/state`。

## 验证重点

- Ready fixture 仍然通过。
- 不支持的 `schema_version` 在 read-contract 路径 fail-closed。
- readiness 输出保持 `control_mode_allowed=false` 并暴露稳定 blocker/remediation group。
