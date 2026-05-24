## ADDED Requirements

### Requirement: CDP Bridge governance guard SHALL keep read-only defaults and fail closed sensitive actions

The repository SHALL provide a repo-local CDP Bridge governance guard that classifies CDP Bridge actions before any live browser dispatch can occur.

The guard SHALL treat read-only inventory actions as allowed without browser-owner or authorization evidence. The read-only inventory actions SHALL include `tab.list`, `dom.scan`, `screenshot.capture`, and `inventory`.

The guard SHALL treat cookie reads, JavaScript execution, click, type, navigation, and unknown actions as sensitive. Sensitive actions SHALL require both active browser-owner lease evidence and a current one-task authorization receipt before dispatch is allowed.

The guard SHALL be non-mutating. It SHALL NOT launch Chrome, connect to CDP, read cookies, execute JavaScript, click, type, navigate, mutate user-level Codex configuration, or emit raw private profile paths.

#### Scenario: Read-only tab inventory is allowed without owner evidence

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action tab.list --target tab:debug-1 --session session-a --json` runs without an owner registry or authorization receipt
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `authorization_required=false`
- **AND** it SHALL report `owner_required=false`
- **AND** it SHALL report `connects_to_cdp=false`

#### Scenario: Cookie reads fail closed without evidence

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action cookie.read --target tab:debug-1 --session session-a --json` runs without owner lease evidence or authorization receipt evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL include `authorization_receipt_required` in blockers
- **AND** it SHALL report `reads_cookies=false`

#### Scenario: JavaScript execution requires active owner lease and authorization receipt

- **WHEN** `python tools/cdp_bridge_governance.py --state-dir <tmp> check --action js.evaluate --target tab:debug-1 --session session-a --owner-lease-id <lease> --authorization-receipt <receipt> --json` runs with matching active owner lease evidence and current one-task authorization receipt evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `authorization_verified=true`
- **AND** it SHALL report `executes_javascript=false`

#### Scenario: Click, type, navigation, and unknown actions are sensitive by default

- **WHEN** the guard checks `mouse.click`, `keyboard.type`, `page.navigate`, or an unknown action without owner and authorization evidence
- **THEN** each check SHALL fail closed
- **AND** each check SHALL report `dispatch_allowed=false`
- **AND** each check SHALL require owner lease evidence
- **AND** each check SHALL require authorization receipt evidence
