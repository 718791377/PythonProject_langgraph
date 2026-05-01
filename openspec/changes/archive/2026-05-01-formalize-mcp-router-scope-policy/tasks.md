## 1. Policy artifacts

- [x] 1.1 Add the English ASCII MCP scope governance policy.
- [x] 1.2 Add the UTF-8 Chinese companion policy.
- [x] 1.3 Register the policy in `docs_bilingual/docs_registry.yaml`.

## 2. Checker and guard integration

- [x] 2.1 Add `tools/check_mcp_router_scope_policy.py` for Codex direct MCP scope and MCP Router drift checks.
- [x] 2.2 Add unit tests for passing and failing checker cases.
- [x] 2.3 Integrate the checker into `tools/run_openspec_guard.py`.
- [x] 2.4 Register the safety rule in `tools/safety_rule_script_backing_registry.json`.

## 3. Validation

- [x] 3.1 Run `python tools/check_mcp_router_scope_policy.py --root . --json`.
- [x] 3.2 Run `python test/check_mcp_router_scope_policy.test.py`.
- [x] 3.3 Run `openspec validate --all`.
- [x] 3.4 Run `python tools/run_openspec_guard.py --root . --json`.
- [x] 3.5 Run `git diff --check`.
