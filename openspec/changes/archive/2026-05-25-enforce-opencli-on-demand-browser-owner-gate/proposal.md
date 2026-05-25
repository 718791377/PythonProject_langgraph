# Proposal: enforce OpenCLI on-demand browser owner gate

## Summary

Add a repo-local OpenCLI governance guard that keeps OpenCLI on-demand, requires browser owner registry evidence for target-bound actions, and fails closed for cookie, JavaScript, click, type, navigate, and unknown actions without one-task authorization.

## Scope

- Add `tools/opencli_governance.py`.
- Add `test/opencli_governance.test.py`.
- Register the test in `tools/ci/ci_test_manifest.json`.
- Promote the OpenCLI on-demand guard contract into the stable governance spec.
- Update the implementation-plan checklist for this slice.

## Non-goals

- Do not install OpenCLI.
- Do not start OpenCLI.
- Do not launch Chrome or connect to a browser.
- Do not bind to human-owned Chrome tabs.
- Do not write user-level Codex configuration.
- Do not implement `oh-my-pi`, CLI-Anything, or `wecom-cli`.

## Rollback

Revert the local commit for this slice or reset local `main` to the rollback ref captured during local integration.
