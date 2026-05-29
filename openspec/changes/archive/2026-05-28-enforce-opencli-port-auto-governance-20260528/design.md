# Design: OpenCLI port-auto governance

## Boundary

This change is repo-local only. It models OpenCLI pre-dispatch governance without installing OpenCLI, opening browsers, binding ports, or changing user-level configuration.

## Approach

`opencli_governance.py` evaluates three independent gates before dispatch is allowed:

1. adapter gate: OpenCLI remains `on-demand`;
2. port gate: the requested port mode must be `auto`, and a sanitized `codex-port` lease receipt must prove a Codex-owned lease in `39300-39499`;
3. target/action gate: browser owner lease is required for target-bound actions, and authorization receipt is required for sensitive actions.

The port gate intentionally accepts fixture receipts in tests instead of invoking `codex-port`, because this guard must remain deterministic and non-mutating.

## Acceptance evidence

- `python test/cdp_bridge_governance.test.py` - validates the CDP Bridge and OpenCLI governance unit path.
- `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json` - validates the user-level MCP/skills/browser/CLI governance baseline.
- `python tools/run_openspec_guard.py --root . --json` - validates OpenSpec and repository governance guard coverage.
- local gate and local MR review before integration.
