## Tasks

- [x] 1. Create bilingual OpenSpec artifacts for `refresh-mainline-memory-after-mcp-scope-policy` - this change directory documents why the handoff refresh is needed and how it will be validated.
- [x] 2. Update `AGENTS.md` - the repository instruction surface so future MCP Router scope questions route to the stable MCP policy document.
- [x] 3. Update `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md` - the startup summary pair so cold-start read order includes the MCP scope policy and handles the no-active-change state clearly.
- [x] 4. Update the current mainline memory summary pair - the drift-prone handoff files under `docs_bilingual/memory/` so they identify the latest landed MCP and memory-handoff increments before listing next actions.
- [x] 5. Run validation commands - `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, `python tools/check_name_clarity_rules.py --root . --json`, and `git diff --check`.
- [ ] 6. Publish by GitLab-first workflow - push the feature branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
