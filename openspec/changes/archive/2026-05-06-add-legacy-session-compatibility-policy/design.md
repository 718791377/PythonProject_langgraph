# Design: Legacy session compatibility policy

## Decision

Keep old `/resume` threads usable while assigning them a lower authority level than current repository state.

## Script Backing

The rule is backed by existing repository checkers:

- `tools/check_mcp_router_scope_policy.py` validates direct Codex MCP scope.
- `tools/check_windows_cleanup_output_control.py` validates wrapped-launch cleanup control without disabling `omx_*` servers.
- `tools/check_session_ownership_claims.py` validates current-session ownership before writable governance work.

## Rollback

The change is documentation and registry-only. Reverting the commit removes the compatibility rule without touching user-level Codex configuration.
