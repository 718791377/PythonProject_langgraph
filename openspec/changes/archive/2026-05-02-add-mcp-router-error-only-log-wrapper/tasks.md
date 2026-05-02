## Tasks

- [x] 1. Create bilingual OpenSpec artifacts for `add-mcp-router-error-only-log-wrapper` - this change defines the opt-in MCP Router log filtering behavior.
- [x] 2. Add `tools/mcp-router-log-filter-wrapper.ps1` and `tools/mcp_router_log_filter_wrapper.py` - launcher plus Python core that preserve protocol stdout, write full logs to a file, and forward only actionable errors.
- [x] 3. Add `test/mcp_router_log_filter_wrapper.test.ps1` - PowerShell tests for benign suppression, protocol preservation, error forwarding, log retention, and non-zero exit propagation.
- [x] 4. Run validation commands - wrapper tests, `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, and `git diff --check`.
- [x] 5. Publish by GitLab-first workflow - push the feature branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
