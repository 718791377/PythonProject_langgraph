---
doc_id: codex_user_level_mcp_scope_policy
lang: en
doc_class: governance
status: active
---

# Codex User-Level MCP Scope Policy

## 1. Purpose

This policy defines which MCP servers Codex uses directly and which MCP servers may remain in MCP Router for non-Codex clients.

`MCP` means Model Context Protocol, the tool-server protocol used by Codex and other clients.

`MCP Router` is the shared router application that may expose selected MCP servers to Trae, VS Code, PyCharm, or other non-Codex clients.

`Codex` is the OpenAI coding agent client used as the leader for this repository's orchestration workflow.

## 2. Authority Boundary

Use this boundary rule:

```text
Codex direct tools stay direct.
MCP Router stays disabled for Codex by default.
```

This means Codex must not use the `mcp_router` bridge as its default path to browser, design, or orchestration tools.

`mcp_router` is the Codex-side MCP server entry that would let Codex connect to MCP Router.

MCP Router may still serve non-Codex clients. Its server list does not define Codex capability unless Codex explicitly enables the `mcp_router` bridge, which this policy forbids by default.

## 3. Codex-Private Direct MCP Servers

`omx_state` is the oh-my-codex state MCP server used to read and write Codex mode state.

`omx_memory` is the oh-my-codex memory MCP server used to read and write Codex project memory and notepad data.

`omx_code_intel` is the oh-my-codex code intelligence MCP server used by Codex for repository diagnostics and code search.

`omx_trace` is the oh-my-codex trace MCP server used to inspect Codex agent-flow trace data.

These Codex-private MCP servers must be enabled directly in Codex user-level configuration when the oh-my-codex layer is enabled.

These Codex-private MCP servers must not be exposed through MCP Router as shared server entries for other clients.

## 4. Codex Direct Utility MCP Servers

`chrome-devtools` is the browser debugging MCP server used for browser pages, DOM snapshots, screenshots, console data, and network inspection.

`pencil` is the design MCP server used for Pencil design documents, visual variables, node reads, and exports.

Codex must use `chrome-devtools` and `pencil` through direct Codex MCP entries, not through the `mcp_router` bridge.

`C:\Users\lenovo\.codex\config.toml` is the user-level Codex configuration file that controls direct MCP server entries for Codex on this Windows machine.

Direct Codex entries for `chrome-devtools` and `pencil` should remain enabled when the operator wants Codex browser or design capability.

If MCP Router also contains `chrome-devtools` or `pencil` for Trae, VS Code, PyCharm, or another non-Codex client, that Router state is external client state and does not count as Codex access.

## 5. MCP Router Bridge Rule for Codex

The Codex-side `mcp_router` bridge must remain disabled or absent by default.

Codex must not load MCP Router's full tool catalog during normal startup, because MCP Router may aggregate large cross-client tool lists that increase startup cost, tool-choice noise, and `/resume` risk.

`tools/list` is the MCP method that returns the tool names, descriptions, and input schemas for an MCP server. A large `tools/list` payload can consume startup budget even when each tool is valid.

Re-enabling the Codex-side `mcp_router` bridge requires a future approved governance change that defines a bounded Codex-specific Router profile and validates `tools/list` size, resume startup, and direct-MCP fallback behavior.

## 6. Router Self-Reference Rule

`mcp-router` is the MCP Router application or package name and must not be registered as a server managed by MCP Router itself.

MCP Router must not manage a server entry that points back to MCP Router, because that creates self-reference and can cause recursive routing, duplicate startup, or confusing tool exposure.

## 7. High-Risk Shared Server Rules

`windows-cli` is a Windows shell MCP server and must not be exposed to Codex through MCP Router.

SSH management MCP servers are tools that can create, update, or delete SSH connection records and must not be exposed to Codex through MCP Router by default.

Deployment MCP servers are tools that can publish or mutate remote infrastructure and must not be exposed to Codex through MCP Router without task-specific approval gates.

These tools may exist in MCP Router for other clients only when the operator accepts that external client risk.

## 8. Required Checker Behavior

`tools/check_mcp_router_scope_policy.py` is the repository checker that validates the Codex MCP scope split and reports MCP Router drift.

The checker must verify, when local user-level files are present, that Codex keeps `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `chrome-devtools`, and `pencil` enabled directly.

The checker must verify that the Codex-side `mcp_router` bridge is disabled or absent by default.

The checker must report MCP Router server records for `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `mcp-router`, or `mcp_router` as drift.

The checker does not need to fail only because MCP Router contains `chrome-devtools` or `pencil` for non-Codex clients; Codex access is controlled by direct Codex entries and the disabled `mcp_router` bridge.

The default guard path may report MCP Router database drift as warnings because MCP Router is external user-level application state. A strict local run may fail on that drift when the operator wants to audit the live machine.

## 9. Historical Bridge Exception

`tools/mcp_router_scope_policy_exceptions.json` is the repository-owned MCP scope exception registry used by the checker.

The earlier `mcp-router-disabled-for-resume-stability` exception recorded that `/resume` was unstable when the Codex-side `mcp_router` bridge was enabled.

That exception is now resolved because this policy makes the disabled bridge the default Codex rule.

The exception must not be reactivated unless a future approved governance change explicitly reverses the default and supplies bounded Router-profile validation.


## 10. Legacy Resume Compatibility

Existing Codex `/resume` threads may continue during a compatibility period, but they remain compatibility-scoped.

A legacy resumed session is an older Codex thread that may carry stale runtime overrides, stale MCP assumptions, or old launcher behavior from before the current MCP scope policy.

Rules:

- Use current repository policy and current local Git state as truth; do not let a legacy resumed session redefine MCP ownership or publication safety.
- If a specific legacy resumed session fails because one direct MCP server has stale startup state, use a per-invocation override for that session only. For example, `-c "mcp_servers.omx_code_intel.enabled=false"` is a one-launch Codex config override that disables only `omx_code_intel` for that old thread.
- Do not permanently remove or globally disable `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, `chrome-devtools`, or `pencil` to work around one legacy resumed session.
- Do not edit `C:\Users\lenovo\.codex\config.toml` only because one old thread fails. That path is the user-level Codex configuration file and remains operator-controlled.
- New sessions and normal wrapped launches must continue to follow this direct-MCP policy.

Script backing:

- `tools/check_mcp_router_scope_policy.py` is the checker that confirms Codex-private MCP servers remain direct and that the Codex-side `mcp_router` bridge remains disabled or absent by default.
- `tools/check_windows_cleanup_output_control.py` is the checker that confirms wrapped launch cleanup output control does not require disabling direct `omx_*` MCP servers.

## 11. Validation Commands

Run these commands after changing this policy or the checker:

```powershell
python tools/check_mcp_router_scope_policy.py --root . --json
python tools/run_openspec_guard.py --root . --json
git diff --check
```

`python tools/check_mcp_router_scope_policy.py --root . --json` runs the MCP scope checker and emits machine-readable JSON.

`python tools/run_openspec_guard.py --root . --json` runs the aggregate repository guard for OpenSpec and governance checks.

`git diff --check` checks whitespace safety before committing.
