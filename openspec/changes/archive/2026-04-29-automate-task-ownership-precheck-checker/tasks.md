## 1. OpenSpec artifacts

- [x] 1.1 Create proposal, design, tasks, and delta spec for task ownership precheck automation.

## 2. Checker implementation

- [x] 2.1 Add optional task ownership precheck inputs to `tools/check_session_ownership_claims.py`.
- [x] 2.2 Detect semantic signals from worktrees, branches, remote branches, OpenSpec changes, active claims, and ignored/local-only guard-scanned files.
- [x] 2.3 Add optional GitLab MR inspection with fail-closed behavior when explicitly required.

## 3. Tests and governance

- [x] 3.1 Add tests for clean-branch claimed-not-started classification, active-claim in-progress classification, ignored-file signals, and required GitLab MR failure.
- [x] 3.2 Update bilingual governance policy wording from manual-only precheck to checker-backed precheck.

## 4. Verification

- [x] 4.1 Run targeted unit tests for the checker.
- [x] 4.2 Run OpenSpec validation and repository guard.
