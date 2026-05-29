# Receipt redaction guard implementation plan

- [x] Add `tools/user_level_receipt_governance.py` with `auth-check`, `update-check`, `redact-check`, and `template`.
- [x] Add unit tests for required fields, future expiry, smoke/rollback evidence, path hashing, and sensitive payload detection.
- [x] Register the test in `tools/ci/ci_test_manifest.json`.
- [x] Update the bilingual implementation plan and stable OpenSpec spec.
- [x] Verify with focused tests, baseline checker, OpenSpec guard, local gate, and local MR review.

