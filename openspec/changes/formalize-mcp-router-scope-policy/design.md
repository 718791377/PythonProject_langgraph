## Context

MCP Router is external user-level application state. The repository can define policy and provide checkers, but a repository MR must not directly mutate the user's MCP Router database or UI configuration.

The checker therefore has two layers:

1. Codex configuration checks are blocking when `C:\Users\lenovo\.codex\config.toml` or an explicit `--codex-config` file is present.
2. MCP Router database checks report drift by default and can be made blocking with `--strict-router-state` for local machine audits.

## Decisions

### Decision: Keep Codex-dedicated MCP direct

`omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` remain direct Codex MCP servers because they read or write Codex orchestration state, project memory, code-intel context, or trace data.

### Decision: Keep shared browser/design MCP in Router

`chrome-devtools` and `pencil` are cross-client utility MCP servers. They may be managed by MCP Router and should not also be enabled as direct Codex entries in the same user-level profile.

### Decision: Router self-reference is drift

`mcp-router` or equivalent Router self-reference entries must not appear as MCP Router managed servers. Codex may keep the `mcp_router` entry only as the client-side bridge to MCP Router.

### Decision: CI-safe checker behavior

The checker must pass in CI when user-level Codex configuration or MCP Router state is absent. Missing user-level runtime files are reported as informational skips, not repository failures.

## Risks

- MCP Router database fields may change across app versions. The checker treats unreadable or unknown router state as warnings unless strict mode is requested.
- A disabled server can remain in MCP Router history. The checker distinguishes active drift from disabled residue when the database exposes a `disabled` field.
- The current launcher may still pass command-line overrides for Codex-dedicated MCP servers. That is acceptable because the policy keeps those servers direct.
