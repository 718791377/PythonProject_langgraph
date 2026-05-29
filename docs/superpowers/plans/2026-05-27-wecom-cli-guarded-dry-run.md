---
change: implement-wecom-cli-guarded-dry-run
design-doc: docs/superpowers/specs/2026-05-27-wecom-cli-guarded-dry-run-design.md
status: archived-with-local-implementation
---

# Plan: WeCom CLI Guarded Dry-Run

- [x] Add `tools/wecom_cli_governance.py`.
- [x] Add `test/wecom_cli_governance.test.py`.
- [x] Register the test in `tools/ci/ci_test_manifest.json`.
- [x] Extend the baseline checker to require the helper and test registration.
- [x] Update bilingual implementation plan and OpenSpec stable spec.
- [x] Verify with targeted tests, OpenSpec guard, local gate, and local MR review.
