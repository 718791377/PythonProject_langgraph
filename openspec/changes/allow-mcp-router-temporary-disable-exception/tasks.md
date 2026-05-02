## Tasks

- [x] 1. Create bilingual OpenSpec artifacts for `allow-mcp-router-temporary-disable-exception` - this change defines the resume-stability exception for the Codex `mcp_router` bridge.
- [x] 2. Add `tools/mcp_router_scope_policy_exceptions.json` - this registry records the active temporary exception and its recovery condition.
- [x] 3. Update `tools/check_mcp_router_scope_policy.py` - this checker now allows only the declared `mcp_router` disabled exception while preserving blocking errors for `omx_*` direct MCP servers.
- [x] 4. Update `test/check_mcp_router_scope_policy.test.py` - these tests cover disabled bridge behavior with and without the exception.
- [x] 5. Update MCP scope governance docs - these docs explain why MCP Router can remain available to other clients while Codex temporarily disables its bridge.
- [x] 6. Run validation commands - checker tests, strict local MCP scope check, `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, and `git diff --check`.
- [ ] 7. Publish by GitLab-first workflow - push the feature branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
