## ADDED Requirements

### Requirement: Legacy Resume MCP Workarounds SHALL Be Scoped Per Invocation

Legacy resumed Codex sessions SHALL keep temporary per-invocation MCP overrides scoped to the affected old thread when a stale old thread cannot start cleanly.

A per-invocation MCP override is a one-launch Codex config override such as `-c "mcp_servers.omx_code_intel.enabled=false"`.

Such overrides SHALL NOT be treated as permission to permanently disable Codex-private MCP servers or to edit user-level Codex configuration as the default fix.

#### Scenario: A legacy old thread fails on one direct MCP server

- **GIVEN** a legacy resumed session fails because of stale direct MCP startup state
- **WHEN** the operator continues that old thread
- **THEN** a per-invocation override MAY disable the affected server for that launch only
- **AND** the direct MCP policy for new sessions SHALL remain unchanged

#### Scenario: A new wrapped session starts normally

- **GIVEN** oh-my-codex is enabled for normal work
- **WHEN** a new wrapped session starts
- **THEN** `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `chrome-devtools`, and `pencil` SHALL remain governed by the direct Codex MCP policy
- **AND** a legacy workaround SHALL NOT remove those servers globally
