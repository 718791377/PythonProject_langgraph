## Tasks

- [x] 1. Create bilingual OpenSpec artifacts for `codex-direct-browser-design-mcp-policy` - this change defines the direct Codex MCP boundary.
- [x] 2. Update `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` and `.zh-CN.md` - document that Codex uses `chrome-devtools` and `pencil` directly and keeps `mcp_router` disabled.
- [x] 3. Update `openspec/specs/codex-user-level-mcp-scope-policy/spec.md` and `.zh-CN.md` - align stable requirements with the direct Codex MCP rule.
- [x] 4. Update `tools/check_mcp_router_scope_policy.py` and `tools/mcp_router_scope_policy_exceptions.json` - enforce direct Codex MCP entries and mark the old disabled-bridge exception resolved.
- [x] 5. Run validation commands - `python tools/check_mcp_router_scope_policy.py --root . --json`, `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, and `git diff --check`.
- [ ] 6. Publish by GitLab-first workflow - push the feature branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
