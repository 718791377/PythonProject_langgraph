# codex-user-level-mcp-scope-policy Specification

## Purpose
TBD - created by archiving change formalize-mcp-router-scope-policy. Update Purpose after archive.
## Requirements
### Requirement: Codex-dedicated MCP servers SHALL remain direct Codex servers

Codex-dedicated MCP servers SHALL remain configured directly for Codex and SHALL NOT be managed through MCP Router as shared server entries.

Codex-dedicated MCP servers include `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace`.

#### Scenario: Codex starts with oh-my-codex enabled
- **WHEN** Codex starts with the oh-my-codex layer enabled
- **THEN** `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` SHALL be available as direct Codex MCP servers
- **AND** those servers SHALL NOT be required to pass through MCP Router

#### Scenario: MCP Router is audited
- **WHEN** MCP Router managed server records are audited
- **THEN** active records for `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace` SHALL be reported as drift
- **AND** the operator SHALL be directed to keep those servers Codex-dedicated

### Requirement: Shared utility MCP servers SHALL be eligible for MCP Router management

Cross-client utility MCP servers SHALL be eligible for MCP Router management when multiple clients need the same capability and the server does not own Codex orchestration state.

Shared utility MCP servers include `chrome-devtools` and `pencil`.

#### Scenario: Browser and design MCP servers are shared
- **WHEN** `chrome-devtools` or `pencil` is managed by MCP Router
- **THEN** the corresponding direct Codex server entry SHALL be disabled or absent
- **AND** Codex SHALL access that capability through the MCP Router bridge

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
- **THEN** active MCP Router records for Codex-dedicated servers SHALL be blocking errors
- **AND** active Router self-reference records SHALL be blocking errors

