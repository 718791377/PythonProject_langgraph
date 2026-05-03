## 1. Readiness Review

- [x] 1.1 Confirm the current durable-state rollout queue names MR 6 as the next decision point.
- [x] 1.2 Confirm existing automatic durable routing evidence in specs, generator source, tests, and the team-mode implementation plan.

## 2. Plan and Spec Synchronization

- [x] 2.1 Create bilingual OpenSpec artifacts for `define-mr6-automatic-durable-routing-readiness` - the readiness-review change that prevents duplicate runtime hookup work.
- [x] 2.2 Update the bilingual cross-session durable-state isolation plan - mark MR 6 readiness review complete and point future runtime exercise to a separate explicit smoke or adoption gate.
- [x] 2.3 Update the stable plan-status-sync spec - require MR 6 queues to reconcile existing automatic routing evidence before opening duplicate runtime work.

## 3. Validation and Publication

- [x] 3.1 Run validation commands - `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, `python tools/check_implementation_plan_rules.py --root . --json`, `python tools/check_name_clarity_rules.py --root . --json`, and `git diff --check`.
- [x] 3.2 Publish through GitLab-first workflow - push the branch to GitLab, open a merge request, wait for pipeline success, merge to GitLab `main`, then sync that exact `main` commit to GitHub.
