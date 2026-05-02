## Why

Codex `/resume` became stable again only after the Codex-side `mcp_router` bridge was disabled. The existing MCP scope checker still treats a disabled `mcp_router` bridge as an unconditional failure, so the repository policy conflicts with the current safety hotfix.

## What Changes

- Add a declared temporary exception file for the Codex `mcp_router` bridge being disabled for resume stability.
- Update `tools/check_mcp_router_scope_policy.py` so a disabled `mcp_router` bridge remains a failure unless an active exception with a recovery condition exists.
- Keep `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` required as direct Codex MCP servers with no exception.
- Document that MCP Router may still be used by other clients while Codex keeps its bridge disabled.

## Impact

- `tools/mcp_router_scope_policy_exceptions.json` - declares the temporary resume-stability exception and recovery condition.
- `tools/check_mcp_router_scope_policy.py` - validates the exception and downgrades only this specific disabled bridge state from error to warning.
- `test/check_mcp_router_scope_policy.test.py` - covers disabled bridge behavior with and without the declared exception.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` and `.zh-CN.md` - explain the exception policy.

## Non-goals

- Do not re-enable `mcp_router` in `C:\Users\lenovo\.codex\config.toml`; that file is the user-level Codex configuration file.
- Do not modify MCP Router database or token storage.
- Do not change the direct Codex requirement for `omx_*` MCP servers.
- Do not claim the wrapper is fixed; a separate MCP-safe wrapper fix remains pending.
