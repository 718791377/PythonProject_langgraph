# codex-user-level-mcp-skills-browser-cli-governance Specification

## Purpose

This specification preserves the script-backed baseline governance requirements for user-level MCP, skills, browser automation, and CLI harness surfaces. It keeps Token/risk priority, authorization receipt, update receipt, evidence redaction, port registry/lease, OpenSpec slice, and fail closed rules visible before the later `skills2cli`, `mcp2cli`, browser, and `wecom-cli` implementation slices land.
## Requirements
### Requirement: User-level MCP skills browser CLI baseline SHALL be script-backed

The repository SHALL maintain an executable baseline checker for the user-level MCP, skills, browser automation, and CLI harness governance plan.

The checker SHALL validate that repository-owned plan and OpenSpec surfaces preserve token/risk priority, lane default states, sensitive authorization receipt fields, user-level tool update receipt fields, evidence redaction rules, and OpenSpec slice completion markers.

#### Scenario: Baseline checker runs in the repository guard

- **WHEN** `python tools/run_openspec_guard.py --root . --json` runs
- **THEN** the aggregate guard SHALL include `check_user_level_mcp_skills_browser_cli_baseline`
- **AND** the checker SHALL pass only when the baseline governance surfaces are present

#### Scenario: Authorization receipt evidence is incomplete

- **WHEN** the baseline checker scans the implementation plan
- **AND** action, target, scope, expiry, session, or operator confirmation evidence is absent
- **THEN** the checker SHALL fail closed

#### Scenario: Update receipt evidence is incomplete

- **WHEN** the baseline checker scans the implementation plan
- **AND** install path, wrapper path, state path, pin/version, smoke command, updater command, rollback pointer, or owner lane evidence is absent
- **THEN** the checker SHALL fail closed

### Requirement: User-level port governance SHALL be preserved before allocator implementation

The baseline checker SHALL validate that the repository-owned plan and OpenSpec surfaces preserve the port registry/lease contract for Codex, the later external project range, OpenCLI, and managed browser automation.

The preserved contract SHALL include the Codex `39000-39299` helper range, the broader Codex `39000-39999` owner block, the later external `40000-40999` owner range, `codex-port` allocator ownership (codex-port allocator), allocator-driven OpenCLI `--port auto`, `pending_bind` provisional leases, `registry_revision` concurrency evidence, live-socket collision skipping, stale/crash evidence, and the rule that port governance never kills existing processes.

#### Scenario: Port-governance markers are removed

- **WHEN** the baseline checker scans the repository-owned plan and spec surfaces
- **AND** port registry/lease, `codex-port` allocator, `pending_bind`, `registry_revision`, owner ranges including `39000-39299` and `40000-40999`, or OpenCLI `--port auto` evidence is missing
- **THEN** the checker SHALL fail closed
- **AND** the operator SHALL restore the port-governance contract before committing

### Requirement: User-level MCP skills browser CLI evidence SHALL remain sanitized

Repository evidence for this plan SHALL NOT retain secrets, cookies, tokens, raw browser data, message contents, full personal runtime paths, or complete plugin description dumps.

#### Scenario: Evidence redaction markers are removed

- **WHEN** the baseline checker scans the repository-owned plan and spec surfaces
- **AND** the evidence redaction boundary is missing
- **THEN** the checker SHALL fail
- **AND** the operator SHALL restore the sanitized-evidence boundary before committing

### Requirement: User-level MCP skills browser CLI slices SHALL not become active without evidence

Each implementation slice SHALL remain `planned`, `implemented-local`, `installed-user-level`, or `smoke-tested` until implementation, tests, CI registration, OpenSpec updates, rollback evidence, and completed receipts are present.

#### Scenario: A slice has only documentation or research

- **WHEN** the slice lacks implementation, test, CI registration, rollback evidence, or completed receipt evidence
- **THEN** it SHALL NOT be marked `active`
- **AND** the baseline checker SHALL require the plan to preserve slice completion rules

### Requirement: Skills2cli MVP SHALL provide compact sanitized skill discovery

The repository SHALL provide a repo-local `skills2cli` helper that indexes available Codex skill metadata without dumping full skill bodies, private paths, secrets, cookies, tokens, raw browser data, or complete plugin description dumps in default output.

The helper SHALL support at least:

- `index --json` for compact skill inventory metadata;
- `search <query> --json` for compact query results;
- `show <skill-id> --json` for compact per-skill metadata.

Default metadata SHALL include skill id, source layer, sanitized location hint, short description summary, description hash, frontmatter validity, and availability status.

#### Scenario: Compact index output is requested

- **WHEN** `python tools/skills2cli.py index --json` runs
- **THEN** the JSON output SHALL contain compact skill metadata
- **AND** it SHALL NOT contain full skill bodies or complete plugin description dumps
- **AND** it SHALL keep private filesystem paths sanitized

#### Scenario: Search output is requested

- **WHEN** `python tools/skills2cli.py search browser --json` runs
- **THEN** matching results SHALL contain compact summaries and sanitized location hints
- **AND** the output SHALL NOT include full SKILL.md bodies by default

#### Scenario: Show output is requested without full expansion

- **WHEN** `python tools/skills2cli.py show <skill-id> --json` runs
- **THEN** the result SHALL report `full_body_included=false`
- **AND** the output SHALL remain compact and sanitized

### Requirement: Skills2cli profile suggestion SHALL be preview-only

The repository-local `skills2cli profile suggest --task <text> --json` command SHALL recommend candidate profiles/modules without applying them, editing user-level configuration, or editing plugin cache files.

#### Scenario: Profile suggestion is requested

- **WHEN** `python tools/skills2cli.py profile suggest --task "browser debugging" --json` runs
- **THEN** the result SHALL include profile/module suggestions
- **AND** `mutates_config` SHALL be `false`
- **AND** `profile_apply_performed` SHALL be `false`
- **AND** `approval_required_for_apply` SHALL be `true`

### Requirement: Skills2cli warning audit SHALL summarize budget and skipped-loading warnings

The repository-local `skills2cli audit warnings --since <duration> --json` command SHALL summarize Codex skills context budget warnings and skipped-loading warnings from available session logs without retaining raw log paths or private path details.

#### Scenario: Warning audit finds warning lines

- **WHEN** Codex session logs contain `Exceeded skills context budget of 2%` or `Skipped loading` warning text
- **AND** `python tools/skills2cli.py audit warnings --since 7d --json` runs
- **THEN** the result SHALL include budget-warning and skipped-loading counts
- **AND** recent excerpts SHALL be sanitized
- **AND** raw log paths SHALL NOT be retained


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

