## Tasks

- [x] Create the `chrome-devtools-mcp` managed wrapper OpenSpec proposal, design, delta spec, and implementation tasks.
- [x] Implement `tools/chrome_devtools_mcp_managed.py` with isolated-session plan/reserve/start/release/status commands.
- [x] Delegate lease writes and releases to `tools/browser_owner_registry.py`.
- [x] Keep plan, lease, and receipt output sanitized with profile-path and receipt-path hashes.
- [x] Fail closed for live start without a pinned install receipt and defer live start even when an install receipt is supplied.
- [x] Add `test/chrome_devtools_mcp_managed.test.py` for dry-run planning, reserve receipts, fail-closed live start, and release delegation.
- [x] Register `chrome_devtools_mcp_managed.test.py` in `tools/ci/ci_test_manifest.json`.
- [x] Update bilingual implementation-plan checklist state for the completed repo-local isolated-session wrapper MVP item.
- [x] Run local validation and archive this completed OpenSpec change before local `main` integration.
