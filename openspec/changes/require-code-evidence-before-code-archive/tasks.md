## 1. Implementation

- [x] 1.1 Add `tools/check_openspec_code_archive_evidence.py` - executable checker for code-class archive evidence.
- [x] 1.2 Add `test/check_openspec_code_archive_evidence.test.py` - regression tests for failing code-only archive and passing docs-only archive.
- [x] 1.3 Wire the checker into `tools/run_openspec_guard.py` - aggregate guard entry used by local verification and GitLab CI.
- [x] 1.4 Update `test/run_openspec_guard_json.test.py` - aggregate JSON contract test for the new guard step.
- [x] 1.5 Update `tools/safety_rule_script_backing_registry.json` - safety registry entry for script-backed enforcement.
- [x] 1.6 Update OpenSpec workflow governance docs - prompt reminder paired with script control.
- [x] 1.7 Allow declared existing `x_code_evidence_paths` - explicit metadata for archive-only closeout after implementation already landed on `main`.
- [x] 1.8 Add archive-only branch regression tests - tests that declared existing evidence passes and missing declared evidence fails.

## 2. Validation

- [x] 2.1 Run checker unit tests.
- [x] 2.2 Run `openspec validate --all`, `python tools/run_openspec_guard.py --root . --json`, implementation-plan checker, name-clarity checker, and `git diff --check`.

## 3. Publication

- [ ] 3.1 Publish through GitLab-first workflow: push branch, open MR, wait for pipeline success, merge to GitLab `main`, then sync exact GitLab `main` to GitHub.
