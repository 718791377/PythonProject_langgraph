## ADDED Requirements

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL gate project profiles

The repository SHALL extend the repo-local `chrome-devtools-mcp` managed wrapper MVP with project-profile browser automation contracts.

The wrapper SHALL support at least:

- `project-profile plan --project <slug> --profile <name> --session <id> --purpose <text> --json`;
- `project-profile reserve --project <slug> --profile <name> --session <id> --purpose <text> --authorization-receipt <path> --ttl <seconds> --json`;
- `project-profile start --project <slug> --profile <name> --session <id> --purpose <text> [--dry-run] [--authorization-receipt <path>] [--install-receipt <path>] --json`;
- `project-profile release --lease-id <id> --session <id> --json`;
- `project-profile status --json`, which lists sanitized managed project-profile lease state.

Project profiles SHALL use the `codex-managed-project` owner class, SHALL be long-lived project assets, SHALL require a current project-profile authorization receipt before reserve or live start, and SHALL NOT be cleanup candidates in the repo-local MVP.

The repo-local MVP SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, write human-owned profiles, or perform live `chrome-devtools-mcp` startup.

#### Scenario: Project-profile plan is a non-mutating dry run

- **WHEN** `python tools/chrome_devtools_mcp_managed.py project-profile plan --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --json` runs
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL report `owner_class=codex-managed-project`
- **AND** it SHALL report `profile_retention=long-lived-project-profile`
- **AND** it SHALL report `cleanup_allowed_after_stale_evidence=false`
- **AND** it SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Project-profile reserve lacks authorization

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile reserve --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --json` runs without an authorization receipt
- **THEN** the command SHALL fail closed
- **AND** it SHALL report authorization receipt evidence is required
- **AND** it SHALL NOT mutate browser owner registry state
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Project-profile reserve writes protected ownership evidence

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile reserve --project pythonproject-langgraph --profile dev-login --session session-a --purpose test --authorization-receipt <path> --json` runs with a current matching authorization receipt
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL write an active `codex-managed-project` owner lease through the browser owner registry
- **AND** it SHALL write a sanitized wrapper receipt
- **AND** it SHALL report project-profile cleanup is not allowed
- **AND** it SHALL NOT start Chrome or connect to CDP

#### Scenario: Same project profile is already owned

- **WHEN** an active `codex-managed-project` lease already controls a project profile
- **AND** another session requests the same project profile or target
- **THEN** the wrapper SHALL fail closed through the browser owner registry
- **AND** it SHALL NOT overwrite the existing lease

#### Scenario: Project-profile live start is gated before repo-local deferral

- **WHEN** `project-profile start` runs without a current matching project-profile authorization receipt
- **THEN** the command SHALL fail closed before checking install receipt state
- **AND** it SHALL report `start_performed=false`

- **WHEN** `project-profile start` runs with a current matching project-profile authorization receipt but without an install receipt
- **THEN** the command SHALL fail closed with `install_receipt_required`
- **AND** it SHALL report `start_performed=false`

- **WHEN** `project-profile start` runs with both a current matching project-profile authorization receipt and an install receipt
- **THEN** the command SHALL still fail closed with `live_start_not_implemented_repo_local_mvp`
- **AND** it SHALL report `start_performed=false`
- **AND** it SHALL NOT mutate browser owner registry state

#### Scenario: Project-profile release delegates to owner registry

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> project-profile release --lease-id <id> --session session-a --json` runs for a matching active project-profile lease
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL mark the owner lease as released through the browser owner registry
- **AND** it SHALL write a sanitized project-profile wrapper release receipt
