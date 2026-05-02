## Tasks

- [x] 1. Create bilingual OpenSpec artifacts for `fix-mcp-router-mcp-safe-wrapper` - this change defines the MCP-safe wrapper correction.
- [x] 2. Update `tools/mcp_router_log_filter_wrapper.py` - make stdout and stdin byte-transparent while keeping stderr error-only filtering and full log retention.
- [x] 3. Update `test/mcp_router_log_filter_wrapper.test.ps1` - cover no-newline JSON-RPC, `Content-Length` frames, large payloads, stderr filtering, log retention, and non-zero exit propagation.
- [x] 4. Run validation commands - wrapper tests, `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, and `git diff --check`.
- [ ] 5. Publish by GitLab-first workflow - push the feature branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
