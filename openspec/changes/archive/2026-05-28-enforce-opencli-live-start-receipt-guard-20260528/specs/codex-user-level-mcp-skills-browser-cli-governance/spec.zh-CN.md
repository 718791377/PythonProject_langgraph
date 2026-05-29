## ADDED Requirements

### Requirement: OpenCLI live-start preflight SHALL require install receipt, owner evidence, and port lease evidence

repository-local OpenCLI governance guard 必须提供非变更型 live-start preflight；如果缺少有效 OpenCLI install receipt evidence、active browser-owner lease evidence，或 Codex browser/OpenCLI range 内 sanitized codex-port `--port auto` lease evidence，必须 fail closed。

即使证据齐全，repo-local MVP 也不得启动 OpenCLI；必须返回 `live_start_not_implemented_repo_local_mvp` 与 `start_performed=false`。

#### Scenario: OpenCLI live start lacks install receipt

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> start --target tab:opencli-1 --session session-a --owner-lease-id <lease> --port-lease-receipt <receipt> --json` 在没有 install receipt 的情况下运行
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `install_receipt_required`
- **AND** 必须报告 `start_performed=false`

#### Scenario: OpenCLI live start lacks owner evidence

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> start --target tab:opencli-1 --session session-a --install-receipt <receipt> --port-lease-receipt <receipt> --json` 在没有 owner evidence 的情况下运行
- **THEN** 命令必须 fail closed
- **AND** blockers 必须包含 `owner_lease_required`
- **AND** 必须报告 `install_receipt_verified=true`

#### Scenario: OpenCLI live start has complete evidence but remains deferred

- **WHEN** OpenCLI live-start preflight 收到有效 install receipt、owner lease 与 port lease evidence
- **THEN** 命令必须以 `live_start_not_implemented_repo_local_mvp` fail closed
- **AND** 必须报告 `start_performed=false`
- **AND** 不得 install OpenCLI、start OpenCLI、launch browser、connect to browser target 或 mutate user-level Codex configuration
