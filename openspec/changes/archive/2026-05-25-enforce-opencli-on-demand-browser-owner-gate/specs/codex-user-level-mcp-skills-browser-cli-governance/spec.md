# Delta: OpenCLI on-demand owner-registry gate

## ADDED Requirements

### Requirement: OpenCLI governance guard SHALL remain on-demand and require browser owner evidence

The repository SHALL provide a repo-local OpenCLI governance guard that evaluates browser-target actions before any live OpenCLI dispatch can occur.

The guard SHALL keep OpenCLI as an on-demand adapter. Any request that attempts always-on or persistent adapter mode SHALL fail closed.

The guard SHALL require active browser-owner lease evidence for every target-bound OpenCLI action, including read-only inspection. The read-only actions SHALL include `adapter.inventory`, `session.inspect`, `page.snapshot`, and `screenshot.capture`.

The guard SHALL treat cookie reads, JavaScript execution, click, type, navigation, and unknown actions as sensitive. Sensitive actions SHALL require both active browser-owner lease evidence and a current one-task authorization receipt before dispatch is allowed.

The guard SHALL be non-mutating. It SHALL NOT install OpenCLI, start OpenCLI, launch browsers, connect to browser targets, read cookies, execute JavaScript, click, type, navigate, mutate user-level Codex configuration, or emit raw private profile paths.

#### Scenario: Read-only inspection requires a browser-owner lease

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> check --action session.inspect --target tab:opencli-1 --session session-a --json` runs without owner lease evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL report `authorization_required=false`

#### Scenario: Read-only inspection is allowed with an active owner lease

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> check --action session.inspect --target tab:opencli-1 --session session-a --owner-lease-id <lease> --json` runs with matching active owner lease evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `adapter_mode=on-demand`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `connects_to_browser=false`

#### Scenario: Always-on adapter mode is blocked

- **WHEN** the guard checks an OpenCLI action with `--adapter-mode always-on`
- **THEN** the command SHALL fail closed
- **AND** it SHALL include `opencli_must_remain_on_demand` in blockers
- **AND** it SHALL report `autoload_allowed=false`

#### Scenario: Cookie reads fail closed without evidence

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> check --action cookie.read --target tab:opencli-1 --session session-a --json` runs without owner lease evidence or authorization receipt evidence
- **THEN** the command SHALL return a non-zero exit code
- **AND** it SHALL report `dispatch_allowed=false`
- **AND** it SHALL include `owner_lease_required` in blockers
- **AND** it SHALL include `authorization_receipt_required` in blockers
- **AND** it SHALL report `reads_cookies=false`

#### Scenario: JavaScript execution requires active owner lease and authorization receipt

- **WHEN** `python tools/opencli_governance.py --state-dir <tmp> --owner-state-dir <owner-state> check --action js.evaluate --target tab:opencli-1 --session session-a --owner-lease-id <lease> --authorization-receipt <receipt> --json` runs with matching active owner lease evidence and current one-task authorization receipt evidence
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dispatch_allowed=true`
- **AND** it SHALL report `owner_verified=true`
- **AND** it SHALL report `authorization_verified=true`
- **AND** it SHALL report `executes_javascript=false`

#### Scenario: Click, type, navigation, and unknown actions are sensitive by default for OpenCLI

- **WHEN** the guard checks `mouse.click`, `keyboard.type`, `page.navigate`, or an unknown OpenCLI action without owner and authorization evidence
- **THEN** each check SHALL fail closed
- **AND** each check SHALL report `dispatch_allowed=false`
- **AND** each check SHALL require owner lease evidence
- **AND** each check SHALL require authorization receipt evidence
