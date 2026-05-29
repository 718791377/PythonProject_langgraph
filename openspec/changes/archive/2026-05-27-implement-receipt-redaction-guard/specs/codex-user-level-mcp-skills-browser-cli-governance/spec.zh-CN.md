# Delta：receipt redaction guard

## ADDED Requirements

### Requirement: 用户级 receipt governance guard SHALL 校验 authorization、update、rollback 与 redaction evidence

仓库必须提供 repo-local 通用 receipt governance guard，用于用户级 MCP、skills、browser 与 CLI harness lanes。该 guard 必须校验单任务 authorization receipt schema、update receipt schema、rollback pointer、smoke evidence 和 redaction 边界；不得安装工具、调用 MCP server、控制浏览器、读取 browser data、修改用户级 Codex 配置，默认输出不得暴露 raw private paths 或 raw secrets。

#### Scenario: Authorization receipt 缺少必填字段

- **WHEN** `python tools/user_level_receipt_governance.py auth-check --receipt <path> --action browser.click --target tab:123 --session session-a --json` 针对不完整 receipt 运行
- **THEN** 命令必须 fail closed
- **AND** 必须报告缺失的 authorization receipt 字段

#### Scenario: 有效 update receipt 对私有路径和 rollback pointer 做 hash 化输出

- **WHEN** `update-check` 收到具有 install、wrapper、state、smoke、updater、owner-lane、redaction 和 rollback evidence 的有效 receipt
- **THEN** 命令必须返回 `ok=true`
- **AND** 必须报告 `rollback_ready=true`
- **AND** 必须对 install path、wrapper path、state path 和 rollback pointer 输出 hash

#### Scenario: Redaction check 发现原始敏感 payload

- **WHEN** `python tools/user_level_receipt_governance.py redact-check --receipt <path> --json` 针对含 cookies、inline token value、message contents 或 plugin description dumps 的 receipt 运行
- **THEN** 命令必须 fail closed
- **AND** 必须报告 redaction findings
