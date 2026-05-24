# codex-user-level-mcp-skills-browser-cli-governance Delta Spec

### Requirement: Browser owner registry MVP SHALL coordinate browser automation ownership

The repository SHALL provide a repo-local browser owner registry helper that records browser automation ownership without launching Chrome, connecting to CDP, or mutating user-level Codex configuration.

The helper SHALL support at least:

- `lease reserve --owner-class <class> --project <slug> --session <id> --target <target> --profile-path <path> --purpose <text> --ttl <seconds> --json`;
- `lease renew --lease-id <id> --session <id> --ttl <seconds> --json`;
- `lease release --lease-id <id> --session <id> --json`;
- `lease list --json`;
- `stale-scan --dry-run --json`;
- Cleanup dry-run command: `cleanup dry-run --json`, used only to preview safe cleanup candidates without deleting browser profiles.

The registry SHALL preserve owner class, project slug, session id, target, sanitized profile-path evidence, profile-path hash, lease expiry, status, and receipt evidence for write actions.

#### Scenario: Isolated managed browser lease is reserved

- **WHEN** `python tools/browser_owner_registry.py lease reserve --owner-class codex-managed-isolated --project pythonproject-langgraph --session session-a --target tab:debug --profile-path <path> --purpose test --ttl 300 --json` runs against an empty registry
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL record an active managed isolated lease
- **AND** it SHALL write a sanitized reserve receipt
- **AND** default output SHALL include a profile-path hash rather than a raw private profile path

#### Scenario: Project profile lacks authorization

- **WHEN** `browser_owner_registry.py lease reserve` is requested for `codex-managed-project` without a current one-task authorization receipt
- **THEN** the command SHALL fail closed
- **AND** no lease SHALL be recorded

#### Scenario: Same target is already owned

- **WHEN** an active lease already owns the requested browser target
- **AND** another lease reserve request names the same target
- **THEN** the command SHALL fail closed with target ownership evidence
- **AND** it SHALL NOT overwrite the existing lease

### Requirement: Browser cleanup dry-run SHALL protect project and human-owned assets

The browser owner registry helper SHALL keep cleanup as dry-run only in the repo-local MVP and SHALL never treat project profiles or human-owned browser assets as cleanup candidates.

#### Scenario: Cleanup dry-run sees stale leases

- **WHEN** stale leases include a `codex-managed-isolated` profile and a `codex-managed-project` profile
- **AND** `python tools/browser_owner_registry.py cleanup dry-run --json` runs
- **THEN** only the stale `codex-managed-isolated` profile SHALL be listed as a cleanup candidate
- **AND** the stale project profile SHALL be listed as protected
- **AND** `cleanup_performed` SHALL be `false`
- **AND** `human_owned_cleanup_performed` SHALL be `false`
