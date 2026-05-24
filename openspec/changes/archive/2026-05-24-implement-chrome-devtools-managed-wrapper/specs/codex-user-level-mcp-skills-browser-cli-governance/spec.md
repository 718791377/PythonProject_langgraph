# codex-user-level-mcp-skills-browser-cli-governance Delta Spec

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate isolated sessions

The repository SHALL provide a repo-local `chrome-devtools-mcp` managed wrapper MVP for isolated-session browser automation contracts.

The wrapper SHALL support at least:

- `isolated-session plan --project <slug> --session <id> --purpose <text> --json`;
- `isolated-session reserve --project <slug> --session <id> --purpose <text> --ttl <seconds> --json`;
- `isolated-session start --project <slug> --session <id> --purpose <text> [--dry-run] [--install-receipt <path>] --json`;
- `isolated-session release --lease-id <id> --session <id> --json`;
- `isolated-session status --json`, which lists sanitized managed isolated lease state.

The wrapper SHALL coordinate with the browser owner registry, SHALL sanitize default output, and SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, or write human-owned profiles in the repo-local MVP.

#### Scenario: Isolated-session plan is a non-mutating dry run

- **WHEN** `python tools/chrome_devtools_mcp_managed.py isolated-session plan --project pythonproject-langgraph --session session-a --purpose test --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Isolated-session reserve writes managed ownership evidence

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session reserve --project pythonproject-langgraph --session session-a --purpose test --ttl 120 --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write an active `codex-managed-isolated` owner lease through the browser owner registry
- **AND** it SHALL write a sanitized wrapper receipt
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Live start lacks install receipt

- **WHEN** `python tools/chrome_devtools_mcp_managed.py isolated-session start --project pythonproject-langgraph --session session-a --purpose test --json` runs without an install receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report `install_receipt_required`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL NOT mutate browser owner registry state

#### Scenario: Isolated-session release delegates to owner registry

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> isolated-session release --lease-id <id> --session session-a --json` runs for a matching active lease
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL mark the owner lease as released through the browser owner registry
- **AND** it SHALL write a sanitized wrapper release receipt
