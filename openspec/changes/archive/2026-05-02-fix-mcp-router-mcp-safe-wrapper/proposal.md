## Why

The current MCP Router wrapper classifies stdout line by line. MCP stdio transports may use JSON-RPC lines, `Content-Length` frames, large `tools/list` payloads, or no-newline writes. Rewriting stdout at line boundaries can break protocol framing and may contribute to Codex startup or `/resume` instability.

## What Changes

- Make wrapper stdout byte-transparent: every byte from child stdout is forwarded to wrapper stdout unchanged.
- Continue writing full raw stdout/stderr data to local logs for diagnostics.
- Filter only stderr for visible benign noise, and forward actionable stderr errors.
- Add tests for JSON-RPC without a trailing newline, `Content-Length` framed output, large `tools/list`-like payloads, benign stderr suppression, and non-zero exits.
- Keep the wrapper opt-in and do not re-enable Codex `mcp_router` in user-level config.

## Non-goals

- Do not modify `C:\Users\lenovo\.codex\config.toml`; this file is the user-level Codex configuration file.
- Do not mutate MCP Router database or token storage.
- Do not remove the current resume-stability exception.
- Do not claim the wrapper is ready for default Codex startup until operator testing confirms `/resume` remains visible.
