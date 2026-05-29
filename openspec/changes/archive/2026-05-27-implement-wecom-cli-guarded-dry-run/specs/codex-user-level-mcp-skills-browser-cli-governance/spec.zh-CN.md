# Delta：wecom-cli 受治理 dry-run

## ADDED Requirements

### Requirement: WeCom CLI governance guard SHALL prefer API/Webhook and fail closed for WXWork GUI automation

仓库 SHALL 提供 repo-local `wecom-cli` governance guard，用于建模企业微信 / WeCom / WXWork 控制边界；不得 attach `WXWork.exe`、探测本地进程、调用 live API 或 webhook、读取消息内容、发送消息、修改用户级 Codex 配置或控制 GUI 状态。

#### Scenario: API/Webhook status is requested

- **WHEN** `python tools/wecom_cli_governance.py api-status --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `api_or_webhook_first`
- **AND** it SHALL report no process probe, no GUI control, no message-content read, and no WeCom API call

#### Scenario: GUI attach lacks receipts

- **WHEN** `python tools/wecom_cli_governance.py gui-check --action gui.attach --session session-a --json` runs without receipts
- **THEN** the command SHALL fail closed
- **AND** it SHALL require both operator authorization receipt and global WXWork lease receipt
- **AND** it SHALL report `gui_control_performed=false`
