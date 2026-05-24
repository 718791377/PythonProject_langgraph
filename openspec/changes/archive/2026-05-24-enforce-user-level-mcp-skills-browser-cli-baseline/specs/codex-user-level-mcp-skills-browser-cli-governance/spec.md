## ADDED Requirements

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
