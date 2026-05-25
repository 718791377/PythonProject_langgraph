# Design: OpenCLI on-demand owner-registry gate

## Context

OpenCLI is useful for browser-to-CLI workflows, but it is higher-risk than compact read-only helpers because it can bind to browser sessions. The repository needs a local guard that proves on-demand behavior and browser owner registry integration before any user-level wrapper or live adapter is installed.

## Design

`tools/opencli_governance.py` provides a deterministic `check` command. It does not install OpenCLI, start OpenCLI, launch a browser, connect to any browser target, read cookies, execute JavaScript, click, type, navigate, or edit user-level configuration.

The guard:

- requires `adapter_mode=on-demand`;
- requires active browser owner lease evidence for every target-bound OpenCLI action;
- treats read-only inspection as allowed only after owner verification;
- treats cookie reads, JavaScript execution, click, type, navigate, and unknown actions as sensitive;
- requires one-task authorization receipt evidence for sensitive actions;
- sanitizes paths and secrets in output.

## Owned files

- `tools/opencli_governance.py` - implements the repo-local on-demand OpenCLI action gate.
- `test/cdp_bridge_governance.test.py` - adds OpenCLI owner evidence, authorization evidence, and fail-closed coverage to an existing registered browser-governance test file.
- `openspec/specs/codex-user-level-mcp-skills-browser-cli-governance/spec.md` - promotes the stable OpenCLI guard contract.
- `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.md` - records English implementation status.
- `docs_bilingual/implementation_plans/user_level_mcp_skills_browser_cli_governance_plan.zh-CN.md` - records Chinese implementation status.

## Receipt and port impact

This slice writes no user-level install receipt and binds no TCP port. It only reads test-local browser owner registry fixtures.
