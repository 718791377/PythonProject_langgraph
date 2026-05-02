## Design

The policy now separates direct Codex capability from external MCP Router state:

- `CODEX_PRIVATE` lists oh-my-codex MCP servers that must never be routed through MCP Router.
- `CODEX_DIRECT_UTILITY` lists browser and design MCP servers that Codex should use directly.
- `mcp_router` is treated as disabled-by-policy for Codex; an enabled bridge is a checker error.
- MCP Router may still contain browser or design servers for other clients, but that state does not satisfy Codex direct capability.

The checker remains read-only. It reads Codex config and MCP Router database state only for validation and does not edit user-level files.
