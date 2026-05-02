## Tasks

- [x] 1. Confirm MR 3 and MR 4 are already complete in the current implementation plan.
- [x] 2. Confirm MR 5 helper mirror source-of-truth is already implemented, validated, and archived.
- [x] 3. Create bilingual OpenSpec artifacts for `sync-durable-rollout-plan-status` - this change prevents stale rollout queue wording.
- [x] 4. Update the bilingual cross-session durable-state isolation plan - mark MR 5 complete and reframe MR 6 as the next decision point.
- [x] 5. Update the stable plan-status-sync spec - require completed durable-state rollout slices not to remain labeled as next active slices.
- [x] 6. Run validation commands - `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, `python tools/check_name_clarity_rules.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, and `git diff --check`.
- [x] 7. Publish through GitLab-first workflow - push the branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
