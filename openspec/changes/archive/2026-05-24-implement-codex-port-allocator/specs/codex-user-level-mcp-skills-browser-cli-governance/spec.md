## ADDED Requirements

### Requirement: Codex-port allocator MVP SHALL provide range-aware port leases

The repository SHALL provide a repo-local `codex-port` helper and range registry for compact, deterministic port lease governance.

The helper SHALL support at least:

- `lease reserve --owner <owner> --project <slug> --tool <tool> --range <range-name> --purpose <text> --ttl <seconds> --json`;
- `lease renew --lease-id <id> --owner-session <session-id> --ttl <seconds> --json`;
- `lease release --owner-session <session-id> --port <port> --json`;
- `lease list --owner <owner> --json`;
- `lease import-legacy --owner openclaw --port <port> --purpose <text> --json`;
- `lease gc --dry-run --json` for read-only stale-candidate inspection.

The allocator SHALL preserve Codex ranges before the external project range: Codex helper ports `39000-39299`, Codex OpenCLI ports `39300-39499`, Codex browser-automation ports `39500-39699`, Codex reserved ports `39700-39999`, and external project ports `40000-40999`.

#### Scenario: Codex reserves a helper port

- **WHEN** `python tools/codex_port.py lease reserve --owner codex --project pythonproject-langgraph --tool mcp2cli --range codex-helper --purpose test --ttl 300 --json` runs against an empty registry
- **THEN** the command SHALL return `ok=true`
- **AND** it SHALL allocate the first available Codex helper port
- **AND** it SHALL write a `pending_bind` lease with `registry_revision` evidence
- **AND** it SHALL write a sanitized reserve receipt

#### Scenario: Owner requests another owner range

- **WHEN** `python tools/codex_port.py lease reserve --owner codex --range openclaw --json` is requested
- **THEN** the command SHALL fail closed with an owner/range mismatch
- **AND** it SHALL NOT mutate the registry

#### Scenario: Live local socket already occupies a port

- **WHEN** a live socket already occupies the first candidate port in the requested range
- **AND** `codex-port lease reserve` runs
- **THEN** the allocator SHALL skip the occupied port
- **AND** it SHALL report a collision warning
- **AND** it SHALL NOT kill, attach to, or otherwise mutate the existing process

### Requirement: Codex-port lease lifecycle SHALL preserve ownership, stale evidence, and receipts

The repository-local `codex-port` helper SHALL require lease ownership evidence for write lifecycle actions and SHALL preserve crash/stale evidence before reusing stale ports.

#### Scenario: Lease renew promotes a bound pending lease

- **WHEN** `codex-port lease renew --lease-id <id> --owner-session <session-id> --ttl <seconds> --activate --json` runs for a matching owner session
- **THEN** the lease SHALL be renewed
- **AND** a `pending_bind` lease MAY be promoted to `active`
- **AND** a sanitized renew receipt SHALL be written

#### Scenario: Release owner session does not match

- **WHEN** `codex-port lease release --owner-session <different-session> --port <port> --json` runs
- **THEN** the release SHALL fail closed
- **AND** the existing lease SHALL remain unreleased

#### Scenario: Legacy openclaw-owner port is imported

- **WHEN** `codex-port lease import-legacy --owner openclaw --port 40000 --purpose <text> --json` runs
- **THEN** the registry SHALL record a `legacy_reserved` lease
- **AND** later Codex allocation SHALL NOT consume that external project range

#### Scenario: Garbage collection is dry-run

- **WHEN** `codex-port lease gc --dry-run --json` runs
- **THEN** stale or expired leases SHALL be reported as candidates
- **AND** the registry SHALL NOT be mutated
- **AND** no process SHALL be killed
