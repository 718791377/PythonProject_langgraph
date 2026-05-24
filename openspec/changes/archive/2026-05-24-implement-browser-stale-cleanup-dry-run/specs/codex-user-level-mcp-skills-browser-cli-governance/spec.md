## ADDED Requirements

### Requirement: Chrome DevTools MCP managed wrapper MVP SHALL expose safe stale scan and cleanup dry-run

The repository-local `chrome-devtools-mcp` managed wrapper MVP SHALL expose browser stale scan and safe cleanup dry-run commands that delegate to the browser owner registry.

The wrapper SHALL support at least:

- `stale-scan --dry-run --json` - previews stale browser owner-registry leases without mutation;
- `cleanup dry-run --json` - previews safe cleanup candidates without deleting profiles.

Both commands SHALL be non-mutating dry runs in the repo-local MVP. They SHALL NOT launch Chrome, connect to CDP, mutate user-level Codex configuration, read cookies, delete browser profiles, or clean up human-owned or project-profile assets.

#### Scenario: Wrapper stale-scan delegates to owner registry without mutation

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> stale-scan --dry-run --json` runs with expired isolated and project-profile leases in registry state
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL report `dry_run=true`
- **AND** it SHALL report `registry_mutated=false`
- **AND** it SHALL report `cleanup_performed=false`
- **AND** it SHALL list sanitized stale candidates without raw private profile paths

#### Scenario: Wrapper cleanup dry-run protects project and human-owned assets

- **WHEN** `python tools/chrome_devtools_mcp_managed.py --state-dir <tmp> cleanup dry-run --json` runs with expired isolated, project-profile, and human-delegated leases in registry state
- **THEN** only expired `codex-managed-isolated` leases SHALL appear as cleanup candidates
- **AND** project-profile or human-delegated leases SHALL appear as protected profiles
- **AND** `cleanup_performed` SHALL be `false`
- **AND** `human_owned_cleanup_performed` SHALL be `false`
- **AND** `deleted_profiles` SHALL be empty
