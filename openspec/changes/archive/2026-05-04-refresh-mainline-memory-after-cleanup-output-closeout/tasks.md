## Tasks

- [x] 1. Create OpenSpec artifacts for `refresh-mainline-memory-after-cleanup-output-closeout`.
- [x] 2. Update the English mainline memory summary with the latest MR 6 readiness, cleanup-output closeout, and local archive-worktree cleanup state.
- [x] 3. Update the Chinese mainline memory summary with the same state through an explicit UTF-8 write path.
- [x] 4. Repair the corrupted Chinese stable-spec companion for `codex-user-level-mainline-memory-handoff`.
- [x] 5. Run validation commands: `git diff --check`, `openspec validate --all`, `python tools/check_document_governance_rules.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, `python tools/check_name_clarity_rules.py --root . --json`, and `python tools/run_openspec_guard.py --root . --tool codex --json`.
- [x] 6. Publish through GitLab-first workflow: push branch to GitLab, open/merge GitLab MR after pipeline success, then sync GitHub main.
