## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, tasks, and delta spec for session ownership claims.

## 2. Checker implementation

- [x] 2.1 Add `tools/check_session_ownership_claims.py` - read-only checker for local session ownership claim files.
- [x] 2.2 Add tests for missing claims, duplicate OpenSpec-change claims, and overlapping path claims.

## 3. Governance and guard integration

- [x] 3.1 Update the multi-session worktree isolation governance policy with the claim workflow.
- [x] 3.2 Register the claim rule in `tools/safety_rule_script_backing_registry.json` - the registry that requires safety rules to have prompt reminders and scripts.
- [x] 3.3 Add the checker to `tools/run_openspec_guard.py` - the aggregate OpenSpec guard script.

## 4. Verification and archive

- [x] 4.1 Run the targeted tests and repository guard.
- [x] 4.2 Mark tasks complete and archive the change so only stable specs remain active.

