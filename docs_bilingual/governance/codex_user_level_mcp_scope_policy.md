---
doc_id: codex_user_level_mcp_scope_policy
lang: en
doc_class: governance
status: active
---

# Codex User-Level MCP Scope Policy

## 1. Purpose

This policy defines which MCP servers are Codex-dedicated and which MCP servers may be managed through MCP Router for cross-client use.

`MCP` means Model Context Protocol, the tool-server protocol used by Codex and other clients.

`MCP Router` is the shared router application that can expose selected MCP servers to multiple clients such as Codex, Trae, VS Code, and PyCharm.

`Codex` is the OpenAI coding agent client used as the leader for this repository's orchestration workflow.

## 2. Authority Boundary

Use this boundary rule:

```text
Codex orchestration truth stays Codex-dedicated.
Cross-client utility tools may go through MCP Router.
```

Codex-dedicated MCP servers MUST remain configured directly for Codex and MUST NOT be managed as shared MCP Router servers.

MCP Router SHOULD manage only cross-client utility MCP servers that do not own Codex session state, durable orchestration state, repository-local truth, or approval-sensitive write authority.

## 3. Codex-Dedicated MCP Servers

`omx_state` is the oh-my-codex state MCP server used to read and write Codex mode state.

`omx_memory` is the oh-my-codex memory MCP server used to read and write Codex project memory and notepad data.

`omx_code_intel` is the oh-my-codex code intelligence MCP server used by Codex for repository diagnostics and code search.

`omx_trace` is the oh-my-codex trace MCP server used to inspect Codex agent-flow trace data.

These Codex-dedicated MCP servers MUST be enabled in Codex user-level configuration when the oh-my-codex layer is enabled.

These Codex-dedicated MCP servers MUST NOT be exposed through MCP Router as shared server entries for other clients.

## 4. MCP Router Shared Utility Servers

`chrome-devtools` is the browser debugging MCP server used for browser pages, DOM snapshots, screenshots, console data, and network inspection.

`pencil` is the design MCP server used for Pencil design documents, visual variables, node reads, and exports.

These shared utility MCP servers MAY be managed by MCP Router when multiple clients need the same browser or design capability.

When `chrome-devtools` or `pencil` is managed by MCP Router, the corresponding direct Codex server entry SHOULD be disabled or absent in `C:\Users\lenovo\.codex\config.toml`.

`C:\Users\lenovo\.codex\config.toml` is the user-level Codex configuration file that controls direct MCP server entries for Codex on this Windows machine.

## 5. Router Self-Reference Rule

`mcp_router` is the Codex-side MCP server entry that lets Codex connect to MCP Router.

`mcp-router` is the MCP Router application or package name and MUST NOT be registered as a server managed by MCP Router itself.

MCP Router MUST NOT manage a server entry that points back to MCP Router, because that creates self-reference and can cause recursive routing, duplicate startup, or confusing tool exposure.

## 6. High-Risk Shared Server Rules

`windows-cli` is a Windows shell MCP server and MUST NOT be exposed broadly through MCP Router without explicit operator approval and strong approval gates.

SSH management MCP servers are tools that can create, update, or delete SSH connection records and SHOULD NOT be exposed to Codex by default unless the task requires them.

Deployment MCP servers are tools that can publish or mutate remote infrastructure and SHOULD be read-only or approval-gated when shared through MCP Router.

## 7. Required Checker Behavior

`tools/check_mcp_router_scope_policy.py` is the repository checker that validates the Codex MCP scope split and reports MCP Router drift.

The checker MUST verify, when local user-level files are present, that Codex keeps `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` enabled directly.

The checker MUST verify, when local user-level files are present, that direct Codex entries for `chrome-devtools` and `pencil` are disabled or absent when MCP Router is enabled.

The checker MUST report MCP Router server records for `omx_state`, `omx_memory`, `omx_code_intel`, `omx_trace`, or `mcp-router` as drift.

The default guard path MAY report MCP Router database drift as warnings because MCP Router is external user-level application state. A strict local run MAY fail on that drift when the operator wants to audit the live machine.

## 8. Validation Commands

Run these commands after changing this policy or the checker:

```powershell
python tools/check_mcp_router_scope_policy.py --root . --json
python tools/run_openspec_guard.py --root . --json
git diff --check
```

`python tools/check_mcp_router_scope_policy.py --root . --json` runs the MCP scope checker and emits machine-readable JSON.

`python tools/run_openspec_guard.py --root . --json` runs the aggregate repository guard for OpenSpec and governance checks.

`git diff --check` checks whitespace safety before committing.
