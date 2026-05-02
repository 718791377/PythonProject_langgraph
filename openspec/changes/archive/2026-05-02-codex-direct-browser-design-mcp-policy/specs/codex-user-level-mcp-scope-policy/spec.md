## MODIFIED Requirements

### Requirement: Browser and design MCP servers SHALL remain direct Codex utility servers

Codex SHALL use browser and design MCP capabilities through direct Codex MCP entries instead of the Codex-side `mcp_router` bridge.

Codex direct utility MCP servers include `chrome-devtools` and `pencil`.

#### Scenario: Codex browser and design tools are configured

- **WHEN** local Codex configuration is audited
- **THEN** `chrome-devtools` and `pencil` SHALL be enabled as direct Codex MCP servers
- **AND** Codex SHALL NOT require MCP Router to access those capabilities

### Requirement: Codex SHALL keep the MCP Router bridge disabled by default

The Codex-side `mcp_router` bridge SHALL be disabled or absent by default.

#### Scenario: Codex MCP Router bridge is enabled

- **WHEN** the Codex `mcp_router` bridge is enabled
- **THEN** the checker SHALL fail
- **AND** the operator SHALL be directed to use direct Codex MCP entries instead
