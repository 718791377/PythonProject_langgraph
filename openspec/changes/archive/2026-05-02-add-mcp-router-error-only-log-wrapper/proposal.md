## Why

MCP Router currently writes benign lifecycle and updater noise into Codex sessions, including update checks, workflow fallback messages, PNG profile warnings, and Windows process-cleanup lines. These lines do not contain secrets, but they pollute the main conversation context and can distract future cold-start sessions.

## What Changes

- Add a repository-local MCP Router log filter wrapper that keeps normal MCP protocol output intact while suppressing known benign non-protocol noise from the main session.
- Forward only actionable error output to the main session, while writing all raw child-process output to a timestamped log file.
- Add tests that prove protocol JSON is preserved, benign noise is suppressed, errors are forwarded, and non-zero exits are reported.
- Do not modify user-level Codex configuration or MCP Router database state in this change.

## Capabilities

### New Capabilities

- `codex-user-level-mcp-router-error-only-log-wrapper` - provides a safe, opt-in wrapper pattern for running the MCP Router bridge with error-only visible logs and full local log retention.

### Modified Capabilities

- None.

## Impact

Impact scope:

- `tools/mcp-router-log-filter-wrapper.ps1` - PowerShell launcher that exposes the wrapper entrypoint for Windows operators.
- `tools/mcp_router_log_filter_wrapper.py` - Python filtering core that shuttles stdio, preserves protocol output, and filters visible logs.
- `test/mcp_router_log_filter_wrapper.test.ps1` - local PowerShell test file for wrapper behavior.
- `openspec/changes/add-mcp-router-error-only-log-wrapper/` - OpenSpec change artifacts for this feature.

Explicit non-goals:

- Do not edit `C:\Users\lenovo\.codex\config.toml`; this file is the user-level Codex configuration and must remain operator-controlled.
- Do not edit MCP Router database, token storage, or UI state.
- Do not hide MCP JSON-RPC protocol messages.
- Do not suppress actionable errors, authentication failures, exceptions, or non-zero process exits.
- Do not enable this wrapper automatically in the current Codex session.

Rollout sequence:

1. Add OpenSpec artifacts and the wrapper implementation.
2. Add tests that exercise benign noise, protocol forwarding, error forwarding, and non-zero exits.
3. Run local validation.
4. Publish through GitLab-first MR flow.
5. Only after review, the operator may manually decide whether to point the Codex `mcp_router` entry at the wrapper.

Rollback plan:

- Revert the repository commit to remove the wrapper and tests.
- No user-level runtime rollback is needed because this change does not alter user-level config.

Validation path:

- `powershell -NoProfile -ExecutionPolicy Bypass -File test/mcp_router_log_filter_wrapper.test.ps1` - runs wrapper behavior tests.
- `openspec validate --all` - validates OpenSpec artifacts.
- `python tools/run_openspec_guard.py --root . --json` - runs repository guard checks.
- `git diff --check` - checks patch formatting.

Mainline classification:

- Existing mainline-adjacent maintenance: MCP Router scope and operator-surface hygiene for the current Codex user-level orchestration repository.
