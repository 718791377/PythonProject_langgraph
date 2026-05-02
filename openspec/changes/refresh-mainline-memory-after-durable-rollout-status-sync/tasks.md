## Tasks

- [x] 1. Create OpenSpec artifacts for `refresh-mainline-memory-after-durable-rollout-status-sync`.
- [x] 2. Update the English mainline memory summary with the latest landed durable rollout status-sync and MCP policy state.
- [x] 3. Update the Chinese mainline memory summary with the same state through an explicit UTF-8 write path.
- [x] 4. Run validation commands: `git diff --check`, `openspec validate --all`, `python tools/check_document_governance_rules.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, and `python tools/run_openspec_guard.py --root . --json`.
- [ ] 5. Publish through GitLab-first workflow: push branch to GitLab, open/merge GitLab MR after pipeline success, then sync GitHub main.
- [x] 6. Defer archive until no active session owns broad `openspec/specs` scope; record that follow-up clearly.
