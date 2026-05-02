## Why

Codex should not consume MCP Router's aggregate tool catalog by default. Recent MCP Router diagnostics showed a large `tools/list` payload, which increases Codex startup cost, tool-choice noise, and `/resume` risk.

Browser and design capability should still be available to Codex, but through direct Codex MCP entries for `chrome-devtools` and `pencil` rather than through the Codex-side `mcp_router` bridge.

## What Changes

- Make the disabled Codex-side `mcp_router` bridge the default policy instead of a temporary exception.
- Classify `chrome-devtools` and `pencil` as Codex direct utility MCP servers.
- Keep `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` as Codex-private direct MCP servers.
- Update the MCP scope checker to require direct Codex entries for browser and design tools and to fail if the Codex `mcp_router` bridge is enabled.
- Mark the previous resume-stability bridge-disabled exception as resolved.

## Non-goals

- Do not modify `C:\Users\lenovo\.codex\config.toml`; this file is the user-level Codex configuration file.
- Do not delete or mutate MCP Router database state.
- Do not prevent MCP Router from serving non-Codex clients such as Trae, VS Code, or PyCharm.
