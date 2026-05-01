## Why

Codex now uses both direct MCP servers and MCP Router. Without a written scope rule, Codex-dedicated MCP servers can be imported into MCP Router and exposed as shared tools, which risks duplicate tool surfaces, recursive router entries, and accidental cross-client access to Codex orchestration state.

This change formalizes the split: Codex-dedicated MCP servers stay direct in Codex, while MCP Router manages only cross-client utility MCP servers.

## What Changes

- Add a bilingual MCP scope governance policy for user-level Codex and MCP Router configuration.
- Add a checker that validates the Codex direct MCP split when local user-level configuration is available.
- Report MCP Router records for Codex-dedicated servers or router self-reference as drift.
- Integrate the checker into the repository aggregate OpenSpec guard.
- Register the safety rule so the policy is backed by script control, not prompt reminders alone.

## Capabilities

### New Capabilities
- `codex-user-level-mcp-scope-policy`: defines the Codex-dedicated versus MCP Router shared MCP server boundary.

### Modified Capabilities
- `codex-user-level-safety-rule-script-backing`: adds the MCP scope policy checker as another implemented safety-rule script control.

## Impact

Impact scope:
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` - English ASCII governance policy for MCP scope.
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md` - UTF-8 Chinese companion governance policy.
- `docs_bilingual/docs_registry.yaml` - documentation registry entry for the new policy.
- `tools/check_mcp_router_scope_policy.py` - checker for Codex direct MCP scope and MCP Router drift reporting.
- `tools/run_openspec_guard.py` - aggregate guard integration for the new checker.
- `tools/safety_rule_script_backing_registry.json` - safety rule registry entry for script-backed enforcement.
- `test/check_mcp_router_scope_policy.test.py` - unit tests for the checker.
- `openspec/changes/formalize-mcp-router-scope-policy/` - OpenSpec artifacts for this change.

Explicit non-goals:
- Do not mutate `C:\Users\lenovo\.codex\config.toml` from this repository change.
- Do not edit the MCP Router database or UI state from repository code.
- Do not remove browser or design capabilities.
- Do not change durable team, LangGraph, or OpenSpec runtime behavior.
- Do not modify consumer projects.

Rollout sequence:
1. Add the bilingual governance policy and docs registry entry.
2. Add the checker and tests.
3. Integrate the checker into the aggregate guard and safety-rule registry.
4. Validate locally.
5. Publish through the GitLab-first workflow.

Rollback plan:
- Revert this branch before merge if the policy or checker behavior is wrong.
- If already merged, revert the GitLab merge commit and resync GitHub main.

Validation path:
- `python tools/check_mcp_router_scope_policy.py --root . --json` - validates the MCP scope checker output.
- `python test/check_mcp_router_scope_policy.test.py` - runs checker unit tests.
- `python tools/run_openspec_guard.py --root . --json` - runs the aggregate repository guard.
- `openspec validate --all` - validates OpenSpec artifacts.
- `git diff --check` - verifies whitespace-safe diffs.
