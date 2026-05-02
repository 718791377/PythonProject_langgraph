## Overview

The wrapper is an opt-in repository-local process wrapper for the MCP Router bridge command. It is designed to reduce conversation pollution without mutating user-level configuration or losing diagnostic evidence.

## Design

`tools/mcp-router-log-filter-wrapper.ps1` is a thin PowerShell launcher. It calls `tools/mcp_router_log_filter_wrapper.py`, the Python filtering core that starts a child command, captures its stdout and stderr, and classifies each line:

- Protocol-like stdout is forwarded to stdout unchanged. A protocol-like line is a JSON object with JSON-RPC fields, a `Content-Length` or `Content-Type` header, or a blank framing line.
- Known benign non-protocol noise is written only to a timestamped log file.
- Unknown non-protocol informational output is written only to the log file.
- Actionable error output is written to the log file and forwarded to stderr.
- Non-zero child exit code is reported to stderr with the log path.

Default benign filters include:

- `checking-for-update` - MCP Router updater check noise.
- `update-not-available` - MCP Router updater result noise.
- `No valid workflows found for` - MCP Router workflow fallback noise.
- `Executing handler directly without workflow` - MCP Router fallback execution noise.
- `libpng warning: iCCP` - Electron or PNG color-profile warning noise.
- `SUCCESS: The process with PID ... has been terminated.` - Windows process-tree cleanup noise from lifecycle management.

Default error filters include:

- `ERROR` - generic high-severity marker that usually means the child command encountered a failure.
- `FAILED` - generic failure marker that usually means an operation did not complete successfully.
- `Exception` - runtime exception marker that usually means a program raised an unexpected error.
- `Traceback` - Python stack trace marker that usually means an exception escaped normal handling.
- `Unauthorized` - authentication failure marker that usually means a credential or permission was rejected.
- `Forbidden` - authorization failure marker that usually means the caller lacks permission.
- `auth failed` - lower-case authentication failure phrase used by some command-line tools.
- `token expired` - token lifetime failure phrase that usually means credentials need refresh or rotation.

## Safety Boundaries

- The wrapper is opt-in and is not wired into `C:\Users\lenovo\.codex\config.toml` by this change.
- The wrapper never suppresses JSON-RPC-looking stdout because that stream may carry MCP protocol messages.
- The wrapper records all raw child output in a local log file for later diagnostics.
- The wrapper does not edit MCP Router database or token storage.

## Validation

The PowerShell test creates short-lived fake child commands and verifies:

- benign stdout/stderr lines are absent from wrapper-visible output
- JSON-RPC stdout is preserved
- error stderr is forwarded
- non-zero exit status is propagated and reported
- raw logs retain suppressed benign lines
