## Design

`tools/mcp_router_scope_policy_exceptions.json` is a repository-owned exception registry. It is intentionally small and explicit so a cold-start session can understand why the live user-level Codex configuration differs from the normal policy.

The registry contains an active exception with:

- `id` - the stable exception identifier.
- `scope` - the exact exception scope, currently `codex_mcp_router_bridge_disabled`.
- `reason` - the operational reason for the exception.
- `recovery_condition` - the condition that must be met before the exception is removed.

`tools/check_mcp_router_scope_policy.py` loads the registry through `--exceptions-path`; this option points to the JSON exception registry and defaults to `tools/mcp_router_scope_policy_exceptions.json`.

When the Codex `mcp_router` bridge is disabled:

- without an active exception, the checker fails;
- with the active resume-stability exception, the checker emits a warning and stays green;
- `omx_*` direct MCP server failures remain blocking errors;
- MCP Router forbidden records and self-reference checks remain unchanged.

This keeps the current `/resume` hotfix visible, reversible, and script-backed without mutating MCP Router state.
