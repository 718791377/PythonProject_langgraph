## Design

The wrapper becomes conservative around MCP stdio:

- Child stdout is copied as bytes from child stdout to wrapper stdout without parsing, filtering, line splitting, newline insertion, or encoding replacement.
- Child stdin is copied as bytes from wrapper stdin to child stdin.
- Child stderr remains text-classified because stderr is not the MCP protocol channel for Codex. Benign stderr noise is log-only, while actionable stderr is forwarded to wrapper stderr.
- Raw stdout and stderr chunks are written to timestamped log files under `.omx/logs/mcp-router` unless `--log-root` is supplied.

This design trades away stdout noise suppression to preserve protocol safety. Benign stdout lifecycle messages cannot be safely removed unless the wrapper implements a full MCP frame parser, so they remain protocol-visible. The primary supported noise reduction is stderr filtering.

Validation focuses on protocol integrity rather than cosmetic stdout filtering.
