# codex-user-level-mcp-scope-policy Specification

## Purpose

Define the user-level MCP server boundary between Codex direct MCP servers and MCP Router servers used by non-Codex clients.

## Requirements

### Requirement: Codex-private MCP servers SHALL remain direct Codex servers

Codex-private MCP servers SHALL remain configured directly for Codex and SHALL NOT be managed through MCP Router as shared server entries.

Codex-private MCP servers include `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace`.

#### Scenario: Codex starts with oh-my-codex enabled

- **WHEN** Codex starts with the oh-my-codex layer enabled
- **THEN** `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` SHALL be available as direct Codex MCP servers
- **AND** those servers SHALL NOT be required to pass through MCP Router

#### Scenario: MCP Router is audited

- **WHEN** MCP Router managed server records are audited
- **THEN** active records for `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace` SHALL be reported as drift
- **AND** the operator SHALL be directed to keep those servers Codex-private

### Requirement: Browser and design MCP servers SHALL remain direct Codex utility servers

Codex SHALL use browser and design MCP capabilities through direct Codex MCP entries instead of the Codex-side `mcp_router` bridge.

Codex direct utility MCP servers include `chrome-devtools` and `pencil`.

`chrome-devtools` is the browser debugging MCP server for browser pages, DOM snapshots, screenshots, console data, and network inspection.

`pencil` is the design MCP server for Pencil design documents, visual variables, node reads, and exports.

#### Scenario: Codex browser and design tools are configured

- **WHEN** local Codex configuration is audited
- **THEN** `chrome-devtools` and `pencil` SHALL be enabled as direct Codex MCP servers
- **AND** Codex SHALL NOT require MCP Router to access those capabilities

#### Scenario: MCP Router also serves non-Codex clients

- **WHEN** MCP Router contains `chrome-devtools` or `pencil` for Trae, VS Code, PyCharm, or another non-Codex client
- **THEN** that Router state SHALL NOT count as Codex access
- **AND** Codex SHALL continue using the corresponding direct Codex MCP entries

### Requirement: Codex SHALL keep the MCP Router bridge disabled by default

The Codex-side `mcp_router` bridge SHALL be disabled or absent by default.

Codex SHALL NOT load MCP Router's full tool catalog during normal startup.

Re-enabling the Codex-side `mcp_router` bridge SHALL require a future approved governance change that defines a bounded Codex-specific Router profile and validates `tools/list` size, resume startup, and direct-MCP fallback behavior.

#### Scenario: Codex configuration is audited

- **WHEN** the Codex `mcp_router` bridge is disabled or absent
- **THEN** the checker SHALL pass that bridge state
- **AND** the checker SHALL not require a temporary exception for the disabled bridge

#### Scenario: Codex MCP Router bridge is enabled

- **WHEN** the Codex `mcp_router` bridge is enabled
- **THEN** the checker SHALL fail
- **AND** the operator SHALL be directed to use direct Codex MCP entries instead

### Requirement: MCP Router SHALL NOT manage itself

MCP Router SHALL NOT contain a managed server entry for `mcp-router`, `mcp_router`, or another Router self-reference.

#### Scenario: Router self-reference is detected

- **WHEN** MCP Router managed server records contain `mcp-router` or `mcp_router`
- **THEN** the checker SHALL report self-reference drift
- **AND** the operator SHALL remove or disable the self-referential Router server entry

### Requirement: MCP scope policy SHALL have script-backed validation

The MCP scope policy SHALL be backed by an executable checker that can validate local Codex configuration and report MCP Router drift.

#### Scenario: Repository guard runs without user-level runtime files

- **WHEN** the repository guard runs in CI or another environment without user-level Codex or MCP Router files
- **THEN** the checker SHALL skip local runtime validation with informational output
- **AND** the guard SHALL continue to validate repository-owned policy artifacts

#### Scenario: Strict local audit is requested

- **WHEN** the operator runs the checker with strict Router-state validation
- **THEN** active MCP Router records for Codex-private servers SHALL be blocking errors
- **AND** active Router self-reference records SHALL be blocking errors

#### Scenario: Codex direct MCP server is disabled

- **WHEN** `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `chrome-devtools`, or `pencil` is missing or disabled in local Codex configuration
- **THEN** the checker SHALL fail
