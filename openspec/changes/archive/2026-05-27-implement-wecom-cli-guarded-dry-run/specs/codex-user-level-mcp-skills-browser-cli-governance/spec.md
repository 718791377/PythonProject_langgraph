# Delta: WeCom CLI Guarded Dry-Run

## ADDED Requirements

### Requirement: WeCom CLI governance guard SHALL prefer API/Webhook and fail closed for WXWork GUI automation

The repository SHALL provide a repo-local `wecom-cli` governance guard that models Enterprise WeChat / WeCom / WXWork control boundaries without attaching to `WXWork.exe`, probing local processes, calling live APIs or webhooks, reading message content, sending messages, mutating user-level Codex configuration, or controlling GUI state.

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
