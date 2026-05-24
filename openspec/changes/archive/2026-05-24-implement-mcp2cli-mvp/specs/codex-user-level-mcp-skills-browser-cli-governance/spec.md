## ADDED Requirements

### Requirement: Mcp2cli MVP SHALL provide compact allowed-profile discovery

The repository SHALL provide a repo-local `mcp2cli` helper and allowed-profile registry for compact MCP tool discovery.

The helper SHALL support at least:

- `list --profile <profile> --json` for compact profile tool inventory;
- `search <query> --profile <profile> --json` for compact query results;
- `show <tool> --profile <profile> --json` for compact per-tool metadata.

Default output SHALL include only compact, sanitized profile/tool metadata and SHALL NOT dump full tool schemas, secrets, cookies, tokens, raw browser data, full personal runtime paths, or complete private configuration details.

#### Scenario: Compact MCP profile list is requested

- **WHEN** `python tools/mcp2cli.py list --profile core-readonly --json` runs
- **THEN** the JSON output SHALL contain compact allowed tool metadata
- **AND** the output SHALL report `compact_output=true`
- **AND** the output SHALL NOT include full schemas by default

#### Scenario: Compact MCP search is requested

- **WHEN** `python tools/mcp2cli.py search browser --profile browser-readonly --json` runs
- **THEN** matching results SHALL contain compact summaries and risk metadata
- **AND** full tool schemas SHALL remain excluded by default

### Requirement: Mcp2cli MVP call facade SHALL fail closed for sensitive calls

The repository-local `mcp2cli call` command SHALL evaluate allowed profile registry metadata before any call result is emitted.

Tools with sensitive categories, medium/high/critical risk, or `requires_authorization=true` SHALL fail closed unless a matching authorization receipt is supplied.

#### Scenario: Sensitive call lacks authorization receipt

- **WHEN** `python tools/mcp2cli.py call browser.tabs.list --profile browser-readonly --json --args {}` runs without a receipt
- **THEN** the result SHALL report `ok=false`
- **AND** it SHALL report `blocked=true`
- **AND** it SHALL report `receipt_required=true`
- **AND** it SHALL report `call_performed=false`

#### Scenario: Authorization receipt is incomplete

- **WHEN** `mcp2cli call` receives an authorization receipt missing action, target, scope, expiry, session, or operator confirmation
- **THEN** the command SHALL fail closed
- **AND** the result SHALL include sanitized blocker codes instead of raw private receipt contents

#### Scenario: Low-risk allowed call is requested

- **WHEN** `python tools/mcp2cli.py call repo.openspec.list --profile core-readonly --json --args {}` runs
- **THEN** the result SHALL remain local and deterministic
- **AND** it SHALL not invoke a live external MCP server
- **AND** it SHALL report the call facade result without requiring a sensitive authorization receipt
