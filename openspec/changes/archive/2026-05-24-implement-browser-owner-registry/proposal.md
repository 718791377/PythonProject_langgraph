## Why

The governance plan requires a browser owner registry before `chrome-devtools-mcp`, CDP Bridge, and OpenCLI can become safe multi-project browser automation surfaces. This slice adds the repository-local ownership registry and fail-closed authorization behavior without launching browsers, connecting to CDP, installing user-level wrappers, or touching human-owned Chrome assets.

## What Changes

- Add `tools/browser_owner_registry.py` with compact JSON commands for browser automation ownership leases.
- Support isolated managed leases, project-profile authorization gates, target exclusivity, renew/release, stale scan dry-run, and cleanup dry-run.
- Redact raw private profile paths from output while retaining deterministic profile-path hashes.
- Ensure `human-owned` assets are never treated as Codex-managed cleanup targets.
- Add unit tests for isolated round-trip, project-profile authorization/exclusivity, human-owned protection, target exclusivity, and cleanup dry-run.
- Register the new unit test in the shared CI test manifest and update bilingual plan state.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `codex-user-level-mcp-skills-browser-cli-governance`: add executable repo-local browser owner registry MVP behavior for browser automation ownership and cleanup safety.

## Impact

- Affected source: `tools/browser_owner_registry.py`.
- Affected tests: `test/browser_owner_registry.test.py`, `tools/ci/ci_test_manifest.json`.
- Affected governance docs: bilingual implementation plan and OpenSpec delta/stable spec surfaces.
- No user-level files under `C:\Users\lenovo\.codex` are modified by this slice; managed Chrome wrapper installation remains a later governed slice.

## Mainline classification

Existing mainline: user-level MCP, skills, browser automation, and CLI harness governance.

## Explicit non-goals

- Do not install or replace user-level `chrome-devtools-mcp` wrappers.
- Do not launch Chrome, connect to CDP, click/type/navigate, read cookies, or inspect user-owned browser data.
- Do not delete profile directories; cleanup is dry-run only in this repo-local MVP.
- Do not implement CDP Bridge/OpenCLI enforcement, `oh-my-pi`, CLI-Anything, or `wecom-cli` in this slice.

## Rollout sequence

1. Add OpenSpec artifacts for the browser owner registry MVP slice.
2. Implement the repo-local registry helper.
3. Add tests and register them in local CI.
4. Run pre-commit update/archive gate, OpenSpec guard, unit tests, local gate, and local MR review.
5. Archive the completed OpenSpec change as one local integration package before merging to local `main`.

## Rollback plan

Revert the local commit or reset local `main` to the rollback ref created before merge. Since no user-level files are written, rollback is repository-only.

## Validation path

- `python test/browser_owner_registry.test.py` - runs the focused browser owner registry unit tests.
- `python tools/browser_owner_registry.py lease reserve --owner-class codex-managed-isolated --project pythonproject-langgraph --session session-a --target tab:debug --profile-path <path> --purpose test --ttl 300 --json` - verifies isolated managed lease creation.
- `python tools/browser_owner_registry.py cleanup dry-run --json` - verifies cleanup remains dry-run and protected by owner class.
- `python tools/check_precommit_update_archive.py --root . --json` - verifies the pre-commit update/archive gate.
- `python tools/run_openspec_guard.py --root . --json` - verifies OpenSpec guard health.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 300` - runs the shared local CI gate.
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -BaseRef main -HeadRef HEAD` - runs the local MR review gate.
