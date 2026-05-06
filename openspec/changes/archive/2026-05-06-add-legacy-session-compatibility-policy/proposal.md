# Proposal: Add legacy session compatibility policy

## Summary

Document that older Codex `/resume` threads may continue temporarily, but only as compatibility-scoped sessions that cannot override current governance, direct MCP policy, or current local Git state.

## Scope

- Update startup and instruction surfaces.
- Update MCP scope policy and launcher payload policy.
- Update multi-session worktree isolation policy.
- Add stable OpenSpec requirements for legacy-session compatibility and scoped MCP workarounds.
- Register the safety rule in the script-backing registry.

## Non-Goals

- Do not globally disable direct `omx_*`, `chrome-devtools`, or `pencil` MCP servers.
- Do not edit `C:\Users\lenovo\.codex\config.toml` as part of this repository change.
- Do not make legacy resumed sessions authoritative for new governance work.
