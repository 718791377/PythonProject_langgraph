## MODIFIED Requirements

### Requirement: MCP scope policy SHALL have script-backed validation

The MCP scope policy checker SHALL allow the Codex `mcp_router` bridge to be disabled only when a repository-owned active exception declares the reason and recovery condition.

The checker SHALL continue to fail when `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace` are missing or disabled in Codex direct configuration.

#### Scenario: Resume-stability exception is active

- **WHEN** the Codex `mcp_router` bridge is disabled
- **AND** `tools/mcp_router_scope_policy_exceptions.json` contains an active `codex_mcp_router_bridge_disabled` exception with a reason and recovery condition
- **THEN** the checker SHALL report a warning rather than a blocking error
- **AND** the checker output SHALL include the exception identifier

#### Scenario: Disabled bridge has no declared exception

- **WHEN** the Codex `mcp_router` bridge is disabled
- **AND** no active `codex_mcp_router_bridge_disabled` exception is declared
- **THEN** the checker SHALL fail

#### Scenario: Codex-dedicated MCP server is disabled during a bridge exception

- **WHEN** a resume-stability exception exists for the Codex `mcp_router` bridge
- **AND** `omx_state`, `omx_memory`, `omx_code_intel`, or `omx_trace` is missing or disabled
- **THEN** the checker SHALL fail
