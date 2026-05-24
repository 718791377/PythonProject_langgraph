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

